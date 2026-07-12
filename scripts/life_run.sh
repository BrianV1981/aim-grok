#!/usr/bin/env bash
# Full life-cycle test: headless install → live use → reincarnate → wiki verify
set -euo pipefail

ROOT_SRC="${AIM_GROK_SRC:-/home/kingb/aim-grok}"
TEST_ROOT="${AIM_LIFE_ROOT:-/home/kingb/test_aim_grok_life}"
STAMP=$(date +%Y%m%d_%H%M%S)
TEST_DIR="${TEST_ROOT}/${STAMP}"
REPORT="${TEST_DIR}/LIFE_RUN_REPORT.md"
SESSION_ID="${AIM_SESSION_ID:-019f542b-7e52-71c1-95c1-50d1c5e5ccea}"

mkdir -p "$TEST_DIR"
exec > >(tee -a "${TEST_DIR}/life_run.log") 2>&1

echo "======== LIFE RUN START $(date -Iseconds) ========"
echo "TEST_DIR=$TEST_DIR"
echo "SRC=$ROOT_SRC SESSION_ID=$SESSION_ID"

pass=0; fail=0
ok() { echo "[PASS] $1"; pass=$((pass+1)); }
bad() { echo "[FAIL] $1"; fail=$((fail+1)); }

# --- 1) Headless install (download vessel from GitHub or local clone) ---
echo ""
echo "=== PHASE 1: HEADLESS INSTALL ==="
cd "$TEST_DIR"
if [[ "${AIM_LIFE_USE_LOCAL:-0}" == "1" ]]; then
  echo "Using local rsync from $ROOT_SRC (dev mode)"
  rsync -a --exclude .git --exclude aim-agy_os/venv --exclude aim-agy_os/memory_lance \
    --exclude aim-agy_os/archive --exclude aim-agy_os/.aim_core/temp \
    --exclude workspace --exclude .pytest_cache \
    "$ROOT_SRC/" "$TEST_DIR/vessel/"
  cd "$TEST_DIR/vessel"
  git init -b main >/dev/null
  git remote add origin https://github.com/BrianV1981/aim-grok.git 2>/dev/null || true
else
  echo "Cloning https://github.com/BrianV1981/aim-grok.git (depth 1)"
  git clone --depth 1 https://github.com/BrianV1981/aim-grok.git vessel
  cd "$TEST_DIR/vessel"
fi

echo "[*] setup.sh"
bash aim-agy_os/setup.sh
mkdir -p aim-agy_os/memory_lance
cp -a aim-agy_os/assets/default_lance/. aim-agy_os/memory_lance/
chmod +x ./aim 2>/dev/null || true

# Local CONFIG
mkdir -p .aim_core
python3 - <<'PY'
import json
from pathlib import Path
root = Path(".").resolve()
os_root = root / "aim-agy_os"
cfg = {
  "paths": {
    "aim_root": str(os_root),
    "os_root": str(os_root),
    "src_dir": str(os_root / ".aim_core"),
    "tmp_chats_dir": str(Path.home() / ".grok/sessions"),
    "continuity_dir": str(os_root / "continuity"),
    "archive_raw_dir": str(os_root / "archive/raw"),
  },
  "settings": {"cognitive_mode": "monolithic", "sentinel_mode": "full"},
  "vessel": "aim-grok-life-test",
}
(root / ".aim_core" / "CONFIG.json").write_text(json.dumps(cfg, indent=2))
print("CONFIG written")
PY

./aim doctor && ok "install doctor" || bad "install doctor"
./aim map | head -15 && ok "map" || bad "map"

