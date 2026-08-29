# Find Skills

---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities.
---

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## When to Use This Skill

Use this skill when the user:
- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows

## Skills CLI

The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem.

**Key commands:**
- `npx skills find [query]` - Search for skills interactively or by keyword
- `npx skills add <package>` - Install a skill from GitHub or other sources
- `npx skills check` - Check for skill updates
- `npx skills update` - Update all installed skills

**Browse skills at:** https://skills.sh/

## Workflow

### Step 1: Understand What They Need
Identify the domain, specific task, and whether a skill likely exists.

### Step 2: Check the Leaderboard First
Check https://skills.sh/ to see if a well-known skill already exists for the domain.

### Step 3: Search for Skills
Run: `npx skills find [query]`

### Step 4: Verify Quality Before Recommending
Check: install count (1K+ preferred), source reputation, GitHub stars.

### Step 5: Present Options
Show: skill name, what it does, install count, install command, learn-more link.

### Step 6: Offer to Install
```bash
npx skills add <owner/repo@skill> -g -y
```

## Common Skill Categories

| Category        | Example Queries                          |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| Documentation   | docs, readme, changelog, api-docs        |
| Code Quality    | review, lint, refactor, best-practices   |
| Design          | ui, ux, design-system, accessibility     |
