# Context Compressor

## Context

Activate this skill when the conversation context has grown **long, noisy, or repetitive**, and critical information risks being buried. Use this skill when:

- A conversation has exceeded a length where key details may be lost
- The user asks for a summary of what has been discussed so far
- Context needs to be compressed before passing to another agent or tool
- The user is switching topics and wants to preserve prior decisions
- Working within token-limited environments where efficiency matters

**Do not use** on short conversations where all information is still easily accessible, or when the user explicitly wants the full verbatim context preserved.

## Instructions

### Step 1: Scan for Critical Information
Read through the full context and identify every piece of information that must be preserved with zero loss. Priority categories (in order):

1. **Decisions made** — what was agreed upon and by whom
2. **Action items** — tasks assigned, deadlines, owners
3. **Constraints** — hard limits, requirements, non-negotiables
4. **Key entities** — names, IDs, paths, versions, URLs
5. **Numerical data** — metrics, counts, amounts, thresholds
6. **Temporal markers** — dates, times, deadlines, milestones
7. **Open questions** — items that were raised but not resolved

### Step 2: Extract Key Entities
Create a compact reference of all named entities:

```
Entities:
  - [Project]: Acme Migration v2
  - [People]: Sarah (PM), Dev (lead engineer), Client: XYZ Corp
  - [Systems]: auth-service v3.2, user-db (PostgreSQL 15)
  - [Dates]: Deploy target: 2025-08-15, Review: 2025-08-10
```

### Step 3: Summarize Discussion Progression
Compress the conversation flow into a condensed narrative. For each topic discussed:

- State the topic in one sentence
- State the key points raised (bullet list, max 3 items)
- State the outcome (decision, deferred, or open)

Remove all:
- Acknowledgments ("ok," "got it," "thanks")
- Repeated statements or rephrases of the same point
- Tangential discussions that did not lead to outcomes
- Verbose explanations that were distilled into decisions

### Step 4: Extract Action Items
List every action item found in context:

```
Action Items:
  1. [Owner] Task description — Due: DATE — Status: done/pending/blocked
  2. [Owner] Task description — Due: DATE — Status: done/pending/blocked
```

If no owner or deadline was specified, mark as `[UNASSIGNED]` or `[NO DEADLINE]`.

### Step 5: Identify Open Questions and Risks
List unresolved items that will need future attention:

```
Open Questions:
  - Q1: Description — Raised by: [Person/Context]
  - Q2: Description — Blocked by: [Dependency]

Risks:
  - R1: Description — Likelihood: High/Med/Low — Impact: High/Med/Low
```

### Step 6: Generate the Compressed Context
Assemble the compressed context in this order:

```
=== COMPRESSED CONTEXT ===
Generated: [timestamp]

1. PROJECT OVERVIEW
   [One-paragraph summary of what this project/conversation is about]

2. KEY ENTITIES
   [Compact entity reference]

3. DECISIONS LOG
   [Numbered list of all decisions with brief rationale]

4. ACTION ITEMS
   [Numbered list with owners and deadlines]

5. OPEN QUESTIONS & RISKS
   [List of unresolved items]

6. KEY CONSTRAINTS
   [List of non-negotiable requirements or limits]

=== END COMPRESSED CONTEXT ===
```

### Step 7: Compression Ratio Check
Compare the compressed output to the original context:
- Target: 70-85% reduction in token count
- If the ratio is below 60%, the compression is too aggressive — re-add lost details
- If the ratio is above 90%, the compression is too conservative — remove more noise

## Constraints

1. **Never lose a decision.** If a decision was made, it must appear in the compressed context verbatim or with minimal paraphrasing.
2. **Never lose a number.** All metrics, counts, dates, versions, and thresholds must be preserved exactly as stated.
3. **Never lose an action item.** Every assigned task must be captured, even if incomplete.
4. **Never lose a constraint.** Hard limits and requirements must survive compression intact.
5. **No hallucinated details.** The compressed context must only contain information that was explicitly stated in the original. Do not infer, assume, or fill in gaps.
6. **Label the compression.** Always mark the output as a compressed summary so future readers know they are not seeing the full context.
7. **Preserve attribution.** If a decision was made by a specific person, keep their name attached. Do not anonymize ownership.

