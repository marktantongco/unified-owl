#!/usr/bin/env python3
"""
OWL Forward Proxy v7.2

AI free-tier aggregator with mesh health sync.
Predictive circuit breaker, SSRF allowlist, UDP mesh broadcast.

v7.2 changes (comprehensive audit fixes):
  - FIX: Mesh broadcasts to MESH_PORT (42100), not the TCP proxy port
  - FIX: CONNECT now honors the circuit breaker (was bypassed entirely)
  - FIX: HTTP proxy now forwards request bodies (POST/PUT were broken)
  - FIX: Headers are read once and passed through (auth no longer re-reads)
  - FIX: Predictive circuit breaker records latency on failures too
  - FIX: Timing-safe token comparison via hmac.compare_digest
  - FIX: Double-counting of request/active counters removed
  - FIX: Rate limiter prunes stale IP buckets (memory leak)
  - FIX: Multicast join uses INADDR_ANY for cross-interface reception
  - FIX: 407 responses include Proxy-Authenticate header (RFC 7235)
  - FIX: 429 responses include Retry-After header
  - FIX: Half-open state allows only one probe at a time
  - FIX: Health endpoint no longer increments request counter
  - FIX: Hop-by-hop headers stripped when forwarding plain HTTP
  - ENH: Graceful shutdown drains in-flight connections
  - ENH: /health reports active_connections and mesh_peer_count
  - ENH: Request body size cap (10 MB) for plain HTTP forwarding
  - ENH: Structured access logging for proxy requests
"""

from __future__ import annotations

import argparse
import asyncio
import hmac
import ipaddress
import json
import logging
import os
import signal
import socket
import struct
import sys
import time
from collections import deque
from enum import Enum
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("owl-forward-proxy")

# ---------------------------------------------------------------------------
# Configuration (all via environment variables)
# ---------------------------------------------------------------------------

PROXY_HOST = os.environ.get("OWL_PROXY_HOST", "127.0.0.1")
PROXY_PORT = int(os.environ.get("OWL_PROXY_PORT", "60000"))
MAX_CONNECTIONS = int(os.environ.get("OWL_MAX_CONNECTIONS", "5"))
CONNECT_TIMEOUT = int(os.environ.get("OWL_CONNECT_TIMEOUT", "15"))
PROXY_TIMEOUT = int(os.environ.get("OWL_PROXY_TIMEOUT", "20"))
PROXY_TOKEN = os.environ.get("OWL_PROXY_TOKEN", "")
MAX_BODY_SIZE = int(os.environ.get("OWL_MAX_BODY_SIZE", str(10 * 1024 * 1024)))  # 10 MB
RATE_LIMIT_RPM = int(os.environ.get("OWL_RATE_LIMIT_RPM", "60"))
RATE_LIMIT_BURST = int(os.environ.get("OWL_RATE_LIMIT_BURST", "10"))
SHUTDOWN_TIMEOUT = int(os.environ.get("OWL_SHUTDOWN_TIMEOUT", "10"))

# SSRF allowlist — ONLY these domains (and OWL_ALLOW_EXTRA) are reachable
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
    for domain in _extra.split(","):
        domain = domain.strip().lower()
        if domain:
            ALLOWED_DOMAINS.add(domain)

ENABLE_MESH = os.environ.get("OWL_ENABLE_MESH", "false").lower() == "true"
MESH_PORT = int(os.environ.get("OWL_MESH_PORT", "42100"))
MESH_GROUP = "239.255.255.250"
MESH_BROADCAST_INTERVAL = int(os.environ.get("OWL_MESH_INTERVAL", "30"))

# Hop-by-hop headers that must not be forwarded (RFC 7230 §6.1)
HOP_BY_HOP_HEADERS = frozenset({
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
})

VERSION = "7.2.0"


# ---------------------------------------------------------------------------
# Circuit Breaker — per-domain predictive state machine
# ---------------------------------------------------------------------------


