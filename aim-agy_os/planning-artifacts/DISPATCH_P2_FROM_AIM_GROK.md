# Work order from aim-grok (Orchestrator) — Operator authorized

**You are on aim-agy.** Do **not** re-scaffold aim-grok. Phase 0+1 already exist at `/home/kingb/aim-grok`.

## Status
- P0/P1 merged to main. Issues #66–#72 closed.
- Remaining work is **ticketed P2 / follow-ups #80–#85**.

## Execute in this order (strict)
1. **#83** — Fix `aim fix` double-nested path (`aim-agy_os/aim-agy_os/workspace/`). Root cause in path resolution (`aim_cli` / `config_utils` / worktree setup). Prove with `aim fix` dry or a temp issue that worktree lands at project-root `workspace/issue-N` (or single `aim-agy_os/workspace/` — pick one documented layout and stick to it).
2. **#84** — Strengthen CI: add installer dry-run (or syntax/path checks for `install-core.sh` / `setup.sh`) without destructive host mutation. Prefer a non-root sandbox / `bash -n` + path assertions if full curl install is too heavy.
3. **#82** — Soften Node heap default in installers (e.g. 4096 or 8192) + document why in README or comment.
4. **#81** — Branch retention: script or `aim` subcommand notes to prune remote `fix/issue-*` after merge; do **not** mass-delete remotes without listing first and Operator confirm for bulk `git push origin --delete`. Prefer a dry-run mode.
5. **#80** — Docs drift: SCRIPT_MAP, TOOLS.md, `.aim_core/README.md` match reality.
6. **#85** — Narrow bare `except:` in **highest-traffic** modules first (`aim_cli`, `retriever`, `lance_backend`, `handoff_*`); no mega-PR rewriting all 83 at once.

## GitOps
- `aim fix <id>` → branch → PR → do not push to main.
- Status paste to `aim-grok` after each ticket: issue #, branch, PR #, validation.
- No history rewrite. No force-push main.

## Grok note
aim-grok will continue Phase 2 independently. If you fix shared engine files, list them in your status so orchestrator can sync via SYNC_FROM_AIM_AGY.md.

Start **#83** immediately.
— Grok @ aim-grok
