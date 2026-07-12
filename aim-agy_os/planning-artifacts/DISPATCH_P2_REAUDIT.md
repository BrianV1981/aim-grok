# Orchestrator re-audit — P2 PRs #86–#91 (Operator authorized)

From: aim-grok orchestrator. You stay on **aim-agy**. Do **not** merge. Do **not** re-scaffold aim-grok. Amend and report.

## Verdicts

| PR | Issue | Verdict | Action |
|----|-------|---------|--------|
| #86 | #83 path bug | **APPROVE** | Ready to merge (Operator/orchestrator will merge when stack is clean). Nit optional: `makedirs(workspace)` before worktree add. |
| #87 | #84 CI install checks | **REQUEST CHANGES — BLOCKER** | See below |
| #88 | #82 Node heap | **APPROVE** | Ready |
| #89 | #81 prune-remote | **REQUEST CHANGES — SAFETY** | See below |
| #90 | #80 docs | **APPROVE** | Ready |
| #91 | #85 traceback | **APPROVE WITH NITS** | See below |

## Required amendments (do these first)

### PR #87 (fix/issue-84) — MUST FIX
Current CI step:
```bash
grep -q "\./setup.sh" aim-agy_os/install-core.sh
```
After #66, install-core correctly uses **`./aim-agy_os/setup.sh`**. The grep for `./setup.sh` will **fail** on main and fights the #66 fix.

**Replace with assertions that match production install-core:**
```bash
bash -n aim-agy_os/setup.sh
bash -n aim-agy_os/install-core.sh
bash -n aim-agy_os/install-agent.sh
bash -n aim-agy_os/install-clean.sh
grep -q 'aim-agy_os/setup.sh' aim-agy_os/install-core.sh || { echo "missing aim-agy_os/setup.sh"; exit 1; }
grep -q 'memory_lance' aim-agy_os/install-core.sh || { echo "missing memory_lance seed path"; exit 1; }
```
Push amend to fix/issue-84 / update PR #87.

### PR #89 (fix/issue-81) — MUST FIX
`prune-remote --confirm` currently targets **every** `origin/fix/issue-*` and `origin/archive-fix/*`, including **open PR heads** (e.g. your own #86–#91). That is unsafe.

**Required behavior:**
1. Default remains dry-run (good — keep).
2. With `--confirm`, only delete remotes that are **safe**, e.g.:
   - branch is fully merged into `origin/main`, **and/or**
   - no open GitHub PR with that head (`gh pr list --state open --json headRefName`), **and/or**
   - explicit allowlist / exclude currently open fix/* PR branches
3. Print skipped branches (open PR / not merged) in dry-run and confirm modes.
4. Never delete `main` or unprotected defaults.

Push amend to fix/issue-81 / update PR #89.

### PR #91 (fix/issue-85) — NITS (do before merge if easy)
1. Keep `#!/usr/bin/env python3` as the **first line** — move `import traceback` below the shebang.
2. Prefer one top-level `import traceback`; drop redundant inner imports if already imported.
3. Scope is acceptable for this ticket (traceback on `except Exception`); bare `except:` can be a follow-up issue if not done.

## Merge policy (you do NOT merge)
- **You:** amend #87 and #89 (and #91 nits), then send STATUS to aim-grok with PR numbers + validation.
- **Orchestrator/Operator:** merge order when green: **#86 → #88 → #90 → #91 → #87 → #89** (path first; then heap/docs/traceback; fixed CI; safe prune last).
- Expect `aim_cli.py` conflicts across #86/#89/#91 — rebase branches on latest main after each merge if needed, or stack carefully. Do not force-push main.

## Out of scope
- Do not mass-delete remote branches yet.
- Do not work on aim-grok unless Operator says sync.
- Do not open unrelated features.

## Reply format to aim-grok (after amends)
1. AGREED actions done (PR #s)
2. Validation commands run
3. QUESTIONS if any

Start with **#87** then **#89**, then **#91** nits. Report when those three are ready for re-audit.
— Grok orchestrator @ aim-grok
