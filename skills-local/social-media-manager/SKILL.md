# social-media-manager - Multi-platform social content execution

## Context
This skill turns a single idea into platform-appropriate social media posts. Use it when you need to maintain a consistent brand presence across LinkedIn, Twitter/X, Instagram, and TikTok. This is the EXECUTION layer — use content-strategy for the planning layer, and use marketing-mode for the strategic positioning layer. This skill generates the actual posts.

## Instructions
1. Provide the core message, audience persona, and any key dates or campaigns.
2. The skill generates a content calendar: one post per platform per day, formatted according to each platform's best practices (character limits, hashtag density, visual requirements).
3. For each post, it suggests the copy, calls to action, and a description of the ideal visual.
4. It also outputs a "content pillars" report showing the distribution of themes (e.g., 40% educational, 30% behind-the-scenes, 20% promotional, 10% curated).
5. At the end, you get a calendar markdown file ready for your scheduling tool.
6. After generating all posts, run the humanizer skill as a final pass to strip AI patterns.

## Constraints
- Never recycle the exact same text across platforms; adapt to the channel.
- All posts must sound like one brand voice, not multiple personas.
- Include at least one UGC (user-generated content) or interaction post per week.
- Do not generate more than 30 days of content at once to avoid staleness.
- Always respect platform-specific character limits (Twitter: 280, LinkedIn: 3000, etc.).

## Error Handling
All errors are typed and surfaced. Never swallow failures silently.

| Error Type | Code | When | Action |
|-----------|------|------|--------|
| `MissingPersonaError` | SM-001 | No audience persona provided | Halt and prompt: "Who is the target audience?" |
| `PlatformLimitError` | SM-002 | Generated post exceeds platform char limit | Auto-truncate with ellipsis, flag which post was cut |
| `BrandVoiceConflictError` | SM-003 | Posts across platforms don't match brand voice | Regenerate conflicting posts with shared voice reference |
| `CalendarGapError` | SM-004 | Days with no content scheduled | Fill gaps with evergreen/curated content, flag as auto-filled |
| `VisualMissingError` | SM-005 | Post requires visual but no description generated | Generate visual description, flag for review |

## Examples
1. Input: "We're launching a new eco-friendly water bottle. Persona: outdoor enthusiasts. Week of Earth Day."
   Output: 7 LinkedIn posts (professional, stats-focused), 7 Twitter threads (conversational), 7 Instagram carousels (visual storytelling), 7 TikTok scripts (hook-based).

2. Error scenario: Generated Twitter post is 312 characters (over 280 limit).
   → Raises `PlatformLimitError(SM-002)` — auto-truncated to 277 chars + "...", flagged for review.
