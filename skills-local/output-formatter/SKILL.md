# Output Formatter

## Context

Activate this skill when the user requires **structured, well-formatted output** or when the response format matters as much as the content. Use this skill when:

- The user requests a specific output format (JSON, table, markdown, etc.)
- The response will be consumed by another system or tool
- The user needs data presented in a scannable, structured way
- Generating reports, documentation, API responses, or configuration files
- Any context where formatting inconsistencies would reduce clarity or break tooling

**Do not use** for informal conversational responses where rigid formatting would feel unnatural or counterproductive.

## Instructions

### Step 1: Determine the Output Format
Assess the content type and user request to select the appropriate format:

| Content Type | Recommended Format |
|---|---|
| Structured data / API payloads | JSON |
| Comparisons / metrics / features | Markdown table |
| Prose with structure | Markdown with headings |
| Code snippets | Fenced code blocks with language tag |
| Mixed content | Combination with clear separators |
| Configuration / data files | YAML, TOML, or JSON as appropriate |

### Step 2: Apply Markdown Rules
When using markdown:

**Heading hierarchy:**
- Use `#` for the document title (only once, at the top)
- Use `##` for major sections
- Use `###` for subsections
- Never skip levels (e.g., `#` directly to `###`)
- Do not use more than 3 heading levels in a single response unless the document is long-form

**Lists:**
- Use `-` for unordered lists (not `*` or `+`)
- Use `1.` for ordered lists
- Nested lists: indent 2 spaces per level
- Keep list items to one line where possible; break long items across lines

**Emphasis:**
- Use `**bold**` for key terms, labels, and emphasis
- Use `` `backticks` `` for inline code, variable names, and technical terms
- Never use `_underscores_` for emphasis (can conflict with markdown in some renderers)

**Horizontal rules:**
- Use `---` to separate major sections
- Do not use horizontal rules between every paragraph

### Step 3: Apply JSON Rules
When producing JSON:

- Validate that the output is parseable JSON (no trailing commas, no comments, proper quoting)
- Use consistent indentation (2 spaces, not tabs)
- Quote all keys — never use unquoted keys
- Use `null` for missing values, never omit the key
- For arrays of objects, ensure every object has the same keys in the same order
- Wrap in a fenced code block with `json` language tag

### Step 4: Apply Table Rules
When producing markdown tables:

- Always include a header row
- Always include a separator row (`|---|---|`)
- Align columns logically: numbers right-aligned, text left-aligned
- Keep cell content short — tables are for scanning, not reading
- Use `N/A` or `—` for empty cells, never leave them blank
- Limit to 5-7 columns maximum for readability
- For wide tables, consider splitting into multiple focused tables

### Step 5: Apply Code Block Rules
When producing code:

- Always use fenced code blocks with triple backticks
- Always include the language tag (e.g., ```python, ```bash, ```json)
- For multi-line code, ensure consistent indentation
- Add brief comments for non-obvious logic
- Keep code examples minimal and focused — don't paste entire files
- When showing diffs or changes, clearly mark what is new vs. existing

### Step 6: Final Validation
Before outputting, run through this checklist:
- Does the format match what the user requested?
- Are all headings, tables, and code blocks properly closed?
- Is the hierarchy consistent (no skipped heading levels)?
- Is the JSON parseable (if applicable)?
- Would a machine be able to consume this without errors?

## Constraints

1. **No mixed formatting within a single element.** A table cell must not contain a code block. A list item must not contain a nested table unless explicitly requested.
2. **Consistent whitespace.** Use the same indentation style throughout. No mixed tabs and spaces.
3. **No raw HTML unless explicitly requested.** Stick to standard markdown syntax.
4. **JSON must always be valid.** Invalid JSON is never acceptable — validate before outputting.
5. **Tables must always have headers.** Headerless tables are forbidden.
6. **Code blocks must always have a language tag.** Untagged code blocks are forbidden.
7. **Respect the user's format request.** If the user says "give me JSON," give JSON — not markdown wrapping JSON. Format selection is user-driven, not agent-driven.
8. **Length discipline.** Use formatting to reduce verbosity, not increase it. If a table replaces a 20-line list, that is the correct outcome.

## Examples

### Example 1: Structured API Response

**User:** "Give me a JSON schema for a user profile endpoint."

**Output:**

```json
{
  "endpoint": "/api/v1/users/{id}/profile",
  "method": "GET",
  "response": {
    "schema": {
      "id": "string (UUID)",
      "email": "string",
      "display_name": "string",
      "avatar_url": "string (URL, nullable)",
      "role": "string (enum: admin, editor, viewer)",
      "created_at": "string (ISO 8601)",
      "updated_at": "string (ISO 8601)",
      "metadata": {
        "bio": "string (max 500 chars)",
        "location": "string (nullable)",
        "website": "string (URL, nullable)"
      }
    }
  },
  "errors": {
    "404": "User not found",
    "401": "Authentication required",
    "403": "Insufficient permissions"
  }
}
```

### Example 2: Feature Comparison Table

**User:** "Compare Redis, Memcached, and DynamoDB DAX for caching."

**Output:**

| Feature | Redis | Memcached | DynamoDB DAX |
|---|---|---|---|
| **Data types** | Strings, lists, sets, hashes, streams | Strings only | DynamoDB items |
| **Persistence** | Optional (RDB/AOF) | None (in-memory only) | Transparent (DynamoDB-backed) |
| **Replication** | Primary-replica | None | Managed by AWS |
| **Max memory** | Limited by available RAM | Limited by available RAM | Tied to DynamoDB table |
| **Latency (P99)** | <1ms | <1ms | ~1-3ms |
| **Best for** | Complex caching, pub/sub, session store | Simple key-value, LRU caching | DynamoDB-native workloads |
