#!/usr/bin/env bash
# Unit-ish test for aim_turn_chime debounce (no audio required if backends fail).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHIME="$ROOT/scripts/aim_turn_chime.sh"
export AIM_STATE_DIR="${TMPDIR:-/tmp}/aim_turn_chime_test_$$"
export AIM_TURN_CHIME_DEBUG=1
export AIM_TURN_CHIME_DEBOUNCE_MS=5000
export AIM_TURN_CHIME=1
# Prefer missing sound backends? Still exit 0 via BEL.
mkdir -p "$AIM_STATE_DIR"
LOG="$AIM_STATE_DIR/turn_chime.log"
rm -f "$LOG" "$AIM_STATE_DIR/turn_chime_last_ms"

bash "$CHIME" first
[[ -f "$LOG" ]] || { echo "FAIL: expected debug log after first chime"; exit 1; }
lines1=$(wc -l <"$LOG")

bash "$CHIME" second
lines2=$(wc -l <"$LOG")
if [[ "$lines2" -ne "$lines1" ]]; then
  echo "FAIL: debounce should suppress second chime within window (log grew)"
  cat "$LOG"
  exit 1
fi

AIM_TURN_CHIME_FORCE=1 bash "$CHIME" forced
lines3=$(wc -l <"$LOG")
if [[ "$lines3" -le "$lines2" ]]; then
  echo "FAIL: FORCE should always chime"
  cat "$LOG"
  exit 1
fi

AIM_TURN_CHIME=0 bash "$CHIME" disabled
lines4=$(wc -l <"$LOG")
if [[ "$lines4" -ne "$lines3" ]]; then
  echo "FAIL: AIM_TURN_CHIME=0 should no-op"
  exit 1
fi

rm -rf "$AIM_STATE_DIR"
echo "PASS test_turn_chime"
