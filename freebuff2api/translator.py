"""
freebuff2api translator — REAL upstream racing for owl_server.

Races the workstation's local free-tier gateways (first successful response
wins) instead of simulating. Upstream credentials come from (in order of
precedence): environment variables, upstreams.json next to this file
(chmod 600 — carries provider keys).

Env overrides:
  OWL_FBU_KEY / OWL_FBU_URL   freebuff-unified  (default http://127.0.0.1:18080/v1)
  OWL_OllAMA_URL              local ollama     (default http://127.0.0.1:11434)

api surface consumed by owl_server.py:
  api.models() -> dict
  api.chat(body) -> dict      (OpenAI envelope + owl_provider/owl_latency_ms)
  api.stats()  -> dict
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger("freebuff2api.translator")

# ---------------------------------------------------------------------------
# Upstream registry
# ---------------------------------------------------------------------------

def _load_static_config() -> Dict[str, Any]:
    """Optional upstreams.json next to this file; env vars win over it."""
    cfg: Dict[str, Any] = {}
    try:
        path = Path(__file__).with_name("upstreams.json")
        if path.exists():
            cfg = json.loads(path.read_text())
    except Exception as e:  # malformed file must never kill the racer
        logger.warning("upstreams.json unreadable: %s", e)
    return cfg


_STATIC = _load_static_config()

FBU_URL = os.environ.get("OWL_FBU_URL", _STATIC.get("fbu_url", "http://127.0.0.1:18080/v1")).rstrip("/")
FBU_KEY = os.environ.get("OWL_FBU_KEY", _STATIC.get("fbu_key", ""))
FBU_MODEL = os.environ.get("OWL_FBU_MODEL", _STATIC.get("fbu_model", "z-ai/glm-5.3-flash"))

OLLAMA_URL = os.environ.get("OWL_OLLAMA_URL", _STATIC.get("ollama_url", "http://127.0.0.1:11434")).rstrip("/")
OLLAMA_MODEL = os.environ.get("OWL_OLLAMA_MODEL", _STATIC.get("ollama_model", "qwen2.5:3b"))

RACE_TIMEOUT = float(os.environ.get("OWL_RACE_TIMEOUT", "30"))


def _upstreams() -> List[Dict[str, Any]]:
    """Ordered upstream list: freebuff-unified primary, ollama always-on fallback."""
    ups: List[Dict[str, Any]] = [
        {
            "name": "freebuff-unified",
            "kind": "openai",
            "url": f"{FBU_URL}/chat/completions",
            "key": FBU_KEY,
            "model": FBU_MODEL,
            "priority": 1,
        },
        {
            "name": "ollama",
            "kind": "openai",
            "url": f"{OLLAMA_URL}/v1/chat/completions",
            "key": "",
            "model": OLLAMA_MODEL,
            "priority": 3,
        },
    ]
    return [u for u in ups if u["url"]]


MODELS = [
    {"id": "owl-auto-racer", "object": "model", "owned_by": "owl",
     "description": "Races local free-tier gateways, first success wins"},
    {"id": "gpt-4o", "object": "model", "owned_by": "owl"},
    {"id": "claude-3.5-sonnet", "object": "model", "owned_by": "owl"},
    {"id": FBU_MODEL, "object": "model", "owned_by": "owl"},
    {"id": OLLAMA_MODEL, "object": "model", "owned_by": "owl"},
]

# ---------------------------------------------------------------------------
# Translation helpers (kept from the original translator)
# ---------------------------------------------------------------------------


def translate_incoming(body: dict) -> dict:
    """Normalize any provider format to OpenAI. Handles messages vs prompt vs contents."""
    if "messages" in body:
        return body
    if "contents" in body:  # Gemini
        msgs = []
        for c in body["contents"]:
            role = c.get("role", "user")
            parts = c.get("parts", [])
            text = " ".join(p.get("text", "") for p in parts)
            msgs.append({"role": role, "content": text})
        return {"model": body.get("model", "owl-auto-racer"),
                "messages": msgs, "stream": body.get("stream", False)}
    if "prompt" in body and "messages" not in body:  # legacy Anthropic prompt
        return {"model": body.get("model", "owl-auto-racer"),
                "messages": [{"role": "user", "content": body["prompt"]}], "stream": False}
    return body


def translate_outgoing(provider: str, data: dict, latency_ms: float) -> dict:
    """Wrap provider response into an OpenAI envelope with provenance."""
    if "choices" in data:
        data["owl_provider"] = provider
        data["owl_latency_ms"] = round(latency_ms)
        return data
    text = data.get("content") or data.get("text") or data.get("message") or "ok"
    return {
        "id": f"chatcmpl-owl-{int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": data.get("model", provider),
        "owl_provider": provider,
        "owl_latency_ms": round(latency_ms),
        "choices": [{"index": 0,
                     "message": {"role": "assistant", "content": text},
                     "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0,
                  "completion_tokens": len(text.split()),
                  "total_tokens": len(text.split())},
    }


# ---------------------------------------------------------------------------
# Real upstream racing
# ---------------------------------------------------------------------------


async def _call_upstream(session: aiohttp.ClientSession, up: Dict[str, Any],
                         messages: List[dict], timeout: float) -> dict:
    """POST one OpenAI-compatible upstream; return its raw JSON or raise."""
    payload = {"model": up["model"], "messages": messages, "stream": False}
    headers = {"Content-Type": "application/json"}
    if up.get("key"):
        headers["Authorization"] = f"Bearer {up['key']}"
    async with session.post(up["url"], json=payload, headers=headers,
                            timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
        raw = await resp.text()
        if resp.status != 200:
            raise RuntimeError(f"{up['name']} http {resp.status}: {raw[:160]}")
        data = json.loads(raw)
        if "error" in data:
            raise RuntimeError(f"{up['name']} upstream error: {str(data['error'])[:160]}")
        return data


async def race_upstreams(messages: List[dict], model: str = "owl-auto-racer",
                         timeout: float = RACE_TIMEOUT) -> dict:
    """Fire every upstream in parallel; first successful chat completion wins."""
    targets = _upstreams()
    if not targets:
        raise RuntimeError("no upstreams configured for the racer")

    connector = aiohttp.TCPConnector(limit=len(targets))
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = {asyncio.create_task(_call_upstream(session, up, messages, timeout)): up
                 for up in targets}
        start = time.time()
        deadline = start + timeout + 2
        errors: List[str] = []
        try:
            pending = set(tasks)
            # First success wins; failed upstreams are dropped from the wait set
            # so a fast-failing primary never spins the loop.
            while pending and time.time() < deadline:
                done, pending = await asyncio.wait(pending, timeout=max(deadline - time.time(), 0.1),
                                                   return_when=asyncio.FIRST_COMPLETED)
                for d in done:
                    up = tasks[d]
                    try:
                        data = d.result()
                        latency = (time.time() - start) * 1000
                        return translate_outgoing(up["name"], data, latency)
                    except Exception as e:
                        errors.append(f"{up['name']}: {str(e)[:120]}")
            for t in pending:
                t.cancel()
            if not errors:
                errors = [f"timeout: no upstream answered within {timeout}s"]
            raise RuntimeError("all upstreams failed — " + "; ".join(errors[:5]))
        finally:
            for t in tasks:
                if not t.done():
                    t.cancel()


def list_models() -> dict:
    return {"object": "list", "data": MODELS}


# ---------------------------------------------------------------------------
# Clean API surface for owl_server.py
# ---------------------------------------------------------------------------

class Freebuff2API:
    def __init__(self):
        self.request_count = 0
        self.last_provider: Optional[str] = None

    async def chat(self, body: dict) -> dict:
        self.request_count += 1
        norm = translate_incoming(body)
        messages = norm.get("messages") or [{"role": "user", "content": "ok"}]
        if not isinstance(messages, list) or not messages:
            raise RuntimeError("translator: no messages after normalization")
        res = await race_upstreams(messages, norm.get("model", "owl-auto-racer"))
        self.last_provider = res.get("owl_provider")
        return res

    def models(self) -> dict:
        return list_models()

    def stats(self) -> dict:
        return {"requests": self.request_count,
                "upstreams": len(_upstreams()),
                "models": len(MODELS),
                "last_provider": self.last_provider}


api = Freebuff2API()

if __name__ == "__main__":
    async def _test():
        print(json.dumps(api.models(), indent=2))
        res = await api.chat({"model": "owl-auto-racer",
                              "messages": [{"role": "user", "content": "say OK"}]})
        print(json.dumps(res, indent=2))
    asyncio.run(_test())
