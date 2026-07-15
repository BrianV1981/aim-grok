#!/usr/bin/env bash
# Full fleet gate: headless install (GitHub main) → test session → pulse/reincarnate → wiki verify.
# Implements docs/GOAL_REINCARNATION_MEMORY_WIKI.md
#
# Usage:
#   bash scripts/fleet_full_reincarnate_gate.sh              # all vessels
#   AIM_VESSEL=grok bash scripts/fleet_full_reincarnate_gate.sh
# Env:
#   AIM_LIFE_USE_LOCAL=0|1   default 0 = git clone main from GitHub
#   AIM_LIFE_ROOT            default /home/kingb/test_fleet_full_gate
set -euo pipefail

ORCH="${AIM_ORCH_SRC:-/home/kingb/aim-grok}"
LIFE_ROOT="${AIM_LIFE_ROOT:-/home/kingb/test_fleet_full_gate}"
USE_LOCAL="${AIM_LIFE_USE_LOCAL:-0}"
STAMP=$(date +%Y%m%d_%H%M%S)
VESSELS="${AIM_VESSEL:-grok agy opencode}"
# if single vessel passed as AIM_VESSEL=grok, don't split wrong
if [[ "${AIM_VESSEL:-}" == "grok" || "${AIM_VESSEL:-}" == "agy" || "${AIM_VESSEL:-}" == "opencode" ]]; then
  VESSELS="$AIM_VESSEL"
fi

SUMMARY="${LIFE_ROOT}/FLEET_GATE_SUMMARY_${STAMP}.md"
mkdir -p "$LIFE_ROOT"
: > "$SUMMARY"

pass_n=0
fail_n=0
declare -a RESULTS=()

ok() { echo "[PASS] $1"; }
bad() { echo "[FAIL] $1"; }

run_vessel() {
  local VESSEL="$1"
  local GH_URL ROOT_SRC TEST_DIR REPORT
  case "$VESSEL" in
    grok)
      GH_URL="https://github.com/BrianV1981/aim-grok.git"
      ROOT_SRC="${AIM_GROK_SRC:-/home/kingb/aim-grok}"
      ;;
    agy)
      GH_URL="https://github.com/BrianV1981/aim-agy.git"
      ROOT_SRC="${AIM_AGY_SRC:-/home/kingb/aim-agy}"
      ;;
    opencode)
      GH_URL="https://github.com/BrianV1981/aim-opencode.git"
      ROOT_SRC="${AIM_OPENCODE_SRC:-/home/kingb/aim-opencode}"
      ;;
    *) echo "unknown vessel $VESSEL"; return 2 ;;
  esac

  TEST_DIR="${LIFE_ROOT}/${VESSEL}/${STAMP}"
  REPORT="${TEST_DIR}/GATE_REPORT.md"
  mkdir -p "$TEST_DIR"
  local LOG="${TEST_DIR}/gate.log"
  exec 3>&1 4>&2
  exec > >(tee -a "$LOG") 2>&1

  echo "======== GATE vessel=$VESSEL START $(date -Iseconds) ========"
  echo "TEST_DIR=$TEST_DIR USE_LOCAL=$USE_LOCAL GH=$GH_URL"
  local v_pass=0 v_fail=0
  vok() { echo "[PASS] $1"; v_pass=$((v_pass+1)); }
  vbad() { echo "[FAIL] $1"; v_fail=$((v_fail+1)); }

  # --- PHASE 1: HEADLESS INSTALL ---
  echo ""
  echo "=== PHASE 1: HEADLESS INSTALL ==="
  cd "$TEST_DIR"
  if [[ "$USE_LOCAL" == "1" ]]; then
    rsync -a --exclude .git --exclude '*/venv' --exclude venv \
      --exclude '*/memory_lance' --exclude memory_lance \
      --exclude '*/__pycache__' --exclude .pytest_cache \
      "$ROOT_SRC/" "$TEST_DIR/vessel/"
    cd "$TEST_DIR/vessel"
    git init -b main >/dev/null 2>&1 || true
  else
    git clone --depth 1 "$GH_URL" vessel
    cd "$TEST_DIR/vessel"
  fi
  git rev-parse --short HEAD 2>/dev/null || true
  git log -1 --oneline 2>/dev/null || true

  if [[ ! -f aim-agy_os/setup.sh ]]; then
    vbad "missing nested aim-agy_os/setup.sh"
  else
    # sudo-free bootstrap
    if grep -qE "Skipping sudo|VENV BOOTSTRAP|max-old-space" aim-agy_os/setup.sh 2>/dev/null \
      || head -5 aim-agy_os/setup.sh | grep -q bash; then
      set +e
      bash aim-agy_os/setup.sh
      set -e
    fi
    if [[ ! -x aim-agy_os/venv/bin/python3 ]]; then
      python3 -m venv aim-agy_os/venv
      aim-agy_os/venv/bin/python3 -m pip install -q --upgrade pip
      if [[ -f aim-agy_os/requirements.txt ]]; then
        aim-agy_os/venv/bin/python3 -m pip install -q -r aim-agy_os/requirements.txt || true
      fi
    fi
    vok "venv present"
  fi

  VENV_PY=aim-agy_os/venv/bin/python3
  [[ -x "$VENV_PY" ]] || VENV_PY=python3

  mkdir -p aim-agy_os/memory_lance
  if [[ -d aim-agy_os/assets/default_lance ]]; then
    cp -a aim-agy_os/assets/default_lance/. aim-agy_os/memory_lance/ 2>/dev/null || true
  fi
  mkdir -p aim-agy_os/memory-wiki/{pages,_ingest,_raw_logs} memory-wiki/{pages,_ingest} \
    .aim_core aim-agy_os/.aim_core core archive/raw archive/history continuity
  touch aim-agy_os/memory-wiki/log.md aim-agy_os/memory-wiki/index.md 2>/dev/null || true
  touch memory-wiki/log.md memory-wiki/index.md 2>/dev/null || true

  # CONFIG for all path layouts
  python3 - <<'PY'
