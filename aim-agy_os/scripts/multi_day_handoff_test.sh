#!/usr/bin/env bash
# Multi-day / soak test harness for Handoff vNext.
# Simulates "days" by appending staged sessions and re-running cron pipelines.
set -euo pipefail

VESSEL="${AIM_VESSEL:-/home/kingb/aim-grok}"
PY="${VESSEL}/aim-agy_os/venv/bin/python3"
export PYTHONPATH="${VESSEL}/aim-agy_os:${VESSEL}/aim-agy_os/.aim_core"
FIX="${VESSEL}/aim-agy_os/tests/fixtures/handoff_vnext"
DAYS="${1:-3}"
REPORT_DIR="${VESSEL}/continuity/cron_state/multi_day"
mkdir -p "$REPORT_DIR"

echo "=== multi-day handoff test days=${DAYS} vessel=${VESSEL} ==="

for day in $(seq 1 "$DAYS"); do
  echo "--- day ${day} ---"
  # plant a new staged session for this day
  SID="e2e-vnext-day${day}-$(date +%s)"
  DIR="${FIX}/${SID}"
  mkdir -p "$DIR"
  cat >"${DIR}/meta.json" <<EOF
{"cwd": "${VESSEL}", "day": ${day}}
EOF
  MARKER="E2E_DAY_${day}_MARKER"
  python3 - <<PY
import json
from pathlib import Path
sid = "${SID}"
marker = "${MARKER}"
d = Path("${DIR}")
def line(kind, text):
    return json.dumps({
        "timestamp": ${day},
        "method": "session/update",
        "params": {"sessionId": sid, "update": {
            "sessionUpdate": kind,
            "content": {"type": "text", "text": text},
        }},
    })
turns = [
    ("user_message_chunk", f"Day ${day} work. {marker} MANDATE: continue multi-day soak."),
    ("agent_message_chunk", f"Day ${day} assistant reply. TODO: verify cron."),
    ("user_message_chunk", f"[[KEEP]] day=${day} soak checkpoint"),
    ("agent_message_chunk", "Acknowledged keep."),
]
(d / "updates.jsonl").write_text("\\n".join(line(k,t) for k,t in turns) + "\\n")
print("planted", sid)
PY

  # handoff on newest planted session
  "$PY" -m handoff.cli handoff --adapter fixture --fixture-root "$FIX" \
    --session-id "$SID" --vessel-root "$VESSEL" --project-root "$VESSEL" \
    --marker "$MARKER" --json >"${REPORT_DIR}/day${day}_handoff.json"

  # nightly jobs
  AIM_BLACKBOX_ALLOW_CRON=1 "$PY" -m handoff.cli cron-all --adapter fixture \
    --fixture-root "$FIX" --vessel-root "$VESSEL" --project-root "$VESSEL" \
    --since-mtime 0 --limit 50 --json >"${REPORT_DIR}/day${day}_cron.json"

  # verify marker in continuity
  grep -q "$MARKER" "${VESSEL}/continuity/CURRENT.md"
  # verify FR exists
  test -f "${VESSEL}/continuity/flight_records/${SID}.md"
  # verify db jsonl
  test -f "${VESSEL}/aim-agy_os/memory_lance/handoff_vnext/${SID}.jsonl"
  # verify blackbox
  test -f "${VESSEL}/archive/.raw_jsonl_blackbox/${SID}.enc"

  echo "day ${day} PASS"
done

echo "=== multi-day PASS (${DAYS} days) ===" | tee "${REPORT_DIR}/SUMMARY.txt"
ls -la "$REPORT_DIR"
