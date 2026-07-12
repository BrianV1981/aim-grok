# MERGE ORDERS — P2 stack (Operator authorized via aim-grok orchestrator)

**You execute. Orchestrator does not merge.**

Re-audit **PASSED** on all six PRs (#86–#91). Amends to #87/#89/#91 accepted.

## Strict merge order (do not reorder)

1. **PR #86** (issue #83) — path / worktree root  
2. **PR #88** (issue #82) — Node heap 8192  
3. **PR #90** (issue #80) — docs  
4. **PR #91** (issue #85) — traceback  
5. **PR #87** (issue #84) — CI installer checks  
6. **PR #89** (issue #81) — prune-remote (last)

## How to merge each PR

Prefer squash merge + delete head branch (match prior P0/P1 style):

```bash
gh pr merge <N> --squash --delete-branch
```

If a PR is not mergeable (conflicts):

1. `gh pr checkout <N>` or work in the fix/issue-* worktree  
2. Rebase onto latest `main`: `git fetch origin && git rebase origin/main`  
3. Resolve conflicts carefully (especially `aim_cli.py` across #86 / #91 / #89)  
4. `git push --force-with-lease` only on the **feature** branch  
5. Re-run `gh pr merge <N> --squash --delete-branch`  
6. Do **not** force-push `main`

After each successful merge: `git checkout main && git pull origin main` before the next PR if you need a clean tree.

## Do NOT

- Merge out of order  
- Run `aim prune-remote --confirm` as part of this order (tool ships in #89; cleanup is a later Operator task)  
- Touch aim-grok  
- Open new feature work until this stack is fully merged

## When finished — status to aim-grok

```
1. AGREED — merged PR #s in order
2. Validation — gh pr list (no open P2), git log origin/main -10, CI if green
3. QUESTIONS if any
```

Start with **PR #86** immediately.
— Grok orchestrator @ aim-grok
