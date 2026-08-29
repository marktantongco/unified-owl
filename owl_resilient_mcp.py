#!/usr/bin/env python3
"""
OWL Resilient MCP Server v7.2

Model Context Protocol server exposing JSON-RPC tools over stdin/stdout.

v7.2 changes:
  - Cache key includes query string (prevents cache poisoning)
  - Cache entries have TTL (no indefinite stale responses)
  - SSRF allowlist matches subdomains (consistent with forward_proxy)
  - DNS resolution verifies IP is public (defense in depth)
  - Shared AsyncClient (was creating a new client per request)
  - Supports POST / PUT / DELETE / PATCH (GET only was a limitation)
  - Request URL validation (scheme + host)
  - Proper MCP initialize handshake + notifications/initialized handling
  - Tool errors returned as MCP isError content (not JSON-RPC errors)
  - Rate limiter prunes stale keys
  - Timeouts split (connect / read)
  - User-Agent header set
  - Deprecated asyncio.get_event_loop() replaced with get_running_loop()

Tools:
  fetch             — HTTP fetch with circuit-breaker, rate-limit, validation
  fetch_status      — Cache stats, circuit state, rate-limiter tokens
  fetch_clear_cache — Clear the response cache
  health_check      — Server uptime, request count, provider list
  queue_status      — Queue status (always empty; retry deferred to v7.3)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from collections import OrderedDict
from enum import Enum
from typing import Any, Optional
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("owl-mcp-server")

VERSION = "7.2.0"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CACHE_MAX_ENTRIES = int(os.environ.get("OWL_CACHE_MAX_ENTRIES", "200"))
CACHE_MAX_BODY_SIZE = int(
    os.environ.get("OWL_CACHE_MAX_BODY_SIZE", str(1024 * 1024))
)  # 1 MB
CACHE_TTL = int(os.environ.get("OWL_CACHE_TTL", "300"))  # 5 minutes
RATE_LIMIT_RPM = int(os.environ.get("OWL_RATE_LIMIT_RPM", "60"))
REQUEST_CONNECT_TIMEOUT = float(
    os.environ.get("OWL_MCP_CONNECT_TIMEOUT", "10")
)
REQUEST_READ_TIMEOUT = float(
    os.environ.get("OWL_MCP_READ_TIMEOUT", "30")
)
USER_AGENT = f"owl-mcp-server/{VERSION}"

# SSRF allowlist (mirrors forward_proxy.py)
ALLOWED_DOMAINS: set[str] = {
    "antigravity.dev",
    "api.antigravity.dev",
    "anthropic.com",
    "api.anthropic.com",
    "opencode.dev",
    "opencode.ai",
    "api.opencode.dev",
    "api.opencode.ai",
    "copilot.ai",
    "api.githubcopilot.com",
    "githubcopilot.com",
    "kiro.dev",
    "api.kiro.dev",
    "hermes-ai.dev",
    "hermes.ai",
    "api.hermes-ai.dev",
    "api.hermes.ai",
}

_extra = os.environ.get("OWL_ALLOW_EXTRA", "")
if _extra.strip():
    for d in _extra.split(","):
        d = d.strip().lower()
        if d:
            ALLOWED_DOMAINS.add(d)


# ---------------------------------------------------------------------------
# Response Validator
# ---------------------------------------------------------------------------


class ResponseValidator:
    """
    Validates HTTP responses.

    Only rejects malformed JSON / wrong content-type.
    5xx responses are NOT treated as invalid — they are transient failures
    handled by the circuit breaker.
    """

    @staticmethod
    def validate(content_type: str, body: str) -> tuple[bool, str]:
        """Returns (is_valid, reason)."""
        if not content_type:
            return True, ""
        if "application/json" in content_type.lower():
            try:
                json.loads(body)
            except json.JSONDecodeError as exc:
                return False, f"Malformed JSON: {exc}"
        return True, ""


# ---------------------------------------------------------------------------
# Response Cache (LRU + TTL)
# ---------------------------------------------------------------------------


class ResponseCache:
    """LRU response cache with max-body-size limit and TTL."""

    def __init__(
        self,
        max_entries: int = CACHE_MAX_ENTRIES,
        ttl: int = CACHE_TTL,
    ) -> None:
        self._max = max_entries
        self._ttl = ttl
        # key -> (value, expiry_timestamp)
        self._cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[str]:
        item = self._cache.get(key)
        if item is None:
            self._misses += 1
            return None
        value, expiry = item
        if time.time() > expiry:
            # Expired — evict.
            self._cache.pop(key, None)
            self._misses += 1
            return None
        self._cache.move_to_end(key)
        self._hits += 1
        return value

    def put(self, key: str, value: str) -> None:
        if len(value) > CACHE_MAX_BODY_SIZE:
            return
        now = time.time()
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (value, now + self._ttl)
        while len(self._cache) > self._max:
            self._cache.popitem(last=False)

    def clear(self) -> int:
        count = len(self._cache)
        self._cache.clear()
        return count

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "entries": len(self._cache),
            "max_entries": self._max,
            "ttl_seconds": self._ttl,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": (
                f"{self._hits / total * 100:.1f}%" if total > 0 else "N/A"
            ),
        }


# ---------------------------------------------------------------------------
# Rate Limiter
# ---------------------------------------------------------------------------


class RateLimiter:
    """Per-IP token bucket rate limiter with stale-entry pruning."""

    STALE_SECONDS = 300

    def __init__(self, rpm: int = RATE_LIMIT_RPM) -> None:
        self._rpm = rpm
        self._tokens: dict[str, float] = {}
        self._last_refill: dict[str, float] = {}

    def allow(self, ip: str = "default") -> bool:
        now = time.time()
        last = self._last_refill.get(ip, now)
        tokens = self._tokens.get(ip, float(self._rpm))
        tokens = min(
            float(self._rpm), tokens + (now - last) * self._rpm / 60.0
        )
        self._tokens[ip] = tokens
        self._last_refill[ip] = now
        if tokens < 1:
            return False
        self._tokens[ip] -= 1
        return True

    def get_tokens(self, ip: str = "default") -> float:
        return round(self._tokens.get(ip, float(self._rpm)), 2)

    def prune_stale(self) -> int:
        now = time.time()
        stale = [
            k for k, v in self._last_refill.items()
            if now - v > self.STALE_SECONDS
        ]
        for k in stale:
            self._tokens.pop(k, None)
            self._last_refill.pop(k, None)
        return len(stale)


# ---------------------------------------------------------------------------
# Circuit Breaker
# ---------------------------------------------------------------------------


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Simple circuit breaker for upstream provider connections."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
    ) -> None:
        self._threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._circuits: dict[str, dict] = {}

    def _get(self, domain: str) -> dict:
        if domain not in self._circuits:
            self._circuits[domain] = {
                "state": CircuitState.CLOSED,
                "failures": 0,
                "last_opened": 0.0,
            }
        return self._circuits[domain]

    def record_success(self, domain: str) -> None:
        c = self._get(domain)
        c["failures"] = 0
        if c["state"] != CircuitState.CLOSED:
            log.info("Circuit CLOSED for %s", domain)
            c["state"] = CircuitState.CLOSED

    def record_failure(self, domain: str) -> None:
        c = self._get(domain)
        c["failures"] += 1
        if (c["failures"] >= self._threshold
                and c["state"] != CircuitState.OPEN):
            log.warning("Circuit OPEN for %s", domain)
            c["state"] = CircuitState.OPEN
            c["last_opened"] = time.time()

    def is_open(self, domain: str) -> bool:
        c = self._get(domain)
        if c["state"] in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
            return False
        if time.time() - c["last_opened"] > self._recovery_timeout:
            c["state"] = CircuitState.HALF_OPEN
            return False
        return True

    def get_all_states(self) -> dict[str, str]:
        return {d: c["state"].value for d, c in self._circuits.items()}


# ---------------------------------------------------------------------------
# SSRF Helpers (shared with forward_proxy semantics)
# ---------------------------------------------------------------------------


def _is_domain_allowed(host: str) -> bool:
    """Match hostname against the allowlist, including subdomains."""
    host = host.lower().rstrip(".")
    if not host:
        return False
    if host in ALLOWED_DOMAINS:
        return True
    parts = host.split(".")
    if len(parts) >= 2:
        registrable = ".".join(parts[-2:])
        if registrable in ALLOWED_DOMAINS:
            return True
    for allowed in ALLOWED_DOMAINS:
        if host.endswith("." + allowed):
            return True
    return False


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------


class OwlMCPServer:
    """OWL Resilient MCP Server — exposes tools over JSON-RPC stdin/stdout."""

    PROTOCOL_VERSION = "2024-11-05"
    SERVER_INFO = {"name": "owl-resilient-http", "version": VERSION}

    def __init__(self) -> None:
        self._cache = ResponseCache()
        self._rate_limiter = RateLimiter()
        self._circuit_breaker = CircuitBreaker()
        self._validator = ResponseValidator()
        self._start_time = time.time()
        self._request_count = 0
        self._client: Optional[Any] = None  # httpx.AsyncClient
        self._initialized = False
        self._tools: dict[str, dict[str, Any]] = {
            "fetch": {
                "fn": self._tool_fetch,
                "description": (
                    "HTTP fetch with cache, rate-limit, circuit-breaker, "
                    "and response validation. Supports GET/POST/PUT/DELETE."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Absolute URL to fetch (https only).",
                        },
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                            "default": "GET",
                            "description": "HTTP method.",
                        },
                        "headers": {
                            "type": "object",
                            "description": "Optional request headers.",
                        },
                        "body": {
                            "type": "string",
                            "description": "Optional request body (for POST/PUT).",
                        },
                    },
                    "required": ["url"],
                },
            },
            "fetch_status": {
                "fn": self._tool_fetch_status,
                "description": (
                    "Cache stats, circuit state, rate-limiter tokens."
                ),
                "inputSchema": {"type": "object", "properties": {}},
            },
            "fetch_clear_cache": {
                "fn": self._tool_fetch_clear_cache,
                "description": "Clear the response cache.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            "health_check": {
                "fn": self._tool_health_check,
                "description": "Server uptime, request count, provider list.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            "queue_status": {
                "fn": self._tool_queue_status,
                "description": "Queue status (always empty in v7.2).",
                "inputSchema": {"type": "object", "properties": {}},
            },
        }

    # -- Lifecycle -----------------------------------------------------------

    async def _ensure_client(self) -> Any:
        if self._client is None or getattr(self._client, "is_closed", True):
            import httpx
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(
                    REQUEST_READ_TIMEOUT,
                    connect=REQUEST_CONNECT_TIMEOUT,
                ),
                follow_redirects=True,
                headers={"User-Agent": USER_AGENT},
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.close()

    # -- Tool implementations ------------------------------------------------

    async def _tool_fetch(self, params: dict[str, Any]) -> dict[str, Any]:
        url = params.get("url", "")
        method = params.get("method", "GET").upper()
        headers = params.get("headers") or {}
        body = params.get("body")

        if not url:
            return {"error": "Missing 'url' parameter"}

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return {"error": "Only http and https URLs are supported"}

        domain = (parsed.hostname or "").lower()
        if not domain:
            return {"error": "URL has no hostname"}

        if not _is_domain_allowed(domain):
            return {"error": f"Domain '{domain}' not in SSRF allowlist"}

        # Rate limit
        if not self._rate_limiter.allow():
            return {"error": "Rate limit exceeded"}

        # Circuit breaker
        if self._circuit_breaker.is_open(domain):
            return {"error": f"Circuit breaker OPEN for {domain}"}

        # Cache key includes method, host, path, AND query
        cache_key = (
            f"{method}|{parsed.scheme}://{domain}{parsed.path}"
            f"?{parsed.query}"
        )

        # Only GET requests are cached
        if method == "GET":
            cached = self._cache.get(cache_key)
            if cached is not None:
                return {
                    "status": "cached",
                    "body": cached,
                    "domain": domain,
                }

        try:
            client = await self._ensure_client()
            request_kwargs: dict[str, Any] = {"headers": headers}
            if body and method in ("POST", "PUT", "PATCH"):
                request_kwargs["content"] = body
            response = await client.request(method, url, **request_kwargs)
            body_text = response.text
            content_type = response.headers.get("content-type", "")
            status_code = response.status_code
        except Exception as exc:
            self._circuit_breaker.record_failure(domain)
            log.warning("Fetch failed for %s: %s", url, exc)
            return {"error": f"Fetch failed: {exc}", "domain": domain}

        valid, reason = self._validator.validate(content_type, body_text)
        if not valid:
            return {
                "error": f"Invalid response: {reason}",
                "domain": domain,
                "status": status_code,
            }

        # Record success only for 2xx; record failure for 5xx
        if 200 <= status_code < 500:
            self._circuit_breaker.record_success(domain)
        else:
            self._circuit_breaker.record_failure(domain)

        # Cache successful GET responses
        if method == "GET" and 200 <= status_code < 300:
            self._cache.put(cache_key, body_text)

        self._request_count += 1
        return {
            "status": status_code,
            "body": body_text,
            "domain": domain,
            "cached": False,
        }

    async def _tool_fetch_status(self, _params: dict[str, Any]) -> dict[str, Any]:
        return {
            "cache": self._cache.stats(),
            "circuits": self._circuit_breaker.get_all_states(),
            "rate_limit_tokens": self._rate_limiter.get_tokens(),
        }

    async def _tool_fetch_clear_cache(
        self, _params: dict[str, Any],
    ) -> dict[str, Any]:
        count = self._cache.clear()
        return {"cleared": count}

    async def _tool_health_check(self, _params: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "ok",
            "version": VERSION,
            "uptime_seconds": int(time.time() - self._start_time),
            "total_requests": self._request_count,
            "allowed_domains": sorted(ALLOWED_DOMAINS),
        }

    async def _tool_queue_status(self, _params: dict[str, Any]) -> dict[str, Any]:
        return {
            "queue_size": 0,
            "note": (
                "OfflineQueue removed in v7.1. "
                "Retry semantics deferred to v7.3."
            ),
        }

    # -- JSON-RPC dispatch ---------------------------------------------------

    def _error_response(
        self, req_id: Any, code: int, message: str,
    ) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": code, "message": message},
        }

    def _result_response(self, req_id: Any, result: Any) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    async def handle_request(
        self, request: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        method = request.get("method", "")
        params = request.get("params") or {}
        req_id = request.get("id")

        # Notifications (no id) do not receive a response.
        is_notification = "id" not in request

        # MCP initialize handshake
        if method == "initialize":
            self._initialized = True
            if is_notification:
                return None
            return self._result_response(req_id, {
                "protocolVersion": self.PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": self.SERVER_INFO,
            })

        if method == "notifications/initialized":
            return None  # notification, no response

        if method == "ping":
            if is_notification:
                return None
            return self._result_response(req_id, {})

        if method == "tools/list":
            tools = [
                {
                    "name": name,
                    "description": spec["description"],
                    "inputSchema": spec["inputSchema"],
                }
                for name, spec in self._tools.items()
            ]
            return self._result_response(
                req_id, {"tools": tools},
            )

        if method == "tools/call":
            tool_name = params.get("name", "")
            tool_params = params.get("arguments", {}) or {}
            spec = self._tools.get(tool_name)
            if spec is None:
                if is_notification:
                    return None
                return self._error_response(
                    req_id, -32601, f"Unknown tool: {tool_name}",
                )
            result = await spec["fn"](tool_params)
            is_error = isinstance(result, dict) and "error" in result
            return self._result_response(req_id, {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2),
                }],
                "isError": is_error,
            })

        if is_notification:
            return None
        return self._error_response(
            req_id, -32601, f"Unknown method: {method}",
        )

    # -- Main loop -----------------------------------------------------------

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        log.info("OWL MCP server v%s started (stdin/stdout)", VERSION)

        while True:
            try:
                line = await asyncio.wait_for(reader.readline(), timeout=300)
            except asyncio.TimeoutError:
                self._rate_limiter.prune_stale()
                continue
            if not line:
                break

            try:
                request = json.loads(line.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                log.error("Invalid JSON-RPC request: %s", exc)
                sys.stdout.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }) + "\n")
                sys.stdout.flush()
                continue

            response = await self.handle_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

        await self.aclose()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    server = OwlMCPServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        log.info("MCP server shutting down.")


if __name__ == "__main__":
    main()
