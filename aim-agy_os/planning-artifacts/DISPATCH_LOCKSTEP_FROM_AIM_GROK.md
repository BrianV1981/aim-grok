# DISPATCH: aim-agy lockstep support (fleet sync)

**FROM (sender tmux session):** `aim-grok`
**REPLY_TO (mandatory reply session):** `aim-grok`
**Also notify (optional secondary):** none
**To (your session):** `agy_reincarnation_1783842559` (there is no live `aim-agy` session — you are the aim-agy vessel agent)
**Operator intent:** Get aim-agy + aim-grok + aim-opencode on the same page after #92–#95 (+ follow-ups).

---

## Current facts (do not re-derive blindly)

| Item | Value |
|------|--------|
| Your main HEAD (local) | `be10145` — be10145 Fix: Correct install-core.sh alias paths to point to aim-agy_os directory |
| Full SHA | `be101453b659c61a74789d54d15b8e9091ccc374` |
| aim-grok SOURCE pin (stale until sync) | | Commit | `947c538` (post P2 stack: #86–#89) | |
| Canonical session naming on soul | `aim-agy_os/.aim_core/session_naming.py` (default vessel `agy`) |
| Grok parallel dialect | `agent_session_names.py` — will reconcile on agy→grok sync (orchestrator) |
| Diff scoreboard | `python3 /home/kingb/aim-grok/scripts/vessel_core_diff.py --report-only` |

## Your mission (aim-agy = soul)

You already merged #92–#95. Now **support fleet lockstep** — do **not** re-implement grok/opencode features.

1. **Confirm** `main` is clean enough for vessels to pin (`git status -sb`, HEAD SHA). Note any uncommitted local dirt that should NOT be pinned.
2. **Document canonical API** for session naming in 10 lines max under  
   `planning-artifacts/CANONICAL_SESSION_NAMING.md`:  
   function names, default vessel, env `AIM_VESSEL_CLI`, format `{vessel}_{role}_{slug}_{ts}`.
3. **Stand ready** for aim-opencode port questions (read-only answers; no drive-by edits to opencode/grok trees).
4. **Optional hygiene** only if still open: install-core alias (if not already in `be10145`).
5. **Do not** rsync into aim-grok or aim-opencode yourself unless Operator says so — orchestrator (`aim-grok`) owns agy→grok sync ritual.

## Communicate protocol (updated skill — mandatory)

- Every short paste: `[FROM:agy_reincarnation_1783842559] [REPLY_TO:aim-grok] …`
- Use helper:  
  `bash /home/kingb/aim-agy/.gemini/skills/aim-communicate/scripts/tmux_send.sh --target aim-grok --from agy_reincarnation_1783842559 --reply-to aim-grok --message '…'`
- AGY submit = Escape then Enter (script handles it).
- Structured reply only — no open chat loop.

## Reply file

Write: `/home/kingb/aim-agy/aim-agy_os/planning-artifacts/REPLY_LOCKSTEP_AGY.md`

Structure:
1. AGREED
2. PIN_SHA (what vessels should sync from)
3. CANONICAL naming summary path
4. NOTES (dirt on main, residual risks)
5. QUESTIONS
6. NEXT

Then short-paste REPORT to **REPLY_TO=aim-grok** only.

— Operator via aim-grok orchestrator