## Examples

### Example 1: Software Project Context Compression

**Input:** 3,000-word conversation spanning sprint planning, architecture discussion, and bug triage.

**Output:**

```
=== COMPRESSED CONTEXT ===
Generated: 2025-07-18T14:30:00Z

1. PROJECT OVERVIEW
   Migrating auth-service from monolith to standalone microservice.
   Currently in Phase 2 of 3. Sprint 14 in progress.

2. KEY ENTITIES
   - [Services]: auth-service (current: v3.2, target: v4.0), user-db, session-store
   - [People]: Priya (Tech Lead), Marcus (Backend), Lena (QA)
   - [Dates]: Phase 2 complete: 2025-08-01, Phase 3 start: 2025-08-04
   - [Versions]: Go 1.22, PostgreSQL 15, Redis 7.2

3. DECISIONS LOG
   1. [Decided] Use JWT with rotating refresh tokens (not session-based).
      Rationale: Stateless design better suits multi-region deployment.
   2. [Decided] Keep user-db as shared dependency (not replicated).
      Rationale: Replication overhead not justified for read-heavy auth pattern.
   3. [Decided] Defer RBAC migration to Phase 3.
      Rationale: Current scope already at capacity.

4. ACTION ITEMS
   1. [Marcus] Implement JWT refresh rotation — Due: 2025-07-22 — Status: pending
   2. [Lena] Write integration tests for token expiry flow — Due: 2025-07-24 — Status: pending
   3. [Priya] Update API gateway routing config — Due: 2025-07-25 — Status: blocked

5. OPEN QUESTIONS & RISKS
   - Q1: Should refresh tokens be stored in Redis or DB?
     Raised by: Marcus — Blocked by: Priya decision needed
   - R1: JWT secret rotation strategy not yet defined.
     Likelihood: Medium — Impact: High

6. KEY CONSTRAINTS
   - Must maintain backward compatibility with monolith during Phase 2
   - Zero-downtime migration required
   - P99 latency must remain under 50ms for auth endpoints
   - Compliance: tokens must not contain PII

=== END COMPRESSED CONTEXT ===
```

### Example 2: Research Discussion Compression

**Input:** 2,000-word conversation about evaluating three database options for a new product.

**Output:**

```
=== COMPRESSED CONTEXT ===
Generated: 2025-07-18T15:00:00Z

1. PROJECT OVERVIEW
   Evaluating databases for new real-time analytics product.
   Requirements: sub-second query latency, horizontal scaling, cost-effective under 10TB.

2. KEY ENTITIES
   - [Options]: ClickHouse, Apache Druid, Snowflake
   - [Metrics]: Expected data volume: 2TB/year, Query throughput: 500 QPS, Budget: $5k/mo

3. DECISIONS LOG
   1. [Decided] ClickHouse is the leading candidate.
      Rationale: Best latency-to-cost ratio for our query patterns.
   2. [Decided] Snowflake eliminated due to cost at scale ($12k/mo estimated at 5TB).
   3. [Decided] Druid kept as fallback if JOIN performance is needed later.

4. ACTION ITEMS
   1. [Data Team] Run ClickHouse POC with 500GB sample dataset — Due: 2025-07-25
   2. [CTO] Approve POC infrastructure budget ($800) — Status: pending

5. OPEN QUESTIONS & RISKS
   - Q1: ClickHouse materialized view support for our specific aggregation patterns.
   - R1: ClickHouse operational complexity — team has no prior experience.

6. KEY CONSTRAINTS
   - Must not exceed $5,000/month at full scale (10TB)
   - Must support real-time ingestion (sub-5 second delay)
   - Must integrate with existing Kafka pipeline

=== END COMPRESSED CONTEXT ===
```
