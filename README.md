# 🦉 Unified OWL — Merged Ecosystem + Chameleon AI + FBaaS Edge

> **One installer, 6 repos merged, 3 improvements, adaptive stealth, edge-deployed.**
> Built from `owl-dns-synergy` (7-channel router) + `owl-agent` (lib) + `free-ai-proxy-gateway` (SSRF+mesh) + `owl-agent-stack` (gost+mitm) + `owl-agent-installer` (OAuth routing) + `owl-orca` (wiki/spec)

[![Version](https://img.shields.io/badge/version-1.0.0-blue)]() [![Python](https://img.shields.io/badge/python-3.11%20slim-blue)]() [![Node](https://img.shields.io/badge/node-20-green)]() [![Tests](https://img.shields.io/badge/tests-78%2F78-brightgreen)]()

## Quick Start (Beginner — 30s)

```bash
# 1. One-liner (creates ~/.owl-agent + venv + global AGENTS.md)
curl -fsSL https://raw.githubusercontent.com/marktantongco/unified-owl/main/install.sh | bash

# 2. Verify AGENTS.md persistence
bash install.sh --verify-agents
# Global : ~/.config/opencode/AGENTS.md — FOUND ✅
# Project: ./AGENTS.md — FOUND ✅
# Pinned SHA: 75d286671c4f8151fb526d8fe19e29a433fefba5

# 3. Start server (3 ports: 60000 tunnel, 60001 orca router, 8333 kiro)
python owl_server.py --host 127.0.0.1 --api-port 60000 --ab-test --ml --ml-model auto

# 4. Fetch (hot-cache 0ms on repeat)
curl -X POST http://127.0.0.1:60000/fetch -H 'Content-Type: application/json' -d '{"url":"https://example.com"}'
curl http://127.0.0.1:60000/health
curl http://127.0.0.1:60000/stats
curl http://127.0.0.1:9090/metrics | grep owl_proxy
curl http://127.0.0.1:60000/chameleon/stats  # adaptive fingerprint scores
```

## Prerequisites

| Need | Version | Check |
|---|---|---|
| Python | 3.11 slim | `python3 --version` |
| Node | 20 | `node --version` |
| Go | 1.24.4 | `go version` |
| Rust | 1.70+ | `rustc --version` |
| gost | 3.0.0 | `gost -V` |
| mitmproxy | 12.2.3 | `mitmproxy --version` |

`install.sh` checks all, creates `~/.owl-agent/venv`, installs `requirements.txt` (aiohttp 3.14.3, cryptography 50.0.0, proxybroker2 2.0.0a4).

## Architecture

```
User → freebuff2api (clean API)
        → gateway (free-ai-proxy :60000, SSRF allowlist, predictive CB, mesh UDP 42100)
          → OWL Core (ResilientClient: Cache/Dedup/RateLimiter/QualityScorer/Pool/ML)
            → 7-Channel Cascade (cached/http_proxy/socks_pool/dns_tunnel/mitm_stealth/connect_chain/http_direct)
              → L2 Crypto (Fernet+zlib) → L1 DNS Chunking (base36/63B)
                → Chameleon AI (mutates JA3/UA/proxy tier on 403/429 feedback, EMA α=0.3)
                  → FBaaS Edge (wrangler deploy to CF Workers, real regional IPs)
```

- **Improvement #1 Multi-Layer Proxy Chain**: Residential → DC → Tor → Direct with `ProxyEntry.metadata.tier` and `QualityScorer` failover
- **Improvement #2 Auth Pipeline**: OAuth harvesting (`auth/oauth.py` via `OPENROUTER_KEY_1..9` rotation, Fernet vault), injected via `owl_server` middleware
- **Improvement #3 Anti-Detection**: `curl_cffi chrome131` + `clean_headers.py` mitmproxy :8081 + `playwright-stealth-verify` + Chameleon RL loop

## Ports

| Port | Service | Env |
|---|---|---|
| 60000 | Forward Proxy / OWL API | `OWL_PROXY_HOST/PORT` |
| 60001 | Orca Router (Brain) | `ORCA_ROUTER_PORT` |
| 8333 | Kiro Gateway | `KIRO_GATEWAY_PORT` |
| 8081 | mitmproxy header sanitizer | `MITM_PORT` |
| 18181 | gost multiplexer | `GOST_PORT` |
| 42100/udp | Mesh broadcast 239.255.255.250 | `OWL_MESH_PORT` |
| 5353 | DNS tunnel | `DNS_PORT` |
| 9090 | Prometheus | `PROM_PORT` |

## Skills (exhaustive audit pre-code)

All skills verified >1K installs, reputable owner, audits pass. See `docs/skills-registry.md`.

**Install meta first:**
```bash
npx skills add vercel-labs/skills --skill find-skills      # 3.2M
npx skills add obra/superpowers --skill using-git-worktrees # 176K
npx skills add cloudflare/skills --skill wrangler            # 65K
```

## Chameleon AI

```python
from chameleon_ai import engine
engine.report("api.anthropic.com", success=False, blocked=True)  # triggers mutate
print(engine.stats())  # per-domain score, JA3, tier
```

Middleware auto-injected in `owl_server.py:middlewewares=[chameleon_middleware]` — EMA `α=0.3`, mutates on `failures≥3 && sr<0.5`, jitter `50-500ms`.

## FBaaS Edge

```bash
cd edge && npx wrangler deploy --config wrangler.toml
curl https://owl-fbaas-edge.<user>.workers.dev/health
```

Real regional IPs sidestep proxy detection. See `edge/wrangler.toml` + `edge/worker.js`.

## Installer Preflight

`install.sh` guarantees `AGENTS.md` survives `git init` (stash/restore), syncs global ↔ project via symlink, pins `75d286671c4f8151fb526d8fe19e29a433fefba5` (`sha256 49eb054a...`), and checks cross-harness (opencode vs cursor).

```bash
bash install.sh --verify-agents   # full check
bash install.sh --pin-sha <new>   # update pin
bash install.sh --sync-agents     # force project ← global
```

## Worktree & Compression

```bash
git worktree add ../owl-hotfix hotfix/foo && cd ../owl-hotfix
bash install.sh --verify-agents && pytest
# Bundle
tar -czf ../owl-worktree-hotfix.tgz --exclude=venv --exclude=.git --exclude=__pycache__ . && sha256sum ../owl-worktree-hotfix.tgz
# Top-level
bash scripts/compress.sh  # creates unified-owl-v1.0.0.tar.gz
```

## Testing

```bash
make test 2>/dev/null || pytest -q
python -m py_compile proxy_defense.py owl_server.py chameleon_ai.py && echo OK
curl http://127.0.0.1:60000/health | jq
bash diagnose.sh
```

## Wiki

`mkdocs serve` → `http://127.0.0.1:8000` (material theme, 4 PDFs from `docs-synergy/` + `docs/`)

## Troubleshooting

| Symptom | Fix |
|---|---|
| `AGENTS.md drift` | `diff -u ~/.config/opencode/AGENTS.md ./AGENTS.md` or `bash install.sh --sync-agents` |
| `407 Proxy-Auth` on 0.0.0.0 | Set `OWL_PROXY_TOKEN=$(openssl rand -hex 32)` |
| `aiohttp 3.11 vs 3.14` conflict | `pip install -r requirements.txt` (locks 3.14.3) |
| `proxybroker2 get_event_loop` | Patched for 3.12+ in `proxy_defense.py:42` |
| `package-lock vs bun.lock` | Keep `bun.lock` only, `bun install --frozen-lockfile` |

## License

MIT — see `LICENSE` (pinned SHA `75d286671c...` for prompt)
