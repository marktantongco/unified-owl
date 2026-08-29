#!/usr/bin/env bash
# Compress worktree + main bundle
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER="${1:-1.0.0}"
OUT="unified-owl-v${VER}.tar.gz"
echo "Compressing $ROOT → $OUT (excludes venv, .git, __pycache__, node_modules)"
tar -czf "$ROOT/../$OUT" --exclude=venv --exclude=.git --exclude=__pycache__ --exclude=node_modules --exclude=.next --exclude=out --exclude=*.pyc --exclude=*.bak -C "$(dirname "$ROOT")" "$(basename "$ROOT")"
sha256sum "$ROOT/../$OUT" | tee "$ROOT/../$OUT.sha256"
echo "Done: $ROOT/../$OUT"
# Worktrees
if git -C "$ROOT" worktree list 2>/dev/null | grep -q "worktree"; then
  echo "Worktrees detected:"
  git -C "$ROOT" worktree list
  for wt in $(git -C "$ROOT" worktree list --porcelain | grep "^worktree" | cut -d' ' -f2); do
    base=$(basename "$wt")
    tar -czf "$ROOT/../${base}.tgz" --exclude=venv --exclude=.git --exclude=__pycache__ -C "$(dirname "$wt")" "$base" 2>/dev/null || true
    sha256sum "$ROOT/../${base}.tgz" 2>/dev/null | tee -a "$ROOT/../$OUT.sha256" || true
  done
fi
