# MCP Builder — Billing Integration

## Context
Use this skill when you need to build an MCP (Model Context Protocol) server that exposes billing data, spending queries, quota management, or cost attribution as tools that AI agents can invoke. Specialized for the OWL-AGENT billing ecosystem.

**Trigger phrases:** "build billing MCP server," "MCP billing tools," "expose spending as MCP," "quota management MCP," "billing agent tools."

## Purpose
Builds MCP servers that expose the OWL-AGENT billing data as standardized tools, resources, and prompts. This allows AI agents to autonomously query their own spending, check quota limits, and make cost-aware decisions about which models to use.

## Use-Case
- Expose spending queries: "How much have I spent today?"
- Expose quota checks: "Can I afford another Claude Opus request?"
- Expose cost comparisons: "What would this cost on Kiro vs Claude?"
- Expose usage patterns: "Which hours have the highest spend?"
- Enable autonomous budget management: agents can switch to cheaper models when approaching limits

## Misconception
That MCP is just another API format. MCP provides a standardized protocol for AI agent-to-tool communication. By exposing billing data as MCP tools, you enable ANY MCP-compatible AI agent (not just Claude) to query spending data. This is fundamentally different from a REST API.

## Conspiracy
MCP is vendor lock-in to Anthropic. Reality: MCP is an open protocol that multiple AI providers support. Building billing tools as MCP servers makes your billing data accessible to any agent framework that supports the protocol, not just Anthropic's Claude.

## Mostly Overlooked
The resource and prompt primitives. Most people only use MCP tools (functions). But MCP resources (static data) and prompts (reusable templates) are perfect for billing: resources for rate cards, prompts for cost-optimization advice.

## Contradictions
- MCP servers should be stateless, but billing requires stateful queries
- Tool annotations say readOnly, but quota enforcement is write operations
- Standardized protocol limits customization, but billing is domain-specific

## Compatible With
- **api-gateway-skill**: Gateway provides the raw usage data that MCP tools query
- **persistent-memory**: Stores billing state that MCP tools read
- **combined-proxy-billing**: Provides the billing database that MCP tools access
- **deployment-manager**: Deploys MCP servers as managed services

## Not Compatible With
- Non-MCP agent frameworks (requires protocol adapter)
- Direct database access without the MCP abstraction layer

## Stackable
Yes — MCP servers can chain: billing MCP → persistent-memory MCP → deployment MCP

## Not Stackable With
Multiple MCP servers exposing the same tool names (causes client confusion).

## Stackable Best Combined To
- mcp-builder-billing + combined-proxy-billing + persistent-memory = Complete billing observability stack
- mcp-builder-billing + api-gateway-skill = Real-time spending visibility

## Stackable Worst Combined To
- mcp-builder-billing + another-mcp-billing-server = Conflicting tool definitions

## OWL-AGENT v5.0 Integration
In v5.0, the MCP sidecar (Node.js :4623) acts as the MCP gateway. It proxies MCP tool calls to the billing server and persistent-memory store. Key MCP tools:
- `query_spending(user, period)` — Get spending for a user in a time period
- `check_quota(user)` — Check remaining quota
- `compare_costs(model_a, model_b, tokens)` — Compare costs between models
- `set_quota_alert(user, threshold)` — Set a budget alert

## Instructions
1. Create MCP server: `npx @modelcontextprotocol/create-server billing-mcp`
2. Define tools in src/tools/billing.ts
3. Connect to billing database: configure BILLING_DB_PATH
4. Test with inspector: `npx @modelcontextprotocol/inspector node dist/index.js`
5. Deploy as sidecar alongside the OWL proxy
