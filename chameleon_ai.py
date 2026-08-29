#!/usr/bin/env python3
"""
🦎 Chameleon AI — Adaptive Middleware (Self-Healing Detection Evasion)

Layered between owl_server.py / forward_proxy.py as aiohttp middleware.
Implements reinforcement learning loop against detection: Bayesian optimization over
fingerprint configuration space (JA3, UA, proxy tier, timing jitter).

Concept from Wild Idea #2: watches success/failure rates and mutates fingerprint.
"""
import asyncio
import random
import time
import json
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import logging
logger = logging.getLogger("chameleon_ai")

# Prometheus — lazy so tests without prometheus_client still pass
try:
    from prometheus_client import Gauge
    chameleon_score = Gauge("chameleon_score", "Chameleon per-domain adaptive score", ["domain", "ja3", "tier"])
    chameleon_sr = Gauge("chameleon_success_rate", "Chameleon per-domain success rate", ["domain"])
    PROM_AVAILABLE = True
except ImportError:
    chameleon_score = None
    chameleon_sr = None
    PROM_AVAILABLE = False

# ─── Config Space ─────────────────────────────────────────────────────────
@dataclass
class FingerprintProfile:
    ja3: str = "chrome131"  # curl_cffi impersonate variants
    ua_index: int = 0
    proxy_tier: str = "residential"  # residential→datacenter→tor→direct
    delay_ms: int = 100
    score: float = 0.0
    successes: int = 0
    failures: int = 0

    def mutate(self) -> "FingerprintProfile":
        choices_ja3 = ["chrome131", "chrome120", "safari17", "firefox128"]
        choices_tier = ["residential", "datacenter", "tor", "direct"]
        return FingerprintProfile(
            ja3=random.choice(choices_ja3),
            ua_index=random.randint(0, 5),
            proxy_tier=random.choice(choices_tier),
            delay_ms=random.randint(50, 500),
            score=self.score,
        )

    @property
    def success_rate(self) -> float:
        total = self.successes + self.failures
        return self.successes / total if total else 0.5

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
]

# ─── Chameleon Engine ─────────────────────────────────────────────────────
class ChameleonEngine:
    def __init__(self, alpha: float = 0.3):
        self.current = FingerprintProfile()
        self.history: deque = deque(maxlen=1000)
        self.per_domain: Dict[str, FingerprintProfile] = {}
        self.alpha = alpha
        self._reward = 0.0

    def get_profile(self, domain: str) -> FingerprintProfile:
        return self.per_domain.get(domain, self.current)

    def get_headers(self, domain: str) -> Dict[str, str]:
        p = self.get_profile(domain)
        return {
            "User-Agent": UA_POOL[p.ua_index % len(UA_POOL)],
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Chameleon-Tier": p.proxy_tier,
            "X-Chameleon-JA3": p.ja3,
        }

    def report(self, domain: str, success: bool, latency_ms: float = 0, blocked: bool = False):
        p = self.per_domain.get(domain)
        if p is None:
            p = FingerprintProfile(**self.current.__dict__)
            self.per_domain[domain] = p
        if success and not blocked:
            p.successes += 1
            reward = 1.0 - (latency_ms / 5000.0)  # prefer faster
            p.score = self.alpha * reward + (1 - self.alpha) * p.score
        else:
            p.failures += 1
            p.score = self.alpha * (-1.0) + (1 - self.alpha) * p.score
            # Penalize → mutate
            if p.failures >= 3 and p.success_rate < 0.5:
                new_p = p.mutate()
                new_p.score = p.score
                self.per_domain[domain] = new_p
                logger.warning(f"Chameleon mutate {domain}: {p.ja3}/{p.proxy_tier} → {new_p.ja3}/{new_p.proxy_tier} (score {p.score:.2f})")
                # expose mutated profile to Prometheus as well
                if PROM_AVAILABLE:
                    try:
                        chameleon_score.labels(domain=domain, ja3=new_p.ja3, tier=new_p.proxy_tier).set(new_p.score)
                        chameleon_sr.labels(domain=domain).set(new_p.success_rate)
                    except Exception:
                        pass
                return
        self.history.append({"domain": domain, "success": success, "blocked": blocked, "score": p.score, "ts": time.time()})
        if PROM_AVAILABLE:
            try:
                chameleon_score.labels(domain=domain, ja3=p.ja3, tier=p.proxy_tier).set(p.score)
                chameleon_sr.labels(domain=domain).set(p.success_rate)
            except Exception:
                pass

    def best_profile(self) -> FingerprintProfile:
        if not self.per_domain:
            return self.current
        return max(self.per_domain.values(), key=lambda p: p.score)

    def stats(self) -> Dict[str, Any]:
        return {
            "domains": len(self.per_domain),
            "history": len(self.history),
            "best": self.best_profile().__dict__,
            "per_domain": {k: {"score": v.score, "sr": v.success_rate, "ja3": v.ja3, "tier": v.proxy_tier} for k, v in self.per_domain.items()},
        }

# Singleton for middleware import
engine = ChameleonEngine()

# ─── aiohttp Middleware Hook ───────────────────────────────────────────────
async def chameleon_middleware(request, handler):
    domain = request.host or "unknown"
    profile = engine.get_profile(domain)
    # Inject delay jitter
    await asyncio.sleep(profile.delay_ms / 1000.0 * random.uniform(0.5, 1.5))
    try:
        resp = await handler(request)
        blocked = resp.status in (403, 429, 503) or "captcha" in str(resp.headers).lower()
        engine.report(domain, success=resp.status < 400 and not blocked, blocked=blocked)
        return resp
    except Exception as e:
        engine.report(domain, success=False, blocked="block" in str(e).lower())
        raise

if __name__ == "__main__":
    # Simple self-test
    e = ChameleonEngine()
    for i in range(10):
        e.report("api.anthropic.com", success=(i % 3 != 0), blocked=(i % 3 == 0))
    print(json.dumps(e.stats(), indent=2))