# --- 2) Live use (agent life) ---
echo ""
echo "=== PHASE 2: LIVE USE ==="
./aim search "GitOps" >/tmp/life_search.out 2>&1 && ok "search" || bad "search"
./aim wiki bootstrap 2>&1 | tail -15 && ok "wiki bootstrap" || bad "wiki bootstrap"
WIKI_PAGES_BEFORE=$(ls aim-agy_os/memory-wiki/pages/*.md 2>/dev/null | wc -l)
echo "wiki pages before life note: $WIKI_PAGES_BEFORE"

mkdir -p aim-agy_os/memory-wiki/_ingest
cat > aim-agy_os/memory-wiki/_ingest/life_run_marker.md <<EOF
# Life Run Marker

This note was written during the automated life run at $STAMP.

## Facts
- Test directory: $TEST_DIR
- Vessel: aim-grok life test
- Session id for reincarnation: $SESSION_ID
- Goal: prove headless install, reincarnation, and wiki update

## Immediate proof
If you can wiki-search for LIFE_RUN_MARKER_${STAMP}, the wiki pipeline works.
LIFE_RUN_MARKER_${STAMP}
EOF
./aim wiki process 2>&1 | tail -10 && ok "wiki process life note" || bad "wiki process"
./aim wiki search "LIFE_RUN_MARKER_${STAMP}" 2>&1 | head -15
if ./aim wiki search "LIFE_RUN_MARKER_${STAMP}" 2>&1 | grep -q "LIFE_RUN_MARKER_${STAMP}"; then
  ok "wiki finds life marker"
else
  bad "wiki missing life marker"
fi

# --- 3) Reincarnation ---
echo ""
echo "=== PHASE 3: REINCARNATION ==="
mkdir -p aim-agy_os/.aim_core/temp
cat > aim-agy_os/.aim_core/temp/REINCARNATION_GAMEPLAN.md <<EOF
### 1. The Commander's Summary
Life-run reincarnation test for aim-grok. Headless install completed in $TEST_DIR/vessel.
Wiki seeded and life marker LIFE_RUN_MARKER_${STAMP} ingested.

### 2. Tactical State (The "Where Am I?" Block)
- **Active Ticket:** Life-run validation (no GitHub issue)
- **Active Worktree:** $TEST_DIR/vessel
- **Primary Files:** aim-agy_os/memory-wiki/, ./aim, SOURCE.md

### 3. The Localized Directory Map
\`\`\`
vessel/
  aim
  aim-agy_os/
    memory-wiki/pages/
    .aim_core/
\`\`\`

### 4. Epistemic Warnings & Dead Ends
- Do not reinstall the vessel.
- Do not push to production remotes from this test tree.
- AIM_REINCARNATE_NO_TELEPORT is set so the parent session is not killed.

### 5. Immediate Next Action
1. Run \`./aim doctor\`
2. Run \`./aim wiki search "LIFE_RUN_MARKER_${STAMP}"\`
3. Confirm you are the reincarnated vessel and report HANDOFF_RECEIVED.
EOF

# Touch mtime to be fresh
touch aim-agy_os/.aim_core/temp/REINCARNATION_GAMEPLAN.md

export AIM_VESSEL_CLI=grok
export AIM_REINCARNATE_NO_TELEPORT=1
export AIM_WIKI_MODE=deterministic
export AIM_WORKSPACE="$TEST_DIR/vessel"

# Capture sessions before (soul role token: reincarnate → grok_reincarnate_*)
REINC_PREFIX="${AIM_VESSEL_CLI:-grok}_reincarnate_"
SESSIONS_BEFORE=$(tmux list-sessions -F '#{session_name}' 2>/dev/null | grep -c "$REINC_PREFIX" || true)

./aim-agy_os/venv/bin/python aim-agy_os/.aim_core/aim_reincarnate.py \
  --session-id "$SESSION_ID" 2>&1 | tee /tmp/life_reinc.out

if grep -q "REINCARNATION PROTOCOL\|New agent is awake\|NO_TELEPORT\|Success" /tmp/life_reinc.out; then
  ok "reincarnate completed"
else
  bad "reincarnate failed"
  cat /tmp/life_reinc.out | tail -40
fi

NEW_SESS=$(tmux list-sessions -F '#{session_name}' 2>/dev/null | grep "$REINC_PREFIX" | tail -1 || true)
echo "new_tmux_session=${NEW_SESS:-none}"
if [[ -n "${NEW_SESS:-}" ]]; then
  ok "tmux vessel spawned: $NEW_SESS"
  sleep 3
  echo "--- capture new vessel (first lines) ---"
  tmux capture-pane -t "$NEW_SESS" -p -J 2>/dev/null | tail -25 || true
else
  bad "no reincarnation tmux session found"
fi

# --- 4) Wait for wiki/history pipeline ---
echo ""
echo "=== PHASE 4: WIKI / MEMORY AFTER REINCARNATION ==="
# pulse already ran inside reincarnate; summarizer is bg — wait and process
for i in 1 2 3 4 5 6; do
  sleep 5
  echo "wait ${i}/6 ..."
  # Ensure deterministic compile of any new raw/history
  ./aim wiki process 2>&1 | tail -5 || true
done

# Stage latest history if present
if ls aim-agy_os/archive/history/*.md >/dev/null 2>&1; then
  ./aim-agy_os/venv/bin/python aim-agy_os/.aim_core/wiki_compiler.py stage-history --history-limit 3
  ./aim wiki process 2>&1 | tail -10
fi

WIKI_PAGES_AFTER=$(ls aim-agy_os/memory-wiki/pages/*.md 2>/dev/null | wc -l)
echo "wiki pages after: $WIKI_PAGES_AFTER (before life note process was post-bootstrap)"
LOG_TAIL=$(tail -15 aim-agy_os/memory-wiki/log.md)
echo "$LOG_TAIL"
if echo "$LOG_TAIL" | grep -qiE 'life|history|created|updated'; then
  ok "wiki log shows activity"
else
  bad "wiki log quiet"
fi

./aim map 2>&1 | head -20
./aim doctor 2>&1 | tail -8

# --- 5) Report ---
cat > "$REPORT" <<EOF
# Life Run Report

- **When:** $(date -Iseconds)
- **Test dir:** \`$TEST_DIR\`
- **Session ID:** \`$SESSION_ID\`
- **Reincarnation tmux:** \`${NEW_SESS:-none}\`
- **PASS:** $pass
- **FAIL:** $fail
- **Wiki pages:** $WIKI_PAGES_AFTER
- **Life marker:** LIFE_RUN_MARKER_${STAMP}

## Attach
- \`life_run.log\`
- reincarnate: inspect tmux \`$NEW_SESS\`

## Cleanup
\`\`\`bash
tmux kill-session -t $NEW_SESS 2>/dev/null || true
# optional: rm -rf $TEST_DIR
\`\`\`
EOF

echo ""
echo "======== LIFE RUN SUMMARY PASS=$pass FAIL=$fail ========"
echo "Report: $REPORT"
echo "Vessel: $TEST_DIR/vessel"
[[ "$fail" -eq 0 ]]
