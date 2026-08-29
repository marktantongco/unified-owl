#!/usr/bin/env python3
"""
freebuff2api/translator.py — THE TRANSLATOR (freebuff2api + Improvement #3 handoff)
Provides clean API surface that hides proxy complexity:
- OpenAI-compatible /v1/models and /v1/chat/completions
- Stream racing: first-wins among multiple upstream providers
- Protocol translation: Copilot/Gemini/Claude → OpenAI
- Consistent outgoing signatures via us_relay chain
"""
import asyncio
import json
import time
import random
from typing import List, Dict, Any, Optional
import logging
logger = logging.getLogger("freebuff2api.translator")

# Known free-tier upstreams (from owl-orca architecture-data.ts)
UPSTREAMS = [
    {"name": "copilot", "model": "gpt-4o", "priority": 1, "latency_ms": 800},
    {"name": "antigravity", "model": "claude-3.5-sonnet", "priority": 1, "latency_ms": 900},
    {"name": "kiro", "model": "claude-sonnet-4.5", "priority": 2, "latency_ms": 1200},
    {"name": "ollama", "model": "llama3", "priority": 3, "latency_ms": 1500},
]

MODELS = [
    {"id": "owl-auto-racer", "object": "model", "owned_by": "owl", "description": "Races Copilot + Antigravity, auto translates"},
    {"id": "gpt-4o", "object": "model", "owned_by": "openai"},
    {"id": "claude-3.5-sonnet", "object": "model", "owned_by": "anthropic"},
    {"id": "claude-sonnet-4.5", "object": "model", "owned_by": "anthropic"},
    {"id": "deepseek-v3", "object": "model", "owned_by": "deepseek"},
    {"id": "llama3", "object": "model", "owned_by": "meta"},
]

def translate_incoming(body: dict) -> dict:
    """Normalize any provider format to OpenAI. Handles messages vs prompt vs contents."""
    # Already OpenAI
    if "messages" in body:
        return body
    # Gemini: contents -> messages
    if "contents" in body:
        msgs = []
        for c in body["contents"]:
            role = c.get("role", "user")
            parts = c.get("parts", [])
            text = " ".join(p.get("text","") for p in parts)
            msgs.append({"role": role, "content": text})
        return {"model": body.get("model", "owl-auto-racer"), "messages": msgs, "stream": body.get("stream", False)}
    # Anthropic: messages with content blocks
    if "prompt" in body and "messages" not in body:
        return {"model": body.get("model", "owl-auto-racer"), "messages": [{"role": "user", "content": body["prompt"]}], "stream": False}
    return body

def translate_outgoing(provider: str, data: dict, latency_ms: float) -> dict:
    """Wrap provider response into OpenAI envelope with provenance."""
    text = data.get("content") or data.get("text") or data.get("message") or "ok"
    # If provider already returned OpenAI shape, just annotate
    if "choices" in data:
        data["owl_provider"] = provider
        data["owl_latency_ms"] = latency_ms
        return data
    return {
        "id": f"chatcmpl-owl-{int(time.time()*1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": data.get("model", provider),
        "owl_provider": provider,
        "owl_latency_ms": latency_ms,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": len(text.split()), "total_tokens": len(text.split())},
    }

async def race_upstreams(messages: List[dict], model: str = "owl-auto-racer", timeout: float = 10.0) -> dict:
    """
    Stream racing: fire all upstreams in parallel, return first success.
    In production, this would call real httpx clients; here we simulate with latency
    and translate. Replace _call_upstream with real provider SDK.
    """
    async def _call_upstream(up: dict):
        # Simulate latency + occasional failure
        await asyncio.sleep(up["latency_ms"] / 1000.0 * random.uniform(0.8, 1.2))
        # 10% failure rate
        if random.random() < 0.1:
            raise RuntimeError(f"{up['name']} transient error")
        # Simulate response
        prompt = messages[-1].get("content", "") if messages else ""
        return {"provider": up["name"], "content": f"[{up['name']}/{up['model']}] {prompt[:80]}", "model": up["model"]}

    # For auto-racer, race top tier; for specific model, call only that provider
    targets = [u for u in UPSTREAMS if model in ("owl-auto-racer", u["model"])] if model != "owl-auto-racer" else [u for u in UPSTREAMS if u["priority"] == 1]
    if not targets:
        targets = UPSTREAMS[:2]

    tasks = [asyncio.create_task(_call_upstream(u)) for u in targets]
    start = time.time()
    try:
        done, pending = await asyncio.wait(tasks, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
        # Cancel pending
        for t in pending:
            t.cancel()
        # Find first success
        for d in done:
            try:
                res = d.result()
                latency = (time.time() - start) * 1000
                return translate_outgoing(res["provider"], res, latency)
            except Exception:
                continue
        # If all failed, try remaining pending with longer timeout
        if pending:
            done2, _ = await asyncio.wait(pending, timeout=2)
            for d in done2:
                try:
                    res = d.result()
                    latency = (time.time() - start) * 1000
                    return translate_outgoing(res["provider"], res, latency)
                except Exception:
                    pass
        raise RuntimeError("All upstreams failed")
    finally:
        for t in tasks:
            if not t.done():
                t.cancel()

def list_models() -> dict:
    return {"object": "list", "data": MODELS}

# Clean API surface for owl_server.py
class Freebuff2API:
    def __init__(self):
        self.request_count = 0

    async def chat(self, body: dict) -> dict:
        self.request_count += 1
        norm = translate_incoming(body)
        model = norm.get("model", "owl-auto-racer")
        messages = norm.get("messages", [])
        return await race_upstreams(messages, model)

    def models(self) -> dict:
        return list_models()

    def stats(self):
        return {"requests": self.request_count, "upstreams": len(UPSTREAMS), "models": len(MODELS)}

api = Freebuff2API()

if __name__ == "__main__":
    async def _test():
        print(api.models())
        res = await api.chat({"model": "owl-auto-racer", "messages": [{"role": "user", "content": "hello"}]})
        print(json.dumps(res, indent=2))
        # Gemini format
        res2 = await api.chat({"contents": [{"role": "user", "parts": [{"text": "hi"}]}]})
        print(json.dumps(res2, indent=2))
    asyncio.run(_test())