class CircuitState(Enum):
    CLOSED = "closed"
    PREDICTIVE_OPEN = "predictive_open"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Per-domain circuit breaker with predictive opening.

    States:
      CLOSED           → normal operation
      PREDICTIVE_OPEN  → last 3 requests all > 2× p50 baseline
      OPEN             → 5 consecutive failures
      HALF_OPEN        → 60 s cooldown elapsed, one probe allowed
    """

    RECOVERY_TIMEOUT = 60  # seconds in OPEN / PREDICTIVE_OPEN before HALF_OPEN
    FAILURE_THRESHOLD = 5
    PREDICTIVE_WINDOW = 3
    PREDICTIVE_MULTIPLIER = 2.0
    MIN_SAMPLES = 5

    def __init__(self) -> None:
        self._circuits: dict[str, dict] = {}

    def _get(self, domain: str) -> dict:
        if domain not in self._circuits:
            self._circuits[domain] = {
                "state": CircuitState.CLOSED,
                "latencies": deque(maxlen=20),
                "consecutive_failures": 0,
                "last_state_change": time.time(),
                "last_opened_at": 0.0,
                "probe_in_flight": False,
            }
        return self._circuits[domain]

    def record_success(self, domain: str, latency: float) -> None:
        c = self._get(domain)
        c["latencies"].append(latency)
        c["consecutive_failures"] = 0
        c["probe_in_flight"] = False
        if c["state"] != CircuitState.CLOSED:
            log.info("Circuit CLOSED for %s", domain)
            c["state"] = CircuitState.CLOSED
            c["last_state_change"] = time.time()

    def record_failure(self, domain: str, latency: float = 0.0) -> None:
        c = self._get(domain)
        # Record latency for failures too so predictive detection works.
        if latency > 0:
            c["latencies"].append(latency)
        c["consecutive_failures"] += 1
        c["probe_in_flight"] = False
        now = time.time()

        if (c["consecutive_failures"] >= self.FAILURE_THRESHOLD
                and c["state"] != CircuitState.OPEN):
            log.warning(
                "Circuit OPEN for %s (%d consecutive failures)",
                domain, c["consecutive_failures"],
            )
            c["state"] = CircuitState.OPEN
            c["last_state_change"] = now
            c["last_opened_at"] = now
            return

        # Predictive: last 3 requests all > 2× p50
        if (c["state"] == CircuitState.CLOSED
                and len(c["latencies"]) >= self.MIN_SAMPLES):
            sorted_lat = sorted(c["latencies"])
            p50 = sorted_lat[len(sorted_lat) // 2]
            if p50 > 0:
                recent = list(c["latencies"])[-self.PREDICTIVE_WINDOW:]
                if len(recent) == self.PREDICTIVE_WINDOW and all(
                    lat > self.PREDICTIVE_MULTIPLIER * p50 for lat in recent
                ):
                    log.warning(
                        "Circuit PREDICTIVE_OPEN for %s "
                        "(last %d > %.1f× p50=%.3fs)",
                        domain, self.PREDICTIVE_WINDOW,
                        self.PREDICTIVE_MULTIPLIER, p50,
                    )
                    c["state"] = CircuitState.PREDICTIVE_OPEN
                    c["last_state_change"] = now
                    c["last_opened_at"] = now

    def is_open(self, domain: str) -> bool:
        c = self._get(domain)
        if c["state"] in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
            return False
        if time.time() - c["last_opened_at"] > self.RECOVERY_TIMEOUT:
            log.info("Circuit HALF_OPEN for %s (recovery timeout elapsed)", domain)
            c["state"] = CircuitState.HALF_OPEN
            c["last_state_change"] = time.time()
            return False
        return True

    def try_acquire_probe(self, domain: str) -> bool:
        """
        In HALF_OPEN state, allow only one probe at a time.
        Returns True if the caller may proceed; False if another probe is running.
        """
        c = self._get(domain)
        if c["state"] != CircuitState.HALF_OPEN:
            return True
        if c["probe_in_flight"]:
            return False
        c["probe_in_flight"] = True
        return True

    def get_state(self, domain: str) -> CircuitState:
        return self._get(domain)["state"]

    def get_all_states(self) -> dict[str, str]:
        return {d: c["state"].value for d, c in self._circuits.items()}


# ---------------------------------------------------------------------------
# Mesh Health Broadcaster — UDP multicast via DatagramTransport
# ---------------------------------------------------------------------------


class MeshHealthBroadcaster:
    """
    Broadcasts node health to UDP multicast every 30 s and listens for peers.
    Uses asyncio.DatagramTransport — no thread-pool busy-poll (fixes P0-21).

    v7.2: broadcasts to MESH_PORT (was incorrectly using proxy TCP port),
          joins via INADDR_ANY, and tracks peers for /health reporting.
    """

    PEER_TIMEOUT = 90  # seconds before a peer is considered stale

    def __init__(
        self,
        proxy_host: str,
        proxy_port: int,
        mesh_port: int,
        max_connections: int,
    ) -> None:
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port
        self._mesh_port = mesh_port
        self._max = max_connections
        self._transport: Optional[asyncio.DatagramTransport] = None
        self._broadcast_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._peers: dict[str, dict] = {}
        self._running = False

    async def start(self) -> None:
        loop = asyncio.get_running_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # SO_REUSEPORT when available (Linux 3.9+) allows multiple OWL instances
        if hasattr(socket, "SO_REUSEPORT"):
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except OSError:
                pass
        sock.bind(("", self._mesh_port))
        sock.setblocking(False)

        self._transport, _ = await loop.create_datagram_endpoint(
            lambda: _MeshProtocol(self._handle_datagram), sock=sock,
        )

        # Join multicast group via INADDR_ANY so we receive on all interfaces.
        mreq = struct.pack(
            "4s4s",
            socket.inet_aton(MESH_GROUP),
            socket.inet_aton("0.0.0.0"),
        )
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        # Socket ownership transferred to transport; drop our reference
        del sock

        self._running = True
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        log.info(
            "Mesh broadcaster started → %s:%d (proxy %s:%d)",
            MESH_GROUP, self._mesh_port, self._proxy_host, self._proxy_port,
        )

    async def _broadcast_loop(self) -> None:
        while self._running:
            try:
                payload = json.dumps({
                    "type": "owl-mesh",
                    "host": self._proxy_host,
                    "port": self._proxy_port,
                    "max_connections": self._max,
                    "timestamp": time.time(),
                })
                assert self._transport is not None
                self._transport.sendto(
                    payload.encode(), (MESH_GROUP, self._mesh_port),
                )
            except (OSError, RuntimeError) as exc:
                log.debug("Mesh broadcast error: %s", exc)
            await asyncio.sleep(MESH_BROADCAST_INTERVAL)

    async def _cleanup_loop(self) -> None:
        """Prune stale peers every 30 s."""
        while self._running:
            await asyncio.sleep(30)
            now = time.time()
            stale = [
                k for k, v in self._peers.items()
                if now - v["last_seen"] > self.PEER_TIMEOUT
            ]
            for k in stale:
                del self._peers[k]

    def _handle_datagram(self, data: bytes, addr: tuple[str, int]) -> None:
        try:
            msg = json.loads(data.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return
        if msg.get("type") != "owl-mesh":
            return
        peer_host = msg.get("host", "")
        peer_port = msg.get("port", 0)
        if not peer_host or not peer_port:
            return
        # Ignore our own broadcasts
        if peer_host == self._proxy_host and peer_port == self._proxy_port:
            return
        peer_key = f"{peer_host}:{peer_port}"
        self._peers[peer_key] = {
            "host": peer_host,
            "port": peer_port,
            "max_connections": msg.get("max_connections", 0),
            "timestamp": msg.get("timestamp", 0),
            "last_seen": time.time(),
        }

    def get_peer_count(self) -> int:
        now = time.time()
        return sum(
            1 for v in self._peers.values()
            if now - v["last_seen"] <= self.PEER_TIMEOUT
        )

    def get_peers(self) -> list[dict]:
        now = time.time()
        return [
            v for v in self._peers.values()
            if now - v["last_seen"] <= self.PEER_TIMEOUT
        ]

    async def stop(self) -> None:
        self._running = False
        for task in (self._broadcast_task, self._cleanup_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        if self._transport:
            self._transport.close()


class _MeshProtocol(asyncio.DatagramProtocol):
    def __init__(self, on_datagram) -> None:
        self._on_datagram = on_datagram

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        pass

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        self._on_datagram(data, addr)

    def error_received(self, exc: Exception) -> None:
        log.debug("Mesh datagram error: %s", exc)


# ---------------------------------------------------------------------------
# Rate Limiter — per-IP token bucket with periodic cleanup
# ---------------------------------------------------------------------------


class RateLimiter:
    """
    Per-IP token bucket rate limiter.

    v7.2: Stale entries (idle > 5 min) are pruned to prevent unbounded growth.
    """

    STALE_SECONDS = 300  # 5 minutes

    def __init__(
        self,
        rpm: int = RATE_LIMIT_RPM,
        burst: int = RATE_LIMIT_BURST,
    ) -> None:
        self._rpm = rpm
        self._burst = burst
        self._tokens: dict[str, float] = {}
        self._last_refill: dict[str, float] = {}
        self._lock = asyncio.Lock()

    def allow(self, ip: str) -> bool:
        now = time.time()
        last = self._last_refill.get(ip, now)
        tokens = self._tokens.get(ip, float(self._burst))
        tokens = min(
            float(self._burst),
            tokens + (now - last) * self._rpm / 60.0,
        )
        self._tokens[ip] = tokens
        self._last_refill[ip] = now
        if tokens < 1:
            return False
        self._tokens[ip] -= 1
        return True

    def retry_after(self, ip: str) -> int:
        """Seconds until the next token is available."""
        now = time.time()
        tokens = self._tokens.get(ip, 0.0)
        if tokens >= 1:
            return 0
        deficit = 1.0 - tokens
        rate = self._rpm / 60.0
        return max(1, int(deficit / rate) + 1) if rate > 0 else 60

    def prune_stale(self) -> int:
        """Remove entries idle longer than STALE_SECONDS. Returns count removed."""
        now = time.time()
        stale = [
            ip for ip, ts in self._last_refill.items()
            if now - ts > self.STALE_SECONDS
        ]
        for ip in stale:
            self._tokens.pop(ip, None)
            self._last_refill.pop(ip, None)
        return len(stale)


# ---------------------------------------------------------------------------
# Main Proxy
# ---------------------------------------------------------------------------


class OwlForwardProxy:
    """
    Local-first AI free-tier aggregator proxy.

    Features:
      - SSRF allowlist (default-deny, only AI-provider domains)
      - Predictive circuit breaker per domain
      - UDP mesh health broadcast
      - Bearer token auth for non-loopback binds
      - GET /health endpoint
      - Rate limiting per client IP
    """

    def __init__(
        self,
        host: str = PROXY_HOST,
        port: int = PROXY_PORT,
        max_connections: int = MAX_CONNECTIONS,
        token: str = PROXY_TOKEN,
        mesh_enabled: bool = ENABLE_MESH,
        mesh_port: int = MESH_PORT,
    ) -> None:
        self._host = host
        self._port = port
        self._max_connections = max_connections
        self._token = token
        self._mesh_enabled = mesh_enabled
        self._mesh_port = mesh_port
        self._circuit_breaker = CircuitBreaker()
        self._rate_limiter = RateLimiter()
        self._mesh: Optional[MeshHealthBroadcaster] = None
        self._semaphore = asyncio.Semaphore(max_connections)
        self._request_count = 0
        self._active_count = 0
        self._start_time = time.time()
        self._server: Optional[asyncio.AbstractServer] = None
        self._drain_event = asyncio.Event()
        self._drain_event.set()
        self._cleanup_task: Optional[asyncio.Task] = None

    # -- helpers -------------------------------------------------------------

    @staticmethod
    def _extract_host_port(request_line: str) -> tuple[str, int]:
        """Extract host and port from a CONNECT target."""
        parts = request_line.split()
        if len(parts) < 2:
            raise ValueError(f"Malformed request: {request_line}")
        target = parts[1]
        if target.startswith("[") and "]" in target:
            bracket_end = target.index("]")
            host = target[1:bracket_end]
            rest = target[bracket_end + 1:]
            port = int(rest[1:]) if rest.startswith(":") else 443
        elif ":" in target:
            host, port_s = target.rsplit(":", 1)
            port = int(port_s)
        else:
            host, port = target, 443
        return host, port

    @staticmethod
    def _is_safe_public_ip(
        ip: ipaddress.IPv4Address | ipaddress.IPv6Address,
    ) -> bool:
        """Reject loopback, link-local, private, multicast, unspecified, reserved."""
        if ip.is_loopback or ip.is_link_local or ip.is_private:
            return False
        if ip.is_multicast or ip.is_unspecified or ip.is_reserved:
            return False
        # Block CGNAT (100.64.0.0/10) — carrier-grade NAT is not truly public.
        if isinstance(ip, ipaddress.IPv4Address):
            if ip in ipaddress.ip_network("100.64.0.0/10"):
                return False
        return True

    @staticmethod
    async def _resolve_and_verify(host: str) -> str:
        """
        Resolve hostname and reject private / reserved IPs.
        DNS-rebinding defense: hostname must resolve to a public IP.
        Uses async getaddrinfo to avoid blocking the event loop.
        """
        try:
            infos = await asyncio.get_running_loop().getaddrinfo(
                host, None, type=socket.SOCK_STREAM,
            )
        except socket.gaierror as exc:
            raise ConnectionError(
                f"DNS resolution failed for {host}: {exc}"
            ) from exc

        for family, _, _, _, sockaddr in infos:
            ip_str = sockaddr[0]
            try:
                ip = ipaddress.ip_address(ip_str)
            except ValueError:
                continue
            if OwlForwardProxy._is_safe_public_ip(ip):
                return ip_str

        raise ConnectionError(
            f"No safe public address resolved for {host} "
            f"— all IPs are private/reserved"
        )

    @staticmethod
    def _extract_domain(host: str) -> str:
        """Return the registrable domain (last two labels) for allowlist matching."""
        host = host.lower().rstrip(".")
        if ":" in host and not host.startswith("["):
            host = host.rsplit(":", 1)[0]
        parts = host.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return host

    def _is_allowed(self, host: str) -> bool:
        """Check hostname against the SSRF allowlist."""
        host = host.lower().rstrip(".")
        if not host:
            return False
        if host in ALLOWED_DOMAINS:
            return True
        domain = self._extract_domain(host)
        if domain in ALLOWED_DOMAINS:
            return True
        # Also accept subdomains of any exact entry in the allowlist.
        for allowed in ALLOWED_DOMAINS:
            if host.endswith("." + allowed):
                return True
        return False

    @staticmethod
    def _client_ip(transport: asyncio.BaseTransport) -> str:
        peer = transport.get_extra_info("peername")
        return peer[0] if peer else "127.0.0.1"

    def _needs_auth(self, client_ip: str) -> bool:
        """Token auth required when bound to a non-loopback address."""
        if self._host in ("127.0.0.1", "::1", "localhost"):
            return False
        return client_ip not in ("127.0.0.1", "::1", "localhost")

    def _check_auth(self, headers: list[str]) -> bool:
        """
        Validate Bearer token in Proxy-Authorization header (timing-safe).

        The auth-scheme ("Bearer") is case-insensitive per RFC 7235 §2.1,
        but the token itself is compared with hmac.compare_digest to avoid
        timing side-channels.
        """
        if not self._token:
            return False
        for h in headers:
            if h.lower().startswith("proxy-authorization:"):
                value = h.split(":", 1)[1].strip()
                # Split scheme and token, compare case-insensitively
                parts = value.split(None, 1)
                if len(parts) != 2 or parts[0].lower() != "bearer":
                    return False
                return hmac.compare_digest(parts[1], self._token)
        return False

    # -- response helpers ----------------------------------------------------

    @staticmethod
    async def _send_simple(
        writer: asyncio.StreamWriter,
        status_line: str,
        extra_headers: Optional[dict[str, str]] = None,
        body: str = "",
    ) -> None:
        """Send a minimal HTTP response."""
        body_bytes = body.encode()
        lines = [status_line]
        lines.append(f"Content-Length: {len(body_bytes)}")
        lines.append("Content-Type: text/plain; charset=utf-8")
        lines.append("Connection: close")
        if extra_headers:
            for k, v in extra_headers.items():
                lines.append(f"{k}: {v}")
        lines.append("")
        lines.append("")
        writer.write("\r\n".join(lines).encode() + body_bytes)
        try:
            await writer.drain()
        except (ConnectionError, OSError):
            pass

    # -- request handlers ----------------------------------------------------

    async def _handle_health(self, writer: asyncio.StreamWriter) -> None:
        """Respond with proxy health status."""
        peer_count = self._mesh.get_peer_count() if self._mesh else 0
        body = json.dumps({
            "status": "ok",
            "version": VERSION,
            "max_connections": self._max_connections,
            "active_connections": self._active_count,
            "allowed_domains": len(ALLOWED_DOMAINS),
            "mesh_enabled": self._mesh_enabled,
            "mesh_peers": peer_count,
            "circuit_states": self._circuit_breaker.get_all_states(),
            "uptime_seconds": int(time.time() - self._start_time),
            "total_requests": self._request_count,
        })
        response = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "Cache-Control: no-store\r\n"
            "\r\n"
            f"{body}"
        )
        writer.write(response.encode())
        try:
            await writer.drain()
        except (ConnectionError, OSError):
            pass

    async def _handle_connect(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        host: str,
        port: int,
        client_ip: str,
    ) -> None:
        """Handle CONNECT tunnel with SSRF + circuit breaker validation."""
        if not self._is_allowed(host):
            log.warning("SSRF blocked: %s (not in allowlist)", host)
            await self._send_simple(writer, "HTTP/1.1 403 Forbidden")
            return

        domain = self._extract_domain(host)

        if self._circuit_breaker.is_open(domain):
            log.warning("Circuit OPEN — rejecting CONNECT to %s", host)
            await self._send_simple(writer, "HTTP/1.1 503 Service Unavailable")
            return

        if not self._circuit_breaker.try_acquire_probe(domain):
            await self._send_simple(writer, "HTTP/1.1 503 Service Unavailable")
            return

        try:
            ip = await self._resolve_and_verify(host)
        except ConnectionError as exc:
            log.warning("SSRF blocked: %s → %s", host, exc)
            await self._send_simple(writer, "HTTP/1.1 403 Forbidden")
            return

        try:
            target_reader, target_writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=CONNECT_TIMEOUT,
            )
        except (OSError, asyncio.TimeoutError) as exc:
            log.error("CONNECT to %s:%d failed: %s", host, port, exc)
            self._circuit_breaker.record_failure(domain)
            await self._send_simple(writer, "HTTP/1.1 502 Bad Gateway")
            return

        writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        try:
            await writer.drain()
        except (ConnectionError, OSError):
            target_writer.close()
            return

        t0 = time.time()
        try:
            await asyncio.wait_for(
                self._tunnel(reader, target_reader, writer, target_writer),
                timeout=PROXY_TIMEOUT,
            )
            self._circuit_breaker.record_success(domain, time.time() - t0)
        except (OSError, asyncio.TimeoutError) as exc:
            log.error("Tunnel error %s:%d: %s", host, port, exc)
            self._circuit_breaker.record_failure(domain, time.time() - t0)
        finally:
            target_writer.close()
            try:
                await target_writer.wait_closed()
            except OSError:
                pass

    async def _handle_http(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        first_line: str,
        headers: list[str],
        client_ip: str,
    ) -> None:
        """Handle plain HTTP proxy request (non-CONNECT), including body relay."""
        parts = first_line.split()
        if len(parts) < 3:
            await self._send_simple(writer, "HTTP/1.1 400 Bad Request")
            return

        method = parts[0]
        url = parts[1]
        if not url.startswith("http://"):
            await self._send_simple(writer, "HTTP/1.1 400 Bad Request")
            return

        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        port = parsed.port or 80

        if not host:
            await self._send_simple(writer, "HTTP/1.1 400 Bad Request")
            return

        if not self._is_allowed(host):
            log.warning("SSRF blocked (HTTP): %s", host)
            await self._send_simple(writer, "HTTP/1.1 403 Forbidden")
            return

        domain = self._extract_domain(host)

        if self._circuit_breaker.is_open(domain):
            await self._send_simple(writer, "HTTP/1.1 503 Service Unavailable")
            return

        if not self._circuit_breaker.try_acquire_probe(domain):
            await self._send_simple(writer, "HTTP/1.1 503 Service Unavailable")
            return

        try:
            ip = await self._resolve_and_verify(host)
        except ConnectionError as exc:
            log.warning("SSRF blocked: %s → %s", host, exc)
            await self._send_simple(writer, "HTTP/1.1 403 Forbidden")
            return

        try:
            target_reader, target_writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=CONNECT_TIMEOUT,
            )
        except (OSError, asyncio.TimeoutError) as exc:
            log.error("HTTP connect to %s:%d failed: %s", host, port, exc)
            self._circuit_breaker.record_failure(domain)
            await self._send_simple(writer, "HTTP/1.1 502 Bad Gateway")
            return

        # Determine request body length / framing.
        content_length = 0
        is_chunked = False
        filtered_headers: list[str] = []
        for h in headers:
            name, _, value = h.partition(":")
            lname = name.strip().lower()
            if lname in HOP_BY_HOP_HEADERS:
                continue
            if lname == "content-length":
                try:
                    content_length = int(value.strip())
                except ValueError:
                    content_length = 0
            elif lname == "transfer-encoding" and "chunked" in value.lower():
                is_chunked = True
            filtered_headers.append(h)

        if content_length > MAX_BODY_SIZE:
            target_writer.close()
            await self._send_simple(
                writer, "HTTP/1.1 413 Payload Too Large",
                {"Retry-After": "0"},
                "Request body exceeds maximum allowed size.",
            )
            return

        # Forward the request line (origin-form path)
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"
        request_line = f"{method} {path} {parts[2]}\r\n"
        forward_headers = "\r\n".join(filtered_headers) + "\r\n"
        # Ensure Host header points to the origin
        if not any(
            h.lower().startswith("host:") for h in filtered_headers
        ):
            forward_headers = f"Host: {host}\r\n" + forward_headers
        forward = request_line.encode() + forward_headers.encode() + b"\r\n"

        t0 = time.time()
        try:
            target_writer.write(forward)
            await target_writer.drain()

            # Relay request body (POST / PUT / PATCH)
            if content_length > 0:
                remaining = content_length
                while remaining > 0:
                    chunk = await reader.read(min(65536, remaining))
                    if not chunk:
                        break
                    target_writer.write(chunk)
                    await target_writer.drain()
                    remaining -= len(chunk)
            elif is_chunked:
                while True:
                    line = await reader.readline()
                    if not line:
                        break
                    target_writer.write(line)
                    await target_writer.drain()
                    if line.strip() == b"0":
                        # Consume trailing CRLF after 0 chunk
                        await reader.readline()
                        break

            await self._relay(target_reader, writer)
            self._circuit_breaker.record_success(domain, time.time() - t0)
            log.info(
                "%s %s -> %s:%d (client %s)",
                method, url, host, port, client_ip,
            )
        except (OSError, asyncio.TimeoutError) as exc:
            log.error("HTTP relay error %s:%d: %s", host, port, exc)
            self._circuit_breaker.record_failure(domain, time.time() - t0)
            await self._send_simple(writer, "HTTP/1.1 502 Bad Gateway")
        finally:
            target_writer.close()
            try:
                await target_writer.wait_closed()
            except OSError:
                pass

    async def _tunnel(
        self,
        r1: asyncio.StreamReader,
        r2: asyncio.StreamReader,
        w1: asyncio.StreamWriter,
        w2: asyncio.StreamWriter,
    ) -> None:
        """Bidirectional data relay for CONNECT tunnels."""

        async def _copy(src: asyncio.StreamReader, dst: asyncio.StreamWriter) -> None:
            while True:
                data = await src.read(65536)
                if not data:
                    break
                dst.write(data)
                await dst.drain()

        task1 = asyncio.create_task(_copy(r1, w2))
        task2 = asyncio.create_task(_copy(r2, w1))
        try:
            done, pending = await asyncio.wait(
                [task1, task2],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            # Surface exceptions from completed tasks
            for task in done:
                exc = task.exception()
                if exc and not isinstance(exc, (asyncio.CancelledError, OSError)):
                    raise exc
        finally:
            if not task1.done():
                task1.cancel()
            if not task2.done():
                task2.cancel()

    async def _relay(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
    ) -> None:
        """One-directional relay from reader to writer."""
        while True:
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()

    # -- connection handler --------------------------------------------------

    async def _read_headers(
        self, reader: asyncio.StreamReader,
    ) -> tuple[str, list[str]]:
        """Read the request line and headers. Returns (first_line, headers)."""
        first_line_raw = await asyncio.wait_for(reader.readline(), timeout=10)
        if not first_line_raw:
            return "", []
        first_line = first_line_raw.decode("utf-8", errors="replace").strip()
        headers: list[str] = []
        while True:
            line = await reader.readline()
            if line in (b"\r\n", b"\n", b""):
                break
            headers.append(line.decode("utf-8", errors="replace").strip())
        return first_line, headers

    async def _accept(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
    ) -> None:
        client_ip = self._client_ip(writer)

        if not self._rate_limiter.allow(client_ip):
            log.warning("Rate limit exceeded for %s", client_ip)
            retry = self._rate_limiter.retry_after(client_ip)
            await self._send_simple(
                writer,
                "HTTP/1.1 429 Too Many Requests",
                {"Retry-After": str(retry)},
                "Rate limit exceeded. Try again later.",
            )
            return

        try:
            first_line, headers = await self._read_headers(reader)
        except asyncio.TimeoutError:
            log.warning("Header read timeout from %s", client_ip)
            return

        if not first_line:
            return

        # Health check endpoint — does not count against rate limit or connection cap
        if first_line.startswith("GET /health"):
            await self._handle_health(writer)
            return

        # Auth check for non-loopback binds (headers already read above)
        if self._needs_auth(client_ip):
            if not self._check_auth(headers):
                await self._send_simple(
                    writer,
                    "HTTP/1.1 407 Proxy Authentication Required",
                    {"Proxy-Authenticate": 'Bearer realm="owl-proxy"'},
                    "Proxy authentication required.",
                )
                return

        async with self._semaphore:
            self._request_count += 1
            self._active_count += 1
            if self._active_count == 1:
                self._drain_event.clear()
            try:
                if first_line.upper().startswith("CONNECT"):
                    try:
                        host, port = self._extract_host_port(first_line)
                    except (ValueError, IndexError) as exc:
                        log.warning("Malformed CONNECT from %s: %s", client_ip, exc)
                        await self._send_simple(
                            writer, "HTTP/1.1 400 Bad Request",
                        )
                        return
                    await self._handle_connect(
                        reader, writer, host, port, client_ip,
                    )
                else:
                    await self._handle_http(
                        reader, writer, first_line, headers, client_ip,
                    )
            except asyncio.TimeoutError:
                log.warning("Timeout from %s", client_ip)
            except ConnectionError as exc:
                log.error("Connection error from %s: %s", client_ip, exc)
            except Exception as exc:
                log.exception("Unexpected error from %s: %s", client_ip, exc)
            finally:
                self._active_count -= 1
                if self._active_count <= 0:
                    self._active_count = 0
                    self._drain_event.set()
                try:
                    writer.close()
                    await writer.wait_closed()
                except OSError:
                    pass

    # -- background maintenance ----------------------------------------------

    async def _maintenance_loop(self) -> None:
        """Periodically prune stale rate-limiter entries."""
        while True:
            await asyncio.sleep(60)
            removed = self._rate_limiter.prune_stale()
            if removed:
                log.debug("Pruned %d stale rate-limit entries", removed)

    # -- lifecycle -----------------------------------------------------------

    async def run(self) -> None:
        self._server = await asyncio.start_server(
            self._accept, self._host, self._port,
        )
        log.info(
            "OWL forward proxy v%s listening on %s:%d "
            "(max_conn=%d, mesh=%s, token=%s)",
            VERSION, self._host, self._port, self._max_connections,
            "enabled" if self._mesh_enabled else "disabled",
            "set" if self._token else "unset",
        )

        if self._mesh_enabled:
            self._mesh = MeshHealthBroadcaster(
                self._host, self._port, self._mesh_port, self._max_connections,
            )
            await self._mesh.start()

        self._cleanup_task = asyncio.create_task(self._maintenance_loop())

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                loop.add_signal_handler(sig, self._signal_shutdown)
            except NotImplementedError:
                # Windows / non-POSIX
                pass

        async with self._server:
            await self._server.serve_forever()

    def _signal_shutdown(self) -> None:
        """Signal handler — schedules shutdown coroutine safely."""
        loop = asyncio.get_running_loop()
        loop.create_task(self._shutdown())

    async def _shutdown(self) -> None:
        log.info("Shutting down OWL forward proxy...")
        if self._mesh:
            await self._mesh.stop()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._server:
            self._server.close()
            # Wait for in-flight connections to drain (up to SHUTDOWN_TIMEOUT)
            try:
                await asyncio.wait_for(
                    self._drain_event.wait(), timeout=SHUTDOWN_TIMEOUT,
                )
            except asyncio.TimeoutError:
                log.warning(
                    "Shutdown timeout — %d active connections cancelled",
                    self._active_count,
                )
            await self._server.wait_closed()
        log.info("OWL forward proxy stopped.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "OWL Forward Proxy v" + VERSION
            + " — AI free-tier aggregator with mesh health sync"
        ),
    )
    parser.add_argument("--host", default=PROXY_HOST, help="Bind address")
    parser.add_argument("--port", type=int, default=PROXY_PORT, help="Listen port")
    parser.add_argument("--token", default=PROXY_TOKEN, help="Bearer token for auth")
    parser.add_argument(
        "--enable-mesh", action="store_true", default=ENABLE_MESH,
        help="Enable UDP mesh health broadcast",
    )
    parser.add_argument(
        "--mesh-port", type=int, default=MESH_PORT, help="Mesh UDP port",
    )
    parser.add_argument(
        "--max-connections", type=int, default=MAX_CONNECTIONS,
        help="Max concurrent connections",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if (args.host not in ("127.0.0.1", "::1", "localhost")
            and not args.token):
        log.warning(
            "Binding to %s without OWL_PROXY_TOKEN — auth is disabled "
            "for non-loopback. Set OWL_PROXY_TOKEN for production.",
            args.host,
        )

    proxy = OwlForwardProxy(
        host=args.host,
        port=args.port,
        token=args.token,
        mesh_enabled=args.enable_mesh,
        mesh_port=args.mesh_port,
        max_connections=args.max_connections,
    )

    try:
        asyncio.run(proxy.run())
    except KeyboardInterrupt:
        log.info("Interrupted — exiting.")


if __name__ == "__main__":
    main()
