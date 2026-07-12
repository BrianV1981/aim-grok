# DISPATCH from aim-grok / Operator — Reincarnation prefix + E2E

**From:** aim-grok vessel (tmux session may be `aim_reincarnation_*` or similar; reply to Operator / leave artifacts in this file path under your planning-artifacts)
**To:** aim-agy agent (tmux `aim-agy`)
**Authority:** Operator ordered inter-agent dispatch. Execute in scope; do not freestyle rebuilds.

---

## Mission

1. **Implement GitHub issue #93** on **aim-agy**:
   - https://github.com/BrianV1981/aim-agy/issues/93
   - Title: Feature: Prefix reincarnation tmux sessions as `agy_reincarnation_*`
   - Change `session_name` from `aim_reincarnation_{ts}` → `agy_reincarnation_{ts}`
   - Prefer extractable helper (aim-grok reference PR: https://github.com/BrianV1981/aim-grok/pull/2 — vessel via `AIM_VESSEL_CLI` default, tests, life_run greps).

2. **TDD + honesty**
   - Unit tests for naming (default `agy`, env override if used).
   - Do **not** claim pass without running tests.

3. **Full end-to-end life/reincarnation run**
   - After implementation, run your vessel’s full life-run / reincarnate path (or equivalent install→use→reincarnate→wiki if available).
   - **Leave the new reincarnation tmux session UP** for Operator inspection (do **not** kill `agy_reincarnation_*` after success).
   - Confirm log shows spawn like: `agy_reincarnation_<unix_ts>` (not `aim_reincarnation_*`).

4. **Known failure mode: “Do you trust this workspace / folder?”**
   - Operator reports AGY/Antigravity may stall on trust / permission prompts during spawn (and scribe/wiki agents).
   - You were supposed to **bypass by confirming trust** (e.g. select Yes / send Enter / y+Enter as your teleport_engine already attempts for some prompts).
   - **Diagnose and fix if broken:** inspect `reincarnation/teleport_engine.py` (or spawn path) for trust-prompt handling; if Enter-only is failing, harden (capture pane, send `y` then Enter, or documented AGY noninteractive flag if exists).
   - Document in ticket/PR whether trust bypass works on this e2e or still fails (be honest).

---

## Constraints

- Work via GitOps: `./aim fix 93` or equivalent branch/worktree — **not** commit directly to `main` without Operator.
- No force-push, no prune-remote --confirm, no destructive host cleanup.
- Do not modify `/home/kingb/aim-grok` unless absolutely needed for reference only (read-only OK).
- Sibling tickets for awareness (do not implement them): aim-grok #1 / PR #2 (`grok_reincarnation_*`); aim-opencode #9 (`opencode_reincarnation_*`).

---

## Required reply structure (one structured reply; no open-ended chat loop)

Write a short status into:
`/home/kingb/aim-agy/aim-agy_os/planning-artifacts/REPLY_REINCARNATION_PREFIX.md`

And/or paste a brief structured block into your pane for Operator capture:

1. **AGREED** — issue #, branch/PR URL if any
2. **DONE** — what landed (code paths, tests run + results)
3. **E2E** — PASS/FAIL, session name left up (`agy_reincarnation_…`), life-run summary
4. **TRUST PROMPT** — fixed / still broken / not hit + evidence
5. **QUESTIONS** — only if blocked

Do not open an open-ended chat loop with aim-grok. One structured status is enough.

---

## Immediate first actions

1. Read this dispatch fully.
2. `gh issue view 93` / open `aim fix 93`.
3. Implement + unit tests.
4. E2E reincarnate; leave session for Operator.
5. File REPLY_REINCARNATION_PREFIX.md.

— Operator via aim-grok dispatch
