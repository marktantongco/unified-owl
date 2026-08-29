# Combined Proxy Billing

## Context
Use this skill when you need a centralized billing backend that tracks usage across multiple proxy instances, calculates costs, enforces quotas, and provides billing data for reporting. This is the financial ledger for the OWL-AGENT ecosystem.

**Trigger phrases:** "billing backend," "usage tracking," "cost calculation," "quota enforcement," "spending reports," "billing database."

## Purpose
Provides a SQLite-based billing server that ingests usage events from the API gateway, calculates costs per model/token, enforces user quotas, and exposes billing data via REST API for dashboards and MCP agent queries.

## Use-Case
- Track token usage per API key across all proxy instances
- Calculate costs using model-specific pricing (Claude Sonnet vs Opus vs Kiro)
- Enforce per-user daily/monthly quotas with hard and soft limits
- Generate billing reports for cost attribution
- Expose spending data to MCP agents for autonomous budget management

## Misconception
That billing injection in the proxy IS the billing system. Billing injection (the 7-layer sanitization + fingerprint) is about routing — it makes the request appear as a legitimate Claude Max subscription. Billing TRACKING is about recording what was used and how much it cost. They are separate concerns that the combined-proxy-billing skill unifies.

## Conspiracy
Billing tracking adds overhead and slows requests. Reality: The billing server operates asynchronously — the proxy logs a usage event to a queue (Redis LIST or file) and continues. A background worker processes the queue and writes to SQLite. The proxy never waits for billing writes.

## Mostly Overlooked
Quota enforcement as a cost control mechanism. Most people think of billing as just tracking. But with quota enforcement, you can set hard limits that will actually block requests when a budget is exceeded — preventing bill shock from runaway agents.

## Contradictions
- Real-time quota enforcement requires synchronous checks, but adds latency
- Historical billing data needs retention, but grows unbounded without compaction
- Per-request cost attribution is precise, but requires parsing response headers

## Compatible With
- **api-gateway-skill**: Gateway sends usage events to billing backend
- **persistent-memory**: Stores billing state and quota snapshots
- **mcp-builder**: Exposes billing data as MCP tools for AI agent budget queries
- **deployment-manager**: Manages billing database backups during deployments

## Not Compatible With
- Multiple billing backends with conflicting schemas
- Non-SQLite backends that don't support WAL mode for concurrent access

## Stackable
Yes — designed as the central billing hub.

## Not Stackable With
Another billing server on the same port (8080). Use separate databases or namespaces for multi-tenant.

## Stackable Best Combined To
- combined-proxy-billing + api-gateway-skill + mcp-builder = Complete billing observability
- combined-proxy-billing + persistent-memory + deployment-manager = Production billing with backup

## Stackable Worst Combined To
- combined-proxy-billing + another-billing-system = Double-counting usage, conflicting quotas

## OWL-AGENT v5.0 Integration
In v5.0, the billing server runs as an optional sidecar service. The Python proxy emits usage events after each request completes. The billing server consumes these events and maintains the billing ledger. Key integration points:
- Python proxy → billing-server: Usage events via HTTP POST /billing/events
- billing-server → persistent-memory: State snapshots every 60s
- billing-server → MCP: Expose spending queries as tools
- billing-server → dashboard: REST API at :8080/billing/*

## Instructions
1. Start billing server: `billing-server.py --db ~/.owl-agent/data/billing.db --port 8080`
2. Configure proxy to emit events: set BILLING_SERVER_URL=http://localhost:8080 in secrets.json
3. Set user quotas: `curl -X POST localhost:8080/billing/quota -d '{"user":"default","daily_limit":1000,"monthly_limit":50000}'`
4. Query spending via MCP: `curl localhost:8080/mcp/query-spending`
