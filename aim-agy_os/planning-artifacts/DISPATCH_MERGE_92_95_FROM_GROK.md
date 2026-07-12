# DISPATCH — Merge #92–#95 to `main`

**From:** Orchestrator on tmux **`grok-audit`** / **`aim-grok`** (Operator authorized)  
**To:** aim-agy engineering agent  
**Date:** 2026-07-12  
**Audit:** `/home/kingb/grok-audit/artifacts/AUDIT_AIM_AGY_ISSUES_92_95_2026-07-12.md`

---

## Mission

**Merge the completed #92–#95 work onto `main` and close the issues.**  
Fixes exist on worktrees/branches but **are not on `main`** (`947c538`). Production is still unfixed until you land them.

| Issue | Branch / worktree | Tip | Topic |
|-------|-------------------|-----|--------|
| #92 | `fix/issue-92` · `workspace/issue-92` | `0b17c98` | prune-remote fail-closed on `gh` errors |
| #93 | `fix/issue-93` · `workspace/issue-93` | `34cce77` | reincarnation vessel prefix (superseded in shape by #95) |
| #94 | `fix/issue-94` · `workspace/issue-94` | `3e07b2e` | LanceDB FTS index on empty table create |
| #95 | `fix/issue-95` · `workspace/issue-95` | `dc46d10` | Full agent session namespacing (includes reincarnation) |

Orchestrator opinion: code quality is **good** (#95 best; #92 solid; #94 minimal but OK). **Ship by merge**, not more redesign.

---

## Required merge order

1. **#92** → `main` (independent)  
2. **#94** → `main` (independent)  
3. **#95** → `main` (includes reincarnation naming; stacks past #93)  
4. **#93** → close as **implemented by #95** *or* merge only if still needed after #95 (avoid double-apply). Prefer **close #93 with comment** pointing at #95’s `agy_reincarnate_<project>_<ts>` pattern if that is the final contract.

Use normal GitOps for this repo:

```bash
cd /home/kingb/aim-agy
# Prefer: gh pr create from each fix/issue-* then gh pr merge
# Or: merge stack carefully onto main with tests green
```

- Resolve VERSION/CHANGELOG conflicts (all branches bump/edit the same files).  
- Prefer **one VERSION bump to v1.0.8** (or next patch) on the final merge commit that lands naming + prune + FTS.  
- Do **not** force-push `main`.  
- Run tests after merge:

```bash
PYTHONPATH=aim-agy_os:aim-agy_os/.aim_core \
  aim-agy_os/venv/bin/python -m pytest aim-agy_os/tests/ -q
# plus naming tests from #95 if present after merge
```

---

## After merge checklist

- [ ] `main` contains prune fail-closed, FTS create-on-init, session_naming  
- [ ] Close GitHub **#92, #94, #95** (and #93 as appropriate) with merge SHAs  
- [ ] Push `main` to `origin`  
- [ ] Report to orchestrator (see below)  
- [ ] Optional follow-up ticket: #94 ensure-FTS-on-open + log failures; #92 fail-closed on JSON parse when `--confirm`  
- [ ] Optional: fix **install-core.sh** alias paths (still wrong on main per audit) — separate issue if not in scope  

---

## Constraints

- No history rewrite, no `git push --force` to `main`.  
- Surgical commits; do not `git add .` secrets/venv/memory.  
- If merge conflicts are large, open stacked PRs and merge via `gh pr merge` rather than improvise.  
- Blast radius: merging is Operator-authorized by this dispatch.

---

## Report back

Write/append:

```
/home/kingb/aim-agy/aim-agy_os/planning-artifacts/REPORT_TO_GROK_MERGE_92_95.md
```

Then short-paste to **both** if possible:

- `grok-audit`  
- `aim-grok`  

Use vessel-correct submit:

```bash
# Grok targets: Enter only (no Escape first)
bash /home/kingb/grok-audit/.grok/skills/aim-communicate/scripts/tmux_send.sh \
  --target grok-audit \
  --message '[REPORT from aim-agy] Merged #92-#95 — read .../REPORT_TO_GROK_MERGE_92_95.md'
```

Structure:

```text
1. MERGED (SHAs, issue numbers closed)
2. CONFLICTS / NOTES
3. TESTS RUN
4. QUESTIONS (if any)
5. NEXT
```

---

*Orchestrator expects merge-to-main completion, not more parallel feature work on 92–95.*
