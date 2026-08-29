---
name: chain-of-thought
description: Enables explicit step-by-step reasoning to solve complex problems. Use when the user needs structured thinking, multi-step analysis, logical deduction, or wants the AI to show its reasoning process. Improves accuracy on math, logic, coding, and complex decision-making tasks.
author: ai-skills-library
version: "1.0"
tags:
  - reasoning
  - thinking
  - analysis
  - logic
  - problem-solving
---

# Chain of Thought Skill

## When to Use

- Complex multi-step problems requiring logical reasoning
- Math, science, or logic puzzles
- Decision-making with multiple factors
- Debugging or root cause analysis
- Any task where showing reasoning improves accuracy

## Instructions

When this skill is activated, follow these steps:

### 1. Decompose the Problem
Break the user's question into smaller, manageable sub-problems. Identify what information is needed and what steps are required.

### 2. Show Each Reasoning Step
For each sub-problem:
- State the step number and what you're solving
- Show your reasoning explicitly
- Note any assumptions made
- Flag uncertainty clearly

### 3. Connect Steps Logically
Each step should build on the previous one. Make the logical chain visible:
```
Step 1 → (because) → Step 2 → (therefore) → Step 3
```

### 4. Verify Intermediate Results
After each step, briefly check: Does this result make sense? If not, backtrack and reconsider.

### 5. Synthesize Final Answer
Combine all intermediate results into a clear, complete answer. Summarize the reasoning chain.

## Output Format

```
## Reasoning Chain

**Step 1**: [What you're solving]
- Analysis: [Your reasoning]
- Result: [Intermediate conclusion]

**Step 2**: [What you're solving]
- Analysis: [Your reasoning, referencing Step 1 result]
- Result: [Intermediate conclusion]

...

**Final Answer**: [Synthesis of all steps]
**Confidence**: [High/Medium/Low] — [Reason for confidence level]
```

## Best Practices

- Never skip steps, even if they seem obvious
- Use "Let me think about this step by step" to activate deep reasoning
- When uncertain, explicitly state assumptions and their impact
- For numerical problems, show all calculations
- For logical problems, state the inference rules used
