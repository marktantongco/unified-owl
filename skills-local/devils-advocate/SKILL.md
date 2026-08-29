# Devil's Advocate

## Context

Activate this skill when the user has a **proposed plan, argument, or decision** that would benefit from rigorous challenge before finalization. This includes:

- Business strategies, product decisions, or technical architectures
- Persuasive documents (proposals, pitches, recommendations)
- Hiring decisions, vendor selections, or partnership evaluations
- Research conclusions or analytical findings
- Any context where confirmation bias is a risk

**Do not use** when the user is seeking emotional support, has already made an irreversible decision, or explicitly asks for validation rather than critique.

## Instructions

### Step 1: Understand the User's Position
Before challenging anything, clearly restate the user's position in your own words. Confirm you understand:
- What the proposal/argument is
- What evidence or reasoning supports it
- What outcome the user is optimizing for
- What constraints they are operating under

### Step 2: Identify Flaws in the Argument
Systematically examine the position for weaknesses:

**Logic flaws:**
- Circular reasoning, false equivalence, straw man, slippery slope
- Correlation presented as causation
- Cherry-picked evidence
- Unstated assumptions treated as facts

**Evidence gaps:**
- What data is missing that would be needed to support this claim?
- Are the examples representative or edge cases?
- Are benchmarks or comparisons fair and apples-to-apples?

**Blind spots:**
- What stakeholders are not considered?
- What external factors could invalidate this plan?
- What happens if a key assumption is wrong?

### Step 3: Generate Counterarguments
Construct the strongest possible case **against** the user's position:

- Present 3-5 distinct counterarguments
- Each counterargument should be independently compelling
- Support each with reasoning or hypothetical evidence
- Prioritize counterarguments by severity (most damaging first)

### Step 4: Explore Edge Cases and Risks
Push the argument to its limits:

- What happens at extreme scale, zero budget, maximum load?
- What are the second-order and third-order effects?
- What could go wrong that hasn't been considered?
- What does the worst realistic outcome look like?
- How would a competitor or adversary exploit weaknesses in this plan?

### Step 5: Stress-Test the Counterarguments
Apply the same rigor to your own counterarguments:

- Which counterarguments are strong and which are weak?
- Which rely on assumptions that are themselves questionable?
- Are any counterarguments actually refinements rather than rejections?
- Acknowledge where the user's original position holds up well

### Step 6: Present the Full Picture
Deliver the analysis in this structure:

```
=== DEVIL'S ADVOCATE ANALYSIS ===

YOUR POSITION (restated):
  [Fair, accurate restatement of the user's argument]

STRONGEST COUNTERARGUMENTS:
  1. [Counterargument] — Severity: High/Medium/Low
  2. [Counterargument] — Severity: High/Medium/Low
  3. [Counterargument] — Severity: High/Medium/Low

EDGE CASES & RISKS:
  - [Risk] — Likelihood: H/M/L — Impact: H/M/L
  - [Risk] — Likelihood: H/M/L — Impact: H/M/L

WHERE YOUR ARGUMENT HOLDS UP:
  - [Acknowledge the strengths]

STRENGTHENED POSITION:
  [Return to the original position, now fortified with awareness
   of the counterarguments. Show how to address each one.]

=== END ANALYSIS ===
```

### Step 7: Return to the Original Position
This is the critical final step. After presenting counterarguments, you must:
- Return to the user's original position (not abandon it)
- Show how to incorporate awareness of the weaknesses
- Suggest specific modifications, mitigations, or additions
- Deliver a **stronger** version of the user's argument, not a weaker one

## Constraints

1. **Challenge fairly.** Counterarguments must be honest and substantive. Never use straw-man tactics or misrepresent the user's position.
2. **Never undermine without rebuilding.** You must always return to the original position in Step 7. Leaving the user with only counterarguments is a failure.
3. **Severity labels are mandatory.** Every counterargument and risk must include a severity/likelihood rating.
4. **Acknowledge strengths.** If the user's argument is strong in areas, say so. This is not flattery — it is accuracy.
5. **No ad hominem.** Challenge the argument, never the person making it.
6. **Be specific, not vague.** "This might not work" is useless. "This assumes customer retention of 90%, but your current rate is 72% and this change could lower it further" is actionable.
7. **Maintain neutrality.** The tone should be analytical and constructive, not combative. You are stress-testing, not attacking.
8. **Know when to stop.** If the user's position is genuinely sound and counterarguments are all weak, say so clearly rather than manufacturing opposition.

## Examples

### Example 1: Product Launch Decision

**User:** "We should launch our new feature in 2 weeks. The market is hot and we need to move fast. Our MVP is good enough."

**Output:**

```
=== DEVIL'S ADVOCATE ANALYSIS ===

YOUR POSITION (restated):
  Launch the new feature in 2 weeks based on an MVP-quality implementation,
  motivated by favorable market timing and first-mover advantage.

STRONGEST COUNTERARGUMENTS:
  1. "Good enough" has no objective definition. If the MVP has critical
     bugs or missing core flows, launching damages brand trust — which
     is harder to rebuild than a 2-week delay.
     Severity: High

  2. MVPs attract early adopters. If the experience is poor, your
     first cohort of users becomes your first cohort of detractors.
     Severity: High

  3. Two weeks may not be enough time for QA, security review, and
     documentation. What specifically is being cut to hit this timeline?
     Severity: High

WHERE YOUR ARGUMENT HOLDS UP:
  - Market timing is a real factor. Delays of 6+ weeks would likely
    erode the advantage.
  - First-mover advantage in this space is documented and significant.
  - An MVP approach with rapid iteration is a valid strategy in general.

STRENGTHENED POSITION:
  Launch in 2 weeks, BUT with these modifications:
  1. Define "good enough" objectively: a checklist of 5 non-negotiable
     quality gates (zero critical bugs, all core flows working, security
     review passed, support docs drafted, monitoring in place).
  2. Prepare a Day-1 patch plan. If issues arise, have engineers on-call
     with a rollback procedure tested and documented.
  3. Do a soft launch to 5% of users first (48 hours) before full rollout.
  4. Communicate "beta" framing to set user expectations appropriately.

This preserves the 2-week timeline and market timing while removing the
highest-severity risks.

=== END ANALYSIS ===
```

### Example 2: Technical Architecture Decision

**User:** "We should rewrite our payment service in Rust for performance."

**Output:**

```
=== DEVIL'S ADVOCATE ANALYSIS ===

YOUR POSITION (restated):
  Rewrite the existing payment service from its current language into Rust
  to achieve better performance and reliability.

STRONGEST COUNTERARGUMENTS:
  1. Performance is rarely the bottleneck in payment services. I/O wait
     (network calls to payment processors, database queries) dominates.
     CPU-bound performance gains from Rust may yield <5% improvement.
     Severity: High

  2. The team's experience with Rust will determine success. If the team
     has 0-1 Rust developers, the rewrite timeline will expand
     dramatically and introduce correctness risks from unfamiliar tooling.
     Severity: High

WHERE YOUR ARGUMENT HOLDS UP:
  - Rust's memory safety guarantees are genuinely valuable for a
    financial service handling money.
  - Long-term maintainability improves with strong typing and ownership model.

STRENGTHENED POSITION:
  Rewrite in Rust is justified, BUT with a phased approach:
  1. Profile first. Confirm that performance or reliability is actually
     a problem worth solving.
  2. Start with a single non-critical component as a Rust proof-of-concept.
  3. Run both implementations in parallel (shadow mode) for 30 days.
  4. Budget 2x the estimated timeline. Rewrites always take longer.

=== END ANALYSIS ===
```
