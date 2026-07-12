# Work order from aim-grok (Orchestrator) — Operator authorized

**Reply session:** `aim-grok` (structured status only; no chat loops)
**Auditor:** Grok will review your branches/PRs/commits. Prefer small atomic tickets.

## Decision (answers your question)
**Proceed with P0 now.** Defer P2 design work until P0 + P1 are done.

## Execution order (strict)
1. **#67** — Remove `aim-agy_os/memory/` from git tracking + fix `.gitignore` so engine source stays trackable deliberately; keep seed under `assets/default_lance/` only. **Do NOT git filter-repo / force-push history rewrite** without Operator. Removing from the index + ignore rules is enough for this ticket.
2. **#66** — Fix `install-core.sh` (`aim-agy_os/setup.sh`, seed `memory_lance/` not `memory/lance/`).
3. **#68** — Rewrite CI to real paths (`aim-agy_os/requirements.txt`, a real `tests/` tree, correct PYTHONPATH). Add at least one smoke test if none exist.
4. **#69** — Prune stale worktrees issue-59..62 **only after** confirming those branches are fully merged; report commands you will run before destructive remove if unsure.
5. **#70** — Implement minimal `aim doctor` **or** remove the dead command (prefer implement a thin env check).
6. **#71** — Align VERSION files to one semver line (recommend continuing **v1.0.x** from root `v1.0.7` or document bump).
7. **#72** — Pin deps or add lockfile (pip freeze of working venv or constraints file is fine).

## GitOps rules (non-negotiable)
- Never push/commit to `main` directly. Use `aim bug` already filed; `aim fix <id>` / isolated branch + PR or `aim push` per your protocol.
- Surgical staging only (`git add` specific paths).
- No YOLO merges. No `rm -rf` of production memory DBs without isolated proof first.
- After each ticket: brief status paste to `aim-grok` with: issue #, branch, summary of change, how you validated.

## Definition of done per ticket
- Code/docs changed on a branch (not only local uncommitted)
- Empirical check (script runs, CI yaml paths exist, worktree list clean, etc.)
- Issue closed or marked ready-for-review with evidence

Start with **#67** immediately.
— Grok @ aim-grok (orchestrator + auditor)
