# Skill Security Scanner

---
name: skill-scanner
description: Scan agent skills for security issues. Use when asked to "scan a skill", "audit a skill", "review skill security", or assess whether an agent skill is safe to install. Checks for prompt injection, malicious scripts, excessive permissions, secret exposure, and supply chain risks.
metadata:
  author: getsentry
  version: "1.0.0"
---

# Skill Security Scanner

Scan agent skills for security issues before adoption. Detects prompt injection, malicious code, excessive permissions, secret exposure, and supply chain risks.

## Workflow

### Phase 1: Input & Discovery
Determine the scan target:
- User provides a skill directory path
- User names a skill, look for it under `skills/<name>/`
- User says "scan all skills" — discover all `*/SKILL.md` files

### Phase 2: Static Scan
Run automated pattern detection for known malicious patterns.

### Phase 3: Frontmatter Validation
- Required fields: `name` and `description` must be present
- Name consistency: `name` field should match directory name
- Tool assessment: Review `allowed-tools` — is Bash justified?
- Description quality: Does the description match what instructions actually do?

### Phase 4: Prompt Injection Analysis
Review for injection patterns. Critical distinction: a security skill that lists injection patterns is documenting threats, not attacking.

### Phase 5: Behavioral Analysis
- Description vs. instructions alignment
- Config/memory poisoning
- Scope creep
- Information gathering
- Structural attacks (symlinks, frontmatter hooks, test files)

### Phase 6: Script Analysis
- Data exfiltration: external URL calls with data
- Reverse shells: socket connections with redirected I/O
- Credential theft: reading SSH keys, .env files
- Dangerous execution: eval/exec with dynamic input

### Phase 7: Supply Chain Assessment
- Trusted domains: GitHub, PyPI, official docs
- Untrusted domains: unknown domains, URL shorteners
- Remote instruction loading: high risk

### Phase 8: Permission Analysis
- Least privilege: Are all granted tools actually used?
- Risk level tier system

## Output Format

```markdown
## Skill Security Scan: [Skill Name]

### Summary
- **Findings**: X (Y Critical, Z High, ...)
- **Risk Level**: Critical / High / Medium / Low / Clean

### Findings
#### [SKILL-SEC-001] [Finding Type] (Severity)
- **Location**: file:line
- **Confidence**: High/Medium/Low
- **Category**: Prompt Injection / Malicious Code / Excessive Permissions / Secret Exposure / Supply Chain
- **Issue**: What was found
- **Risk**: What could happen
- **Remediation**: How to fix

### Assessment
Safe to install / Install with caution / Do not install
```
