# Fleet live teleport E2E (2026-07-17)

Safe harness: disposable tmux source (`e2e_tp_src_*`) so pillar sessions
(`aim-agy` / `aim-grok` / `aim-opencode` / `aim-codex`) are never killed.

Harness: `aim-agy_os/scripts/operator_reincarnate_teleport_e2e.py`

| Vessel | Verdict | Child spawned | Source killed | Pillars intact |
|--------|---------|---------------|---------------|----------------|
| **aim-grok** | **PASS** | `grok_reincarnate_aim-grok_*` | yes | yes |
| **aim-agy** | **PASS** | `agy_reincarnate_aim-agy_*` | yes | yes |
| **aim-opencode** | **PASS** | `opencode_reincarnate_aim-opencode_*` | yes | yes |
| aim-codex | wired (CLI + harness); not live-run (token budget) | — | — | — |

## Fixes during this run
1. **aim-agy / aim-opencode / aim-codex** `aim_cli.py`: add `--session-id` and `--no-teleport` to `reincarnate` subparser (cmd already forwarded; parser was bare).
2. Teleport E2E harness never attaches Operator pillar as teleport source.

## Operator usage
```bash
# real handoff (will switch YOUR attached client and kill current session)
./aim reincarnate --session-id <uuid>

# safe full path (no spawn/kill)
./aim reincarnate --session-id <uuid> --no-teleport

# automated live teleport proof (disposable source)
AIM_VESSEL=$PWD AIM_VESSEL_KIND=grok \
  aim-agy_os/venv/bin/python3 aim-agy_os/scripts/operator_reincarnate_teleport_e2e.py
```
