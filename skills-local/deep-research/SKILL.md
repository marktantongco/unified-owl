---
name: deep-research
description: Comprehensive multi-source research workflow that goes beyond simple web search. Uses parallel search agents, source verification, cross-referencing, and structured reporting. Use when the user needs thorough research on any topic, market analysis, competitive intelligence, or academic literature review.
author: skills-sh
version: "1.0"
tags:
  - research
  - analysis
  - deep-search
  - verification
  - multi-source
---

# Deep Research Skill

## When to Use

- User needs comprehensive research, not just quick answers
- Market analysis, competitive intelligence, or industry trends
- Academic or technical literature review
- Fact-checking claims across multiple sources
- Any question requiring depth over speed

## Research Workflow

### Phase 1: Scope Definition
Before searching, clarify:
1. **Research question**: What exactly needs to be answered?
2. **Depth level**: Quick scan (3-5 sources), standard (8-12 sources), deep (15+ sources)
3. **Timeframe**: Current only, historical, or both
4. **Source types**: Academic, industry, news, primary data
5. **Output format**: Summary, detailed report, comparison table

### Phase 2: Parallel Search
Launch multiple search queries simultaneously:
- **Broad query**: General topic overview
- **Specific queries**: Targeted sub-questions
- **Contrarian query**: Opposing viewpoints or criticism
- **Recent query**: Latest developments (last 30 days)
- **Authoritative query**: Site: restricted to trusted domains

### Phase 3: Source Triage
Evaluate each source:
| Criteria | Weight | Score (1-5) |
|----------|--------|-------------|
| Authority/credibility | 30% | _ |
| Recency | 20% | _ |
| Relevance to question | 30% | _ |
| Depth of coverage | 20% | _ |

Keep only sources scoring 3.5+ average.

### Phase 4: Cross-Reference
- Verify key claims across at least 2 independent sources
- Flag contradictions between sources
- Note consensus vs. disputed points
- Identify gaps in available information

### Phase 5: Structured Report
```markdown
# Research Report: [Topic]

## Executive Summary
[2-3 paragraph overview of findings]

## Key Findings
1. [Finding 1] — Confidence: High/Medium/Low
2. [Finding 2] — Confidence: High/Medium/Low
...

## Detailed Analysis
### [Sub-topic 1]
[Analysis with source citations]

### [Sub-topic 2]
[Analysis with source citations]

## Contradictions & Gaps
- [What sources disagree on]
- [What information is missing]

## Sources
| # | Source | Type | Date | Credibility |
|---|--------|------|------|-------------|
| 1 | ... | ... | ... | High/Med/Low |
```

## Best Practices

- Always search with multiple query formulations
- Verify factual claims across 2+ independent sources
- Explicitly state confidence level for each finding
- Note what you could NOT find (gaps are valuable data)
- Distinguish between facts, expert opinions, and speculation
- For market/industry data, always check original sources, not summaries
