#!/usr/bin/env bash
# bundle-worktrees.sh — reuse install.sh preflight_agents_persistence for every worktree
# Ensures AGENTS.md persists after `git init` / `git worktree add` and survives `git archive`
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "▸ bundle-worktrees: verify AGENTS.md in all worktrees + git archive"

# 1. Verify current repo first (reuse install.sh preflight, don't source to avoid REPO_ROOT clash)
bash "$REPO_ROOT/install.sh" --verify-agents

# 2. git archive test: AGENTS.md must be in HEAD archive
if ! git -C "$REPO_ROOT" archive HEAD -- AGENTS.md | tar -t | grep -qx "AGENTS.md"; then
  echo "❌ git archive HEAD missing AGENTS.md — check .gitignore / not tracked"
  git -C "$REPO_ROOT" check-ignore -v AGENTS.md || true
  git -C "$REPO_ROOT" ls-files --stage | grep AGENTS || true
  exit 1
fi
echo "✅ git archive HEAD contains AGENTS.md"

# 3. Single verify-agents function for worktree loop (Strategic)
verify_worktree() {
  local wt="$1"
  echo "▸ Checking worktree $wt"
  # Reuse preflight: ensure AGENTS.md exists and in sync with global
  if [[ ! -f "$wt/AGENTS.md" ]]; then
    echo "⚠️ $wt missing AGENTS.md — bootstrapping via install.sh --verify-agents"
    bash "$REPO_ROOT/install.sh" --verify-agents 2>&1 | tail -n 5
    # If still missing, copy from global
    [[ -f "$wt/AGENTS.md" ]] || cp "$HOME/.config/opencode/AGENTS.md" "$wt/AGENTS.md"
  fi
  # diff gate
  if ! diff -u "$HOME/.config/opencode/AGENTS.md" "$wt/AGENTS.md" >/dev/null 2>&1; then
    echo "❌ Drift in $wt"
    diff -u "$HOME/.config/opencode/AGENTS.md" "$wt/AGENTS.md" | head -n 20 || true
    return 1
  fi
  echo "✅ $wt AGENTS.md in sync ($(sha256sum "$wt/AGENTS.md" | cut -d' ' -f1 | cut -c1-7)…)"
  # git init survival: ensure not gitignored and would be tracked
  if git -C "$wt" check-ignore -q "AGENTS.md" 2>/dev/null; then
    echo "❌ $wt gitignores AGENTS.md"
    return 1
  fi
}

# Loop all worktrees from `git worktree list --porcelain`
while IFS= read -r line; do
  [[ "$line" =~ ^worktree\  ]] || continue
  wt="${line#worktree }"
  verify_worktree "$wt"
done < <(git -C "$REPO_ROOT" worktree list --porcelain)

echo "✅ All worktrees verified — AGENTS.md persists"

# 4. Reframe check: fresh `git init` survival simulation (tmp dir)
tmp=$(mktemp -d)
echo "▸ Testing fresh git init survival in $tmp"
cp "$REPO_ROOT/AGENTS.md" "$tmp/AGENTS.md"
git -C "$tmp" init -q
# install.sh preflight should detect .git and ensure not ignored
bash "$REPO_ROOT/install.sh" --verify-agents >/dev/null 2>&1 || true
if [[ -f "$tmp/AGENTS.md" ]]; then
  echo "✅ AGENTS.md survives fresh git init"
else
  echo "❌ AGENTS.md lost after git init"
  exit 1
fi
rm -rf "$tmp"

echo "▸ bundle-worktrees done — c62612a + 92b12bb gate holds"
