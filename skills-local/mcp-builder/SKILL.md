# MCP Builder

## Context

Use this skill when the user wants to build a Model Context Protocol (MCP) server. MCP servers expose tools, resources, and prompts that AI agents can invoke. Covers the full lifecycle from planning through evaluation.

**Trigger phrases:** "build an MCP server," "create an MCP tool," "MCP integration," "add MCP support."

---

## Instructions

### Phase 1: Research & Planning

1. **Clarify scope.** For each tool document: name (snake_case), description, required inputs with types, output shape, and behavior hints (readOnly/destructive/idempotent).
2. **Choose stack:** TypeScript (`@modelcontextprotocol/sdk`) for complex/HTTP servers; Python (`fastmcp`) for data pipelines and rapid prototyping.
3. **Choose transport:** `stdio` for local CLI usage (client launches server as subprocess); HTTP (Streamable) for remote/multi-client deployments.
4. **Design schemas** using JSON Schema. Every parameter must have `type`, `description`, and constraints (`enum`, `minLength`, `pattern`).

### Phase 2: Implementation

5. **Initialize:**
   ```bash
   # TypeScript
   mkdir my-mcp && cd my-mcp && npm init -y && npm install @modelcontextprotocol/sdk zod
   # Python
   pip install fastmcp
   ```
6. **Project structure:** `src/index.ts` (entry), `src/tools/*.ts` (one file per tool), `src/schemas/*.ts` (Zod definitions).
7. **Register tools with annotations:**
   ```typescript
   server.tool("tool_name", "Description", { param: z.string().describe("...") },
     async ({ param }) => ({ content: [{ type: "text", text: "Result" }] }),
     { readOnlyHint: true, destructiveHint: false, idempotentHint: true }
   );
   ```
8. **Error handling:** Return `{ content: [{ type: "text", text: "Error: ..." }], isError: true }`. Never throw unhandled.
9. Add **resources** (static data) and **prompts** (reusable templates) as optional.

### Phase 3: Review & Testing

10. **Lint/type-check:** `tsc --noEmit` or `mypy`.
11. **Test with MCP Inspector:** `npx @modelcontextprotocol/inspector node dist/index.js`
12. **Edge cases:** empty inputs, missing fields, large payloads.
13. **Validate schemas** against JSON Schema spec.

### Phase 4: Evaluation

14. **Checklist:** All tools have annotations and descriptions. Output uses `{ content: [...] }` format. Errors use `isError: true`. No hardcoded secrets. Inspector passes all tests.

---

## Constraints

- Every tool MUST have `description` and hints (`readOnlyHint`, `destructiveHint`, `idempotentHint`).
- Tool names MUST be lowercase snake_case, max 64 characters.
- Input schemas MUST be JSON Schema format (Zod acceptable as builder).
- Output MUST use `content` array format. Never return raw strings.
- Errors MUST use `isError: true`. Never throw unhandled exceptions.
- NEVER expose destructive ops without `destructiveHint: true`.
- NEVER hardcode secrets. Always use environment variables.
- TypeScript MUST compile with `strict: true`. Python MUST type-hint all functions.

---

## Examples

### Example 1: Weather Server (TypeScript, stdio)

```
Tools:
  get_weather (readOnly, not destructive, idempotent)
    Input: { city: string, units?: "celsius"|"fahrenheit" }
    Output: { content: [{ type: "text", text: "Paris: 22C, Partly Cloudy" }] }
  get_forecast (readOnly, not destructive, idempotent)
    Input: { city: string, days: 1..7 }
    Output: { content: [{ type: "text", text: "<JSON forecast>" }] }
```

### Example 2: File Ops Server (Python, HTTP)

```
Tools:
  read_file (readOnly, not destructive, idempotent)
    Input: { path: string }  ->  Output: file contents
  write_file (not readOnly, destructive, idempotent)
    Input: { path: string, content: string }  ->  Output: confirmation
  list_directory (readOnly, not destructive, idempotent)
    Input: { path: string }  ->  Output: JSON array of entries
```
