#!/usr/bin/env bash
# Full E2E suite for Handoff vNext — unit + staged + multi-day soak + CLI.
set -euo pipefail
VESSEL="${AIM_VESSEL:-/home/kingb/aim-grok}"
cd "$VESSEL"
export PYTHONPATH="${VESSEL}/aim-agy_os:${VESSEL}/aim-agy_os/.aim_core"
export AIM_BLACKBOX_ALLOW_CRON=1
PY="${VESSEL}/aim-agy_os/venv/bin/python3"
OUT="${VESSEL}/continuity/cron_state/e2e_suite_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUT"

echo "=== 1) unit + e2e pytest ===" | tee "$OUT/log.txt"
$PY -m pytest \
  aim-agy_os/tests/test_handoff_vnext.py \
  aim-agy_os/tests/test_handoff_vnext_e2e.py \
  -q --tb=short 2>&1 | tee -a "$OUT/log.txt"

echo "=== 2) cli e2e-staged ===" | tee -a "$OUT/log.txt"
$PY -m handoff.cli e2e-staged \
  --fixture-root aim-agy_os/tests/fixtures/handoff_vnext \
  --vessel-root "$VESSEL" \
  --marker E2E_HANDOFF_VNEXT_MARKER_7f3a 2>&1 | tee "$OUT/e2e_staged.json" | tee -a "$OUT/log.txt"

echo "=== 3) multi-day soak (5 days) ===" | tee -a "$OUT/log.txt"
bash aim-agy_os/scripts/multi_day_handoff_test.sh 5 2>&1 | tee "$OUT/multi_day.txt" | tee -a "$OUT/log.txt"

echo "=== 4) negative: wrong session via CLI ===" | tee -a "$OUT/log.txt"
set +e
$PY -m handoff.cli handoff --adapter fixture \
  --fixture-root aim-agy_os/tests/fixtures/handoff_vnext \
  --session-id definitely-missing-id \
  --vessel-root "$VESSEL" --json >"$OUT/negative_resolve.json" 2>&1
RC=$?
set -e
echo "exit=$RC" | tee -a "$OUT/log.txt"
# expect non-zero
if [[ "$RC" -eq 0 ]]; then
  echo "FAIL: wrong session should not exit 0" | tee -a "$OUT/log.txt"
  exit 1
fi
echo "negative resolve OK (non-zero)" | tee -a "$OUT/log.txt"

echo "=== SUITE PASS ===" | tee -a "$OUT/log.txt"
echo "report dir: $OUT"
cat >"$OUT/SUMMARY.md" <<EOF
# Handoff vNext E2E suite

- pytest: unit + expanded e2e
- cli e2e-staged
- multi-day soak: 5 days
- negative resolve session
- status: **PASS**
- when: $(date -Iseconds)
EOF
cat "$OUT/SUMMARY.md"
