#!/usr/bin/env bash
# Install Operator-local crontabs for Handoff vNext nightly jobs.
# Does NOT require agents. Safe: uses vessel paths + venv python.
set -euo pipefail

VESSEL="${AIM_VESSEL:-/home/kingb/aim-grok}"
PY="${VESSEL}/aim-agy_os/venv/bin/python3"
CLI="${VESSEL}/aim-agy_os/scripts/aim_handoff_vnext.py"
LOG_DIR="${HOME}/.aim/cron/logs"
STATE_MARKER="${HOME}/.aim/cron/handoff_vnext.installed"

mkdir -p "$LOG_DIR" "$(dirname "$STATE_MARKER")"

if [[ ! -x "$PY" ]]; then
  echo "missing venv python: $PY" >&2
  exit 1
fi

# Nightly 02:15 — blackbox + wiki batch (cron-all)
# Nightly 03:00 — optional second wiki pass (idempotent watermark)
CRON_LINE_ALL="15 2 * * * cd ${VESSEL} && AIM_BLACKBOX_ALLOW_CRON=1 PYTHONPATH=${VESSEL}/aim-agy_os:${VESSEL}/aim-agy_os/.aim_core ${PY} ${CLI} cron-all --adapter grok --vessel-root ${VESSEL} --project-root ${VESSEL} --limit 100 >> ${LOG_DIR}/cron-all.log 2>&1"
CRON_LINE_BB="0 2 * * * cd ${VESSEL} && AIM_BLACKBOX_ALLOW_CRON=1 PYTHONPATH=${VESSEL}/aim-agy_os:${VESSEL}/aim-agy_os/.aim_core ${PY} ${CLI} blackbox-cron --adapter grok --vessel-root ${VESSEL} --limit 200 >> ${LOG_DIR}/blackbox.log 2>&1"

# Install: remove prior handoff_vnext lines then append
TMP=$(mktemp)
crontab -l 2>/dev/null | grep -v 'aim_handoff_vnext' | grep -v 'handoff_vnext' >"$TMP" || true
echo "$CRON_LINE_BB" >>"$TMP"
echo "$CRON_LINE_ALL" >>"$TMP"
crontab "$TMP"
rm -f "$TMP"

echo "installed" >"$STATE_MARKER"
echo "Installed handoff vNext crons for ${VESSEL}"
echo "  02:00 blackbox-cron"
echo "  02:15 cron-all (blackbox + wiki-batch)"
echo "Logs: ${LOG_DIR}/"
crontab -l | grep aim_handoff_vnext || true
