# Skill Router - Intent-to-Stack Meta-Skill

## Context

Skills are not a list — they are an organization. But an organization without a dispatcher is just a crowd. The Skill Router is the brain stem: it reads the user's intent and automatically selects the right skill or skill stack. This is the difference between having a team and having an organization.

**When to use**: EVERY conversation starts here. Before invoking any individual skill, the router determines the optimal path. If the user's request maps to a known stack, the entire pipeline activates. If it's a single-skill task, only that skill fires.

**What it replaces**: Manual skill selection, guesswork, "which skill should I use?" decisions, forgotten skill combinations.

## Instructions

### Step 1: Classify Intent

Read the user's request and classify it into one of 8 intent domains:

| Intent Domain | Signal Keywords | Primary Stack |
|---------------|----------------|---------------|
| BUILD | "build", "create", "make", "develop", "ship", "launch" | Product Launch |
| WRITE | "write", "content", "blog", "article", "copy", "email" | Content Machine |
| RESEARCH | "research", "investigate", "find out", "analyze", "what is" | Research Pipeline |
| DESIGN | "design", "mockup", "UI", "interface", "prototype" | Design & Deliver |
| DECIDE | "should we", "which option", "compare", "decide", "evaluate" | Reasoning Stack |
| DATA | "data", "spreadsheet", "chart", "financial", "report" | Data Pipeline |
| LEARN | "explain", "teach", "how does", "understand", "learn" | Education Stack |
| AUTOMATE | "automate", "scrape", "extract", "monitor", "track" | Automation Stack |

### Step 2: Select Stack

Map the classified intent to the optimal skill stack. Each stack has a defined handoff chain — skills execute in sequence, each receiving the previous skill's output as context.

```
INTENT → STACK MAPPING (with trigger commands)

BUILD    → /launch  → superpowers → frontend-design → react-best-practices → browser-use → deployment-manager → social-media-manager → humanizer
WRITE    → /content → content-strategy → seo-content-writer → gumroad-pipeline → social-media-manager → humanizer
RESEARCH → /research → deep-research → web-reader → context-compressor → output-formatter → pdf/docx
DESIGN   → /design  → brainstorming → frontend-design → gsap-animations → fullstack-dev → deployment-manager
DECIDE   → /decide  → chain-of-thought → devils-advocate → simulation-sandbox → output-formatter
DATA     → /data    → finance/web-search → xlsx → charts → context-compressor → pdf
LEARN    → /learn   → explained-code → socratic-method → output-formatter → pdf
AUTOMATE → /automate → browser-use → web-reader → contentanalysis → xlsx
```

### Step 3: Handle Multi-Intent Requests

If the user's request spans multiple intents (e.g., "Research X and write a blog post about it"):

1. Identify ALL intent domains present
2. Find the primary intent (usually the action verb)
3. Chain the stacks: primary stack runs first, secondary stacks append their unique skills
4. Deduplicate: if both stacks share a skill (e.g., humanizer), include it once at its latest position

Example: "Research quantum computing and write a blog post"
→ RESEARCH stack (deep-research → web-reader → context-compressor)
→ WRITE stack (content-strategy → seo-content-writer → gumroad-pipeline → social-media-manager → humanizer)
→ Merged: deep-research → web-reader → context-compressor → content-strategy → seo-content-writer → gumroad-pipeline → social-media-manager → humanizer

### Step 4: Handle Ambiguous Intent

If the intent is unclear:
1. Ask ONE clarifying question — never more than one
2. Provide 2-3 options with brief descriptions
3. After the user clarifies, route immediately — no further questions

Example:
User: "I need help with my website"
Router: "Which of these? ① Build a new site (BUILD) ② Fix/design an existing one (DESIGN) ③ Write content for it (WRITE)"

### Step 5: Single-Skill Fast Path

Not every request needs a stack. For simple, focused tasks:
- "Generate an image" → image-generation (no stack)
- "Convert this to PDF" → pdf (no stack)
- "Search for X" → web-search (no stack)
- "Explain this code" → explained-code (no stack)

Rule: If the request has ONE verb and ONE output type, use single-skill fast path.

### Step 6: Execute and Monitor

Once the stack is selected:
1. Execute skills in chain order
2. Each skill receives the previous skill's output as input context
3. If a skill fails (typed error), consult the Error Escalation table
4. After the chain completes, run a quality gate: does the output match the user's original intent?
5. If quality gate fails → re-route with the deviation as new context

## Constraints

1. NEVER ask more than one clarifying question — the router must be fast, not chatty
2. NEVER invoke a skill that is not in the user's installed skills directory (`/home/z/my-project/skills/`)
3. NEVER skip a skill in a chain unless the previous skill's output makes it redundant (and log why)
4. NEVER start a chain without confirming the intent classification with the user (except for obvious cases)
5. ALWAYS prefer a stack over ad-hoc skill selection — stacks are optimized, ad-hoc is not
6. ALWAYS run humanizer as the final skill in any stack that produces written content
7. NEVER re-invoke a skill that already failed with the same input — escalate instead
8. The router MUST log every routing decision for future pattern analysis

## Examples

### Example 1: Clear Intent
```
User: "Launch a SaaS product for freelancers"
Router: Intent = BUILD → Stack = Product Launch → /launch
Executing: superpowers(spec) → frontend-design(UI) → react-best-practices(audit) → browser-use(QA) → deployment-manager(ship) → social-media-manager(announce) → humanizer(polish)
```

### Example 2: Multi-Intent
```
User: "Research the AI agent market and create a report with charts"
Router: Intents = RESEARCH + DATA → Stack = Research Pipeline + Data Pipeline
Merged: deep-research → web-reader → context-compressor → finance(data) → charts(viz) → pdf(output)
```

### Example 3: Ambiguous Intent
```
User: "I need something for my business"
Router: "Which? ① Market research (RESEARCH) ② Financial analysis (DATA) ③ Launch a product (BUILD) ④ Content strategy (WRITE)"
```

### Example 4: Single-Skill Fast Path
```
User: "Convert this document to PDF"
Router: Intent = single action → Skill = pdf (no stack needed)
```

## Error Handling

| Error Type | Code | Action |
|------------|------|--------|
| IntentAmbiguousError | SR-001 | Ask one clarifying question with max 3 options |
| SkillNotInstalledError | SR-002 | Report missing skill, suggest installation command |
| ChainBreakError | SR-003 | Log which skill failed, attempt continuation from next skill |
| MultiIntentConflictError | SR-004 | Prioritize by action verb, defer secondary intents |
| QualityGateFailureError | SR-005 | Re-route with deviation context, max 2 retries |
| CircularDependencyError | SR-006 | Break cycle, log the loop, execute linearized path |
