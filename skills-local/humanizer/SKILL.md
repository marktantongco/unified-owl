# humanizer - Strip AI writing patterns from generated text

## Context
Use this skill every time you generate text that will be read by humans (emails, blog posts, marketing copy, social posts). It strips away detectable AI writing patterns — repetitive structures, overuse of "delve" and "unlock", formulaic transitions — and rewrites the content to sound as if a human wrote it. This is a quality gate, not a standalone workflow — use it as a final pass after seo-content-writer, blog-writer, or social-media-manager.

## Instructions
1. After drafting the final copy, append the command: "Humanize this text: [copy]".
2. The skill runs a classifier to identify AI-hallmark phrases and structures.
3. It rewrites the text while preserving the meaning, but varying sentence length, introducing idioms, and adding natural imperfection.
4. Return the humanized version. If the original line count changes, preserve the key information, not verbatim length.
5. Optionally, return a diff showing what was changed and why.

## Constraints
- Never humanize code, data, or technical specifications.
- Do not alter factual claims; rewriting only affects style, not substance.
- Avoid making the text overly casual; match the original tone (professional, friendly, etc.).
- This is a post-processing step — always run AFTER the primary writing skill, never instead of it.

## Error Handling
All errors are typed and surfaced. Never swallow failures silently.

| Error Type | Code | When | Action |
|-----------|------|------|--------|
| `EmptyInputError` | HZ-001 | No text provided to humanize | Return error: "No input text received. Provide the copy to humanize." |
| `PreservedContentError` | HZ-002 | Factual claim was altered during rewrite | Flag the changed claim, revert it, keep style changes |
| `ToneMismatchError` | HZ-003 | Output tone doesn't match input tone | Re-process with explicit tone constraint, report deviation |
| `CodeCorruptionError` | HZ-004 | Code block or data was modified | Revert code blocks entirely, only humanize prose |

## Examples
1. Input: "We are pleased to announce that our innovative platform leverages advanced AI to unlock unprecedented growth for your business."
   Output: "We just launched something that helps you grow — our new platform uses AI in a way that actually makes sense."

2. Error scenario: Input contains "Revenue grew 47% YoY" and humanizer changes it to "Revenue went up a lot recently."
   → Raises `PreservedContentError(HZ-002)` — reverts to "Revenue grew 47% YoY" and only humanizes surrounding prose.
