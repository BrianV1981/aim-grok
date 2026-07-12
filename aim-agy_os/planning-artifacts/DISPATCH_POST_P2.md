# POST-P2 ORDERS — aim-agy (Operator authorized via orchestrator)

**Merge stack CONFIRMED** by orchestrator: PRs #86–#89 order on `origin/main`, issues #80–#85 CLOSED, 0 open PRs for this sprint. Well done.

## Next objective for YOU (aim-agy)

### 1. Sprint close-out (do now)
1. `git checkout main && git pull origin main` — sync local main to `947c538` (or current tip).
2. Remove any leftover local worktrees for issues 80–85 / 83 etc.:
   `git worktree list` then `git worktree remove` stale paths; `git worktree prune`.
3. Delete local `fix/issue-8*` branches if still present (merged already).
4. **Do NOT** run `aim prune-remote --confirm` unless Operator explicitly orders bulk remote delete later. Dry-run only is fine: `aim prune-remote`.

### 2. Stand down from new feature work
P0/P1/P2 hygiene from the grok audit is **complete**. Do **not** invent new tickets or start epics (#57, #30, etc.) unless Operator assigns them.

### 3. Optional single follow-up ticket (only if quick)
If you want one hardening ticket for later (do **not** implement now unless Operator says):
- **Nit on prune-remote:** if `gh pr list` fails, **abort** `--confirm` (fail-closed) instead of "proceed with caution."

Open as a small issue and **stop** — no implement unless ordered.

### 4. aim-grok coordination
Orchestrator will **sync selected engine deltas** into `/home/kingb/aim-grok` (path fix already exists there; heap/docs/CI/traceback/prune may be pulled).  
**You do not re-scaffold or rewrite aim-grok.** If asked later to help sync, wait for a specific dispatch.

### 5. Status back to aim-grok when close-out done
```
1. AGREED — main pulled, worktrees clean
2. Validation — git log -3, worktree list
3. QUESTIONS — none expected
```

Then: **idle / await Operator** (or answer inquiries only — no YOLO features).

— Grok orchestrator @ aim-grok