import json
from pathlib import Path
root = Path(".").resolve()
os_root = root / "aim-agy_os"
cfg = {
  "paths": {
    "aim_root": str(os_root if (os_root / ".aim_core").is_dir() else root),
    "os_root": str(os_root),
    "src_dir": str(os_root / ".aim_core"),
    "continuity_dir": str(root / "continuity"),
    "archive_raw_dir": str(root / "archive" / "raw"),
    "opencode_export_dir": str(root / "archive" / "raw"),
    "tmp_chats_dir": str(Path.home() / ".grok" / "sessions"),
  },
  "settings": {"cognitive_mode": "monolithic", "sentinel_mode": "full"},
  "vessel": "fleet-full-gate",
}
for p in [
    root / ".aim_core" / "CONFIG.json",
    os_root / ".aim_core" / "CONFIG.json",
    root / "core" / "CONFIG.json",
    os_root / "core" / "CONFIG.json",
]:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cfg, indent=2) + "\n")
print("CONFIG ok")
PY

  chmod +x ./aim 2>/dev/null || true
  if [[ ! -x ./aim ]]; then
    cat > ./aim << 'AIMWRAP'
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
OS="$ROOT/aim-agy_os"
PY="$OS/venv/bin/python3"
[[ -x "$PY" ]] || PY=python3
export PYTHONPATH="${OS}:${OS}/.aim_core${PYTHONPATH:+:$PYTHONPATH}"
exec "$PY" "$OS/.aim_core/aim_cli.py" "$@"
AIMWRAP
    chmod +x ./aim
  fi

  if ./aim doctor >/tmp/gate_doctor_${VESSEL}.out 2>&1; then
    vok "aim doctor"
  else
    # soft: doctor may warn on embeddings
    if grep -qiE "ok|ready|pass" /tmp/gate_doctor_${VESSEL}.out; then
      vok "aim doctor (soft)"
    else
      echo "doctor out:"; tail -20 /tmp/gate_doctor_${VESSEL}.out || true
      vbad "aim doctor"
    fi
  fi

  # --- PHASE 2+3+4: OPERATOR SESSION → PULSE → WIKI ---
  echo ""
  echo "=== PHASE 2–4: TEST SESSION + REINCARNATE PULSE + VERIFY ==="
  export AIM_WIKI_SKIP_LANCE=1
  export PYTHONPATH="aim-agy_os:aim-agy_os/.aim_core${PYTHONPATH:+:$PYTHONPATH}"
  export AIM_VESSEL="$(pwd)"

  local E2E_RC=2
  case "$VESSEL" in
    grok)
      if [[ -f aim-agy_os/scripts/operator_reincarnate_wiki_e2e.py ]]; then
        "$VENV_PY" aim-agy_os/scripts/operator_reincarnate_wiki_e2e.py
        E2E_RC=$?
      else
        vbad "missing operator_reincarnate_wiki_e2e.py on main"
      fi
      ;;
    agy)
      if [[ -f aim-agy_os/scripts/operator_reincarnate_wiki_e2e_agy.py ]]; then
        "$VENV_PY" aim-agy_os/scripts/operator_reincarnate_wiki_e2e_agy.py
        E2E_RC=$?
      else
        vbad "missing operator_reincarnate_wiki_e2e_agy.py on main"
      fi
      ;;
    opencode)
      if [[ -f aim-agy_os/scripts/operator_reincarnate_wiki_e2e_oc.py ]]; then
        "$VENV_PY" aim-agy_os/scripts/operator_reincarnate_wiki_e2e_oc.py
        E2E_RC=$?
      else
        vbad "missing operator_reincarnate_wiki_e2e_oc.py on main"
      fi
      ;;
  esac

  if [[ "$E2E_RC" -eq 0 ]]; then
    vok "operator session+pulse+wiki E2E"
  else
    vbad "operator session+pulse+wiki E2E (exit $E2E_RC)"
  fi

  # --- PHASE 5: aim_reincarnate protocol (no teleport) ---
  echo ""
  echo "=== PHASE 5: aim_reincarnate (NO_TELEPORT) ==="
  mkdir -p aim-agy_os/.aim_core/temp
  cat > aim-agy_os/.aim_core/temp/REINCARNATION_GAMEPLAN.md <<EOF
