# Skills Registry — Unified OWL Installer

> Generated 2026-08-29 from 5 parallel deep-research sub-agents.
> Source: https://skills.sh/trending + /tmp/owl-repos/owl-orca-ai-agentic-stack/skills (99) + GitHub/Perplexity/Firecrawl audits
> Policy: installs >1K, reputable owner, security audits pass

## Meta

| Meta Skill | Installs | Source | Purpose |
|---|---|---|---|
| `find-skills` | 3.2M | `vercel-labs/skills` | Discovery: `npx skills find [query]` → leaderboard → verify → `npx skills add` |

## Curated Skills by Domain

| Domain | Skill | Installs | Owner | Install Command | Status |
|---|---|---|---|---|---|
| proxy | `api-gateway-skill` (LOCAL) | LOCAL | owl-orca | bundled `skills/api-gateway-skill/SKILL.md` | ✅ bundle |
| proxy | `combined-proxy-billing` (LOCAL) | LOCAL | owl-orca | bundled | ✅ bundle |
| proxy | `cloudflare` | 67.9K | cloudflare/skills (590K) | `npx skills add cloudflare/skills --skill cloudflare` | ✅ lazy |
| proxy | `workers-best-practices` | 58.6K | cloudflare/skills | `npx skills add cloudflare/skills --skill workers-best-practices` | ✅ lazy |
| auth | `browser-use-owl` (LOCAL) | LOCAL | owl-orca | bundled | ✅ bundle |
| auth | `persistent-memory` (LOCAL) | LOCAL | owl-orca | bundled | ✅ bundle |
| anti-detection | `browser-fingerprint-audit` | 30.6K | liarjsdev/liarjs-skills (122K) | `npx skills add liarjsdev/liarjs-skills --skill browser-fingerprint-audit` | ✅ |
| anti-detection | `playwright-stealth-verify` | 30.5K | liarjsdev | `npx skills add liarjsdev/liarjs-skills --skill playwright-stealth-verify` | ✅ |
| anti-detection | `anti-detect-browser` | 64.5K | antibrow (132K) | `npx skills add antibrow/anti-detect-browser-skills --skill anti-detect-browser` | ✅ |
| anti-detection | `fingerprint-ci-gate` | 30.6K | liarjsdev | `npx skills add liarjsdev/liarjs-skills --skill fingerprint-ci-gate` | ✅ CI |
| ml | `mcp-builder` | 108K | anthropics/skills | `npx skills add anthropics/skills --skill mcp-builder` | ✅ |
| edge | `wrangler` | 65.6K | cloudflare/skills | `npx skills add cloudflare/skills --skill wrangler` | ✅ |
| edge | `durable-objects` | 52.6K | cloudflare/skills | `npx skills add cloudflare/skills --skill durable-objects` | optional |
| installer | `skill-creator` | 365K | anthropics/skills | `npx skills add anthropics/skills --skill skill-creator` | ✅ |
| worktree | `using-git-worktrees` | 176K | obra/superpowers | `npx skills add obra/superpowers --skill using-git-worktrees` | ✅ |
| worktree | `finishing-a-development-branch` | 172K | obra/superpowers | `npx skills add obra/superpowers --skill finishing-a-development-branch` | ✅ |
| worktree | `context-compressor` (LOCAL) | LOCAL | owl-orca | bundled | ✅ |
| docs | `writing-plans` | 232K | obra/superpowers | `npx skills add obra/superpowers --skill writing-plans` | ✅ |
| docs | `web-design-guidelines` | 3.0K | vercel-labs/agent-skills | `npx skills add vercel-labs/agent-skills --skill web-design-guidelines` | optional |

## Local Bundle (not on registry, authoritative)

`api-gateway-skill`, `combined-proxy-billing`, `browser-use-owl`, `persistent-memory`, `mcp-builder-billing`, `context-compressor`, `deployment-manager`, `skill-router`, `skill-scanner` — copy from `/tmp/owl-repos/owl-orca-ai-agentic-stack/skills/`

## Install Order

```bash
npx skills add vercel-labs/skills --skill find-skills
npx skills add obra/superpowers --skill using-git-worktrees
npx skills add obra/superpowers --skill finishing-a-development-branch
npx skills add cloudflare/skills --skill wrangler
npx skills add cloudflare/skills --skill workers-best-practices
npx skills add liarjsdev/liarjs-skills --skill browser-fingerprint-audit
npx skills add liarjsdev/liarjs-skills --skill playwright-stealth-verify
npx skills add liarjsdev/liarjs-skills --skill fingerprint-ci-gate
npx skills add antibrow/anti-detect-browser-skills --skill anti-detect-browser
npx skills add anthropics/skills --skill mcp-builder
npx skills add anthropics/skills --skill skill-creator
```

## Rejected

- `h4gen/stealth-proxy` (477 dl <1K), `b0tresch/b0tresch-stealth-browser` (964 dl + VirusTotal Suspicious)
- `cloudflare-docs/*` (<1K per skill), `higgsfield-*` (1.0K borderline niche), generic `rate-limit` (<1K)
- Dual lock `package-lock.json` vs `bun.lock` → keep `bun.lock` only

## End-to-End Journey Simulations

See Firecrawl/Perplexity sub-agent outputs — 6 steps: curl|bash → owl fetch hot-cache → auth TTL → JA3 trigger → wrangler deploy → worktree dev
