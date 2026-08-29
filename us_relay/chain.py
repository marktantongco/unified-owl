#!/usr/bin/env python3
"""
us_relay/chain.py — THE MASK (freebuff-us-relay + Improvement #1)
Implements Multi-Layer Proxy Chain with 4-tier failover:
  Residential → Datacenter → Tor → Direct
- Each tier is a ProxyPool shard
- Health-aware failover
- Geo-consistent IP (US-origin token minting)
- Wraps gost :18181 + mitmproxy :8081 + ProxyEntry metadata tier
"""
import asyncio
import random
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import logging
logger = logging.getLogger("us_relay.chain")

TIER_ORDER = ["residential", "datacenter", "tor", "direct"]
TIER_PRIORITY = {t: i for i, t in enumerate(TIER_ORDER)}

@dataclass
class TierStats:
    successes: int = 0
    failures: int = 0
    avg_latency_ms: float = 9999.0

    @property
    def score(self) -> float:
        total = self.successes + self.failures
        if not total:
            return 0.5
        sr = self.successes / total
        # prefer low latency
        lat_penalty = min(self.avg_latency_ms / 2000.0, 1.0)
        return sr * (1 - lat_penalty * 0.3)

class ProxyChain:
    """4-tier chain — picks best tier then best proxy within tier."""
    def __init__(self, pool_manager=None):
        self.pool_manager = pool_manager
        self.tier_stats: Dict[str, TierStats] = {t: TierStats() for t in TIER_ORDER}
        self._failover_counts: Dict[str, int] = {t: 0 for t in TIER_ORDER}

    def _proxies_by_tier(self, tier: str) -> List[Any]:
        if not self.pool_manager or not hasattr(self.pool_manager, '_proxies'):
            return []
        # ProxyEntry.metadata.tier is set by PoolManager during discovery
        out = []
        for p in self.pool_manager._proxies:
            meta_tier = getattr(p, 'metadata', {}).get('tier', 'residential') if hasattr(p, 'metadata') else 'residential'
            # direct is synthetic — no proxy
            if tier == "direct":
                continue
            if meta_tier == tier and p.healthy and not p.is_banned():
                out.append(p)
        return out

    def pick(self, preferred_tier: Optional[str] = None) -> tuple[Optional[Any], str]:
        """Pick best proxy + tier. Returns (proxy_or_None, tier)."""
        # If preferred tier has healthy proxies, use it
        if preferred_tier and preferred_tier in TIER_ORDER:
            ps = self._proxies_by_tier(preferred_tier)
            if ps:
                # pick lowest latency / fail_count within tier
                ps.sort(key=lambda p: (p.fail_count, getattr(p, 'latency_ms', 9999)))
                return random.choice(ps[:3]) if len(ps) >= 3 else ps[0], preferred_tier
        # Otherwise iterate tier priority + health
        for tier in TIER_ORDER:
            if tier == "direct":
                return None, "direct"
            ps = self._proxies_by_tier(tier)
            if ps:
                ps.sort(key=lambda p: (p.fail_count, getattr(p, 'latency_ms', 9999)))
                return random.choice(ps[:2]) if len(ps) >= 2 else ps[0], tier
        return None, "direct"

    def report(self, tier: str, success: bool, latency_ms: float = 9999):
        s = self.tier_stats.get(tier)
        if not s:
            return
        if success:
            s.successes += 1
            # EMA latency
            if s.avg_latency_ms == 9999:
                s.avg_latency_ms = latency_ms
            else:
                s.avg_latency_ms = s.avg_latency_ms * 0.9 + latency_ms * 0.1
        else:
            s.failures += 1
        logger.debug(f"Tier {tier} report success={success} latency={latency_ms} score={s.score:.2f}")

    def failover(self, failed_tier: str) -> tuple[Optional[Any], str]:
        """Explicit failover from failed_tier to next."""
        idx = TIER_PRIORITY.get(failed_tier, 0)
        for tier in TIER_ORDER[idx+1:]:
            ps = self._proxies_by_tier(tier)
            if tier == "direct" or ps:
                self._failover_counts[tier] += 1
                logger.warning(f"Failover {failed_tier} → {tier} (count {self._failover_counts[tier]})")
                if tier == "direct":
                    return None, tier
                ps.sort(key=lambda p: p.fail_count)
                return ps[0], tier
        return None, "direct"

    def stats(self):
        return {
            "tiers": {t: {"score": s.score, "succ": s.successes, "fail": s.failures, "lat": int(s.avg_latency_ms), "failovers": self._failover_counts[t]} for t, s in self.tier_stats.items()},
            "pool_size": len(self.pool_manager._proxies) if self.pool_manager and hasattr(self.pool_manager, '_proxies') else 0,
        }

# Gost + mitmproxy wiring helpers
class EgressMultiplexer:
    """Wraps gost :18181 (HTTP+SOCK5) + mitmproxy :8081 (header sanitizer)"""
    def __init__(self, gost_port=18181, mitm_port=8081):
        self.gost_port = gost_port
        self.mitm_port = mitm_port

    def gost_url(self) -> str:
        return f"http://127.0.0.1:{self.gost_port}"

    def mitm_url(self) -> str:
        return f"http://127.0.0.1:{self.mitm_port}"

    async def health(self) -> Dict[str, bool]:
        import aiohttp
        out = {}
        for name, url in [("gost", self.gost_url()), ("mitm", self.mitm_url())]:
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.get(url, timeout=aiohttp.ClientTimeout(total=2)) as r:
                        out[name] = r.status < 500
            except Exception:
                out[name] = False
        return out

# Singleton
chain = ProxyChain()
mux = EgressMultiplexer()

if __name__ == "__main__":
    c = ProxyChain()
    print(c.stats())
    print("pick", c.pick())
    c.report("residential", True, 120)
    c.report("residential", False)
    print(c.stats())
