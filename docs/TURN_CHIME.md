# Turn-done chime (agent finished responding)

Short audio cue when an agent **ends a turn** so the Operator can look back without staring at every pane.

## What fires it

| Vessel | Event | Wiring |
|--------|--------|--------|
| **Grok** | `Stop` / `StopFailure` | `~/.grok/hooks/aim-turn-chime.json` (+ project `.grok/hooks/`) |
| **OpenCode** | `session.idle` | `aim-hooks.ts` shells out to `aim_turn_chime.sh` |
| **AGY** | best-effort | install script registers AfterAgent if supported; else manual/tmux watch |
| **Codex** | deferred | same host script; host adapter TBD |

## Install (this host)

Already done if you pulled the feature branch / ran install:

```bash
# copy player + sound into host profile
mkdir -p ~/.aim/bin ~/.aim/sounds
cp aim-agy_os/scripts/aim_turn_chime.sh ~/.aim/bin/
cp aim-agy_os/assets/sounds/turn_done.wav ~/.aim/sounds/
chmod +x ~/.aim/bin/aim_turn_chime.sh
# Grok global hooks
cp .grok/hooks/aim-turn-chime.json ~/.grok/hooks/  # or use repo copy under ~/.grok/hooks
```

**Grok:** restart the TUI (or `/hooks` to confirm `Stop` is loaded). Project hooks need `/hooks-trust` once.

## Operator controls

| Env | Effect |
|-----|--------|
| `AIM_TURN_CHIME=0` | disable |
| `AIM_TURN_CHIME_CMD='…'` | custom play command |
| `AIM_TURN_CHIME_SOUND=/path/to.wav` | custom sound file |
| `AIM_TURN_CHIME_DEBOUNCE_MS=1500` | min gap between chimes |
| `AIM_TURN_CHIME_FORCE=1` | ignore debounce (tests) |
| `AIM_TURN_CHIME_BELL=1` | always ring terminal BEL too |
| `AIM_TURN_CHIME_DEBUG=1` | append `~/.aim/state/turn_chime.log` |

## Test

```bash
AIM_TURN_CHIME_FORCE=1 AIM_TURN_CHIME_DEBUG=1 \
  bash aim-agy_os/scripts/aim_turn_chime.sh manual_test
```

If no PulseAudio/ffplay, falls back to terminal BEL (`\a`).

## Non-goals

- Chime on every tool call (too noisy)
- Subagent stop by default (enable later if wanted)
- Making sound part of reincarnate PASS gates
