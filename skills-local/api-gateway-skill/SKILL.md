# API Gateway Skill

## Context
Use this skill when you need to build, configure, or optimize an API gateway that routes requests between clients and multiple AI provider backends (Anthropic, OpenAI, Kiro, etc.). Specialized for the OWL-AGENT unified proxy architecture where billing middleware runs in-process.

**Trigger phrases:** "API gateway," "route AI requests," "proxy configuration," "multi-provider routing," "gateway middleware."

## Purpose
Provides intelligent request routing, caching, rate limiting, and billing-aware middleware for AI API proxy deployments. Acts as the traffic controller between client applications and upstream AI providers.

## Use-Case
- Route Claude Max subscription requests through billing-injected proxy
- Kiro fallback when Anthropic rate limits hit
- Multi-model routing (GPT-4, Claude, Gemini) with cost optimization
- Request deduplication and caching for identical queries

## Misconception
That an API gateway is just a reverse proxy. In the OWL-AGENT architecture, the gateway IS the billing middleware — it runs 7-layer sanitization, fingerprint rotation, and billing injection in-process. Treating it as a simple pass-through defeats the entire purpose.

## Conspiracy
Gateways add latency and are a bottleneck. Reality: In v5.0, the billing middleware runs IN-PROCESS, eliminating the 2-hop chain that existed in v4.0. The gateway now adds ~2-5ms per request for billing injection, down from ~15-25ms for the old Python→Node→upstream chain.

## Mostly Overlooked
The /metrics endpoint exposes Prometheus-compatible data that can be used for auto-scaling, anomaly detection, and cost attribution. Most operators set up the gateway and never look at the metrics.

## Contradictions
- High availability requires Redis, but Redis adds operational complexity
- Rate limiting protects upstream but can block legitimate burst traffic
- Caching reduces cost but may serve stale responses for time-sensitive queries

## Compatible With
- **persistent-memory**: Stores billing state, token quotas, and rate limit counters across restarts
- **mcp-builder**: Exposes billing/spending data as MCP tools for AI agent queries
- **deployment-manager**: Handles tiered deployment (dev/staging/prod) with proper config
- **browser-use**: Automates OAuth token refresh via browser automation
- **combined-proxy-billing**: Provides the centralized billing backend that the gateway feeds into

## Not Compatible With
- Direct-to-upstream client configurations (bypasses gateway entirely)
- Multiple independent gateways without shared Redis (causes rate limit drift)

## Stackable
Yes — can be stacked with persistent-memory, mcp-builder, and deployment-manager for a complete production stack.

## Not Stackable With
Another API gateway on the same port. Running nginx + OWL gateway on port 60000 will conflict.

## Stackable Best Combined To
- api-gateway-skill + persistent-memory + mcp-builder = Full observability stack
- api-gateway-skill + deployment-manager + browser-use = Zero-touch deployment with auto-auth

## Stackable Worst Combined To
- api-gateway-skill + another-proxy-gateway = Port conflicts, routing confusion

## OWL-AGENT v5.0 Integration
The API gateway IS the OWL-AGENT unified proxy. The Python proxy_defense_unified_v5.py serves as both the gateway and the billing middleware. The Node.js MCP sidecar (:4623) provides auxiliary MCP orchestration only. Key endpoints:
- GET /health — comprehensive health including billing circuit breaker state
- GET /metrics — Prometheus-compatible metrics
- POST /v1/messages — primary API route with billing injection
- GET /kiro/* — Kiro fallback route
- POST /rotate-now — manual fingerprint rotation

## Instructions
1. Configure SECRETS_PATH to point to unified secrets.json
2. Set OWL_TIER to dev (no Redis), staging (single Redis), or prod (Sentinel)
3. Add proxy providers to proxy_pool.json for traffic rotation
4. Monitor /health and /metrics endpoints
5. Use /rotate-now if fingerprint detection is suspected