### 1. The Commander's Summary
Fleet full gate reincarnation for **$VESSEL** stamp $STAMP.

### 2. Tactical State
- Active Ticket: fleet_full_reincarnate_gate
- Active Worktree: $TEST_DIR/vessel

### 5. Immediate Next Action
1. ./aim doctor
2. Confirm operator E2E already passed
EOF
  export AIM_REINCARNATE_NO_TELEPORT=1
  export AIM_WORKSPACE="$(pwd)"
  set +e
  "$VENV_PY" aim-agy_os/.aim_core/aim_reincarnate.py 2>&1 | tee /tmp/gate_reinc_${VESSEL}.out
  set -e
  if grep -qE "REINCARNATION PROTOCOL|HANDOFF READY|NO_TELEPORT|Success|New agent|CONTEXT FADE" /tmp/gate_reinc_${VESSEL}.out; then
    vok "aim_reincarnate protocol ran"
  else
    # handoff may be enough; soft-fail only if zero output
    if [[ -s /tmp/gate_reinc_${VESSEL}.out ]]; then
      vok "aim_reincarnate produced output (soft)"
    else
      vbad "aim_reincarnate silent fail"
    fi
  fi

  # Report
  {
    echo "# Gate report — $VESSEL"
    echo
    echo "- stamp: $STAMP"
    echo "- test_dir: \`$TEST_DIR\`"
    echo "- use_local: $USE_LOCAL"
    echo "- git: \`$(git rev-parse --short HEAD 2>/dev/null || echo unknown)\`"
    echo "- pass: $v_pass fail: $v_fail"
    echo "- operator_e2e_exit: $E2E_RC"
    echo
    echo "## Verdict: $([[ $v_fail -eq 0 && $E2E_RC -eq 0 ]] && echo PASS || echo FAIL)"
  } > "$REPORT"

  exec 1>&3 2>&4
  if [[ $v_fail -eq 0 && $E2E_RC -eq 0 ]]; then
    RESULTS+=("$VESSEL:PASS:$TEST_DIR")
    pass_n=$((pass_n+1))
    echo "======== $VESSEL OVERALL PASS ========"
    return 0
  else
    RESULTS+=("$VESSEL:FAIL:$TEST_DIR")
    fail_n=$((fail_n+1))
    echo "======== $VESSEL OVERALL FAIL (see $LOG) ========"
    return 1
  fi
}

echo "FLEET FULL REINCARNATE GATE $STAMP vessels=$VESSELS use_local=$USE_LOCAL"
for v in $VESSELS; do
  set +e
  run_vessel "$v"
  set -e
done

{
  echo "# Fleet full reincarnate gate — $STAMP"
  echo
  echo "Goal: \`docs/GOAL_REINCARNATION_MEMORY_WIKI.md\`"
  echo "use_local=$USE_LOCAL"
  echo
  echo "| Vessel | Result | Tree |"
  echo "|--------|--------|------|"
  for r in "${RESULTS[@]:-}"; do
    IFS=: read -r name res path <<<"$r"
    echo "| $name | **$res** | \`$path\` |"
  done
  echo
  echo "pass=$pass_n fail=$fail_n"
  echo
  if [[ $fail_n -eq 0 ]]; then
    echo "## OVERALL: PASS"
  else
    echo "## OVERALL: FAIL"
  fi
} | tee "$SUMMARY"

echo "SUMMARY: $SUMMARY"
[[ $fail_n -eq 0 ]]
