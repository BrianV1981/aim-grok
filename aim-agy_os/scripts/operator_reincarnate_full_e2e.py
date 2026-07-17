#!/usr/bin/env python3
"""
Full reincarnation path E2E (pulse + vault + wake prompt) without tmux teleport.

Uses: ./aim reincarnate --session-id <id> --no-teleport
Hard gates match GOAL_REINCARNATION_MEMORY_WIKI + blackbox seal.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

VESSEL = Path(os.environ.get("AIM_VESSEL", "/home/kingb/aim-grok")).resolve()
AIM = VESSEL / "aim-agy_os"
VENV_PY = AIM / "venv" / "bin" / "python3"
SESS_ROOT = Path.home() / ".grok/sessions" / quote(str(VESSEL), safe="")
WIKI = AIM / "memory-wiki"
REPORT = AIM / "planning-artifacts" / "OPERATOR_E2E_REINCARNATE_FULL_LATEST.md"
MARKER = os.environ.get(
    "MARKER", f"OP_FULL_REIN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)


def log(msg: str) -> None:
    print(msg, flush=True)


def write_gameplan() -> None:
    temp = AIM / ".aim_core" / "temp"
    temp.mkdir(parents=True, exist_ok=True)
    gp = temp / "REINCARNATION_GAMEPLAN.md"
    gp.write_text(
        f"""### 1. The Commander's Summary
Full reincarnate E2E ({MARKER}). Pulse + vault; no teleport.

### 2. Tactical State
- **Active Ticket:** full-reincarnate-e2e
- **Branch:** main
- **Primary Files:** aim_reincarnate.py, blackbox_vault.py

### 3. The Localized Directory Map
`{VESSEL}`

### 4. Epistemic Warnings & Dead Ends
- Do not teleport in this harness.

