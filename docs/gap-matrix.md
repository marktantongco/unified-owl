# Gap Matrix — 6 Repos → Unified

> Source: gap-analysis + docs-crawl + dep-graph sub-agents (2026-08-29)

## P0 Block Merge (must fix before code port)

| # | Gap | Canonical | Fix |
|---|---|---|---|
| P0-1 | ProxyEntry dataclass diverge (3 forks) | `owl-agent/proxy_defense.py:220` slots=True | Add `metadata: Dict` field, migrate cache shape, delete ProxyItem duplicate |
| P0-2 | LRU+dedup binary-safe vs legacy | `owl-dns-synergy/core.py: HTTPCache + RequestDeduplicator` | Port to `libs/cache.py` everywhere |
| P0-3 | SSRF only in gateway | `forward_proxy.py:68 ALLOWED_DOMAINS` | Extract `owl_security/ssrf.py`, call before every open_connection |
| P0-4 | Fernet+zlib only in synergy | `core.py:388 CryptoManager` | Port to libs, gate behind CRYPTO_AVAILABLE, add cryptography 50.0.0 |
| P0-5 | DNS tunnel only synergy | `router_v3.py` | Keep as channels/dns.py optional behind 7-channel |
| P0-6 | 7-channel only synergy | `router_v3.py:113` | Make router/ package, merge proxy_pool channel |
| P0-7 | Transactional installer only synergy | `install.sh 828L trap ERR` | Promote synergy install.sh as base, inject OWL_HOME defaults |
| P0-8 | Python 3.14 fiction | `requires-python >=3.10` + patch gated >=3.12 | Pin >=3.11, CI matrix 3.10/3.11/3.14 |
| P0-9 | Missing LICENSE + .env leak | MIT | Copy MIT to installer + orca, rm .env, add .gitignore |
| P0-10 | 3-port spec no bind | `architecture-data.ts:60001/8333/60000` + forward_proxy.py | Implement owl_server binds for 60000/60001/8333 |
| P0-11 | Mesh broadcast lib | `forward_proxy.py:246 MeshHealthBroadcaster` | Extract mesh/broadcast.py sidecar |
| P0-12 | OAuth harvesting only installer | `oauth manager preflight/` | Port auth/oauth.py, integrate with key rotator |

## P1 Nice-to-have

ML predictor (libs/ml.py), plugin loader, A/B harness, predictive CB (2×p50), headless browser channel, worktree helper, stream racing (asyncio.gather first-wins), lock dedup (keep bun.lock)

## Merge Order

`① owl-dns-synergy (hardened router+lock) → ② owl-agent (lib) → ③ free-ai-proxy-gateway → ④ owl-agent-stack (stealth) → ⑤ owl-agent-installer (rewrite) → ⑥ owl-orca (isolate docs)`

## Dep Pins

python:3.11-slim, Node 20, Go 1.24.4, Rust 1.70+, mitmproxy 12.2.3, gost 3.0.0, aiohttp 3.14.3, cryptography 50.0.0, proxybroker2 2.0.0a4