### 5. Immediate Next Action
1. Verify wiki pages contain {MARKER}.
2. Verify vault sealed for session.
""",
        encoding="utf-8",
    )


def plant_session(session_id: str) -> Path:
    sess = SESS_ROOT / session_id
    if sess.exists():
        shutil.rmtree(sess)
    sess.mkdir(parents=True)
    rows = []
    ts = int(time.time())

    def add_user(text: str) -> None:
        nonlocal ts
        ts += 1
        rows.append(
            {
                "timestamp": ts,
                "method": "session/update",
                "params": {
                    "sessionId": session_id,
                    "update": {
                        "sessionUpdate": "user_message_chunk",
                        "content": {"type": "text", "text": text},
                    },
                },
            }
        )
        ts += 1
        rows.append(
            {
                "timestamp": ts,
                "method": "session/update",
                "params": {
                    "sessionId": session_id,
                    "update": {"sessionUpdate": "turn_completed"},
                },
            }
        )

    def add_agent(text: str) -> None:
        nonlocal ts
        ts += 1
        rows.append(
            {
                "timestamp": ts,
                "method": "session/update",
                "params": {
                    "sessionId": session_id,
                    "update": {
                        "sessionUpdate": "agent_message_chunk",
                        "content": {"type": "text", "text": text},
                    },
                },
            }
        )
        ts += 1
        rows.append(
            {
                "timestamp": ts,
                "method": "session/update",
                "params": {
                    "sessionId": session_id,
                    "update": {"sessionUpdate": "turn_completed"},
                },
            }
        )

    add_user("Wake. Full reincarnate E2E with no teleport.")
    add_agent("Ready.")
    for i, d in enumerate(
        [
            f"OPERATOR_DIRECTIVE_1: Codename FULL_REIN for grok. Marker={MARKER}",
            f"OPERATOR_DIRECTIVE_2: Seal blackbox on reincarnate. Marker={MARKER}",
            f"OPERATOR_DIRECTIVE_3: Wiki pages must hold {MARKER}.",
        ],
        1,
    ):
        add_user(d)
        add_agent(f"Locked directive {i}.")
    add_user("ok, reincarnate now with no teleport.")
    add_agent("Running reincarnate --no-teleport pipeline.")
    with (sess / "updates.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    (sess / "chat_history.jsonl").write_text(
        json.dumps(
            {
                "type": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"<user_query>\nFull rein {MARKER}\n</user_query>",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return sess


def main() -> int:
    session_id = "019fe2e1-full-4e2e-8e2e-" + hashlib.sha1(
        MARKER.encode()
    ).hexdigest()[:12]
    plant_session(session_id)
    write_gameplan()

    daemon = WIKI / "daemon.log"
    WIKI.mkdir(parents=True, exist_ok=True)
    off = daemon.stat().st_size if daemon.exists() else 0

    env = os.environ.copy()
    env["PYTHONPATH"] = str(AIM / ".aim_core") + os.pathsep + env.get("PYTHONPATH", "")
    env["AIM_WIKI_SKIP_LANCE"] = "1"
    env["AIM_WORKSPACE"] = str(VESSEL)
    env["AIM_REINCARNATE_NO_TELEPORT"] = "1"

    py = str(VENV_PY if VENV_PY.is_file() else sys.executable)
    cmd = [
        py,
        str(AIM / ".aim_core" / "aim_reincarnate.py"),
        "--session-id",
        session_id,
        "--no-teleport",
    ]
    log(f"=== FULL REIN E2E marker={MARKER} session={session_id} ===")
    log("RUN: " + " ".join(cmd))
    p = subprocess.run(
        cmd, cwd=str(VESSEL), env=env, capture_output=True, text=True, timeout=180
    )
    log(p.stdout or "")
    log(p.stderr or "")
    log(f"reincarnate exit={p.returncode}")

    # wait wiki
    daemon_new = ""
    deadline = time.time() + 60
    while time.time() < deadline:
        if daemon.exists():
            daemon_new = daemon.read_bytes()[off:].decode("utf-8", "replace")
            if "[SUCCESS] Deterministic" in daemon_new:
                time.sleep(0.8)
                break
        time.sleep(0.4)

    page_hits = []
    for pg in (WIKI / "pages").glob("*.md") if (WIKI / "pages").is_dir() else []:
        if MARKER in pg.read_text(errors="replace"):
            page_hits.append(str(pg))

    archives = list((AIM / "archive" / "history").glob(f"*_{session_id}.md"))
    arch_ok = any(MARKER in a.read_text(errors="replace") for a in archives)

    box = VESSEL / "archive" / ".raw_jsonl_blackbox"
    enc = box / f"{session_id}.enc"
    man = box / "manifest.jsonl"
    vault_ok = enc.is_file() and man.is_file() and session_id in man.read_text(
        errors="replace"
    )

    wake = AIM / ".aim_core" / "temp" / "LAST_WAKE_PROMPT.md"
    wake_ok = wake.is_file() and wake.stat().st_size > 20

    success_n = daemon_new.count(
        "[SUCCESS] Deterministic wiki reincarnation sequence complete."
    )
    config_n = daemon_new.count("[OK] session_summarizer loaded CONFIG")

    gates = {
        "reincarnate_exit_0": p.returncode == 0,
        "no_teleport_in_stdout": "--no-teleport" in (p.stdout or "")
        or "no teleport" in (p.stdout or "").lower(),
        "archive_marker": arch_ok,
        "wiki_pages_marker": len(page_hits) > 0,
        "daemon_success": success_n >= 1,
        "daemon_no_double_success": success_n == 1,
        "daemon_no_double_config": config_n == 1,
        "vault_sealed": vault_ok,
        "wake_prompt_written": wake_ok,
    }
    hard = all(gates.values())

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        f"# Full Reincarnate E2E (no teleport)\n\n"
        f"**VERDICT: {'PASS' if hard else 'FAIL'}**\n\n"
        f"marker={MARKER}\nsession={session_id}\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in gates.items())
        + f"\n\nsuccess_n={success_n} config_n={config_n}\n"
        + "\npages:\n"
        + "\n".join(page_hits)
        + f"\n\nstdout:\n{(p.stdout or '')[-2000:]}\n"
        + f"\n\ndaemon:\n{daemon_new[-1500:]}\n",
        encoding="utf-8",
    )
    log(f"=== VERDICT {'PASS' if hard else 'FAIL'} {gates} ===")
    return 0 if hard else 2


if __name__ == "__main__":
    sys.exit(main())
