#!/usr/bin/env python3
"""
Operator-style reincarnation → memory-wiki E2E (hard gates).

Simulates: Operator chats directives → pulse --session-id → wiki pages contain markers.
Exit 0 only on full pass. Exit 2 on fail.
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

VESSEL = Path(os.environ.get("AIM_VESSEL", "/home/kingb/grok-audit")).resolve()
AIM = VESSEL / "aim-agy_os"
VENV_PY = AIM / "venv" / "bin" / "python3"
SESS_ROOT = Path.home() / ".grok/sessions" / (
    __import__("urllib.parse").parse.quote(str(VESSEL), safe="")
)
WIKI = AIM / "memory-wiki"
REPORT = AIM / "planning-artifacts" / "OPERATOR_E2E_REINCARNATE_WIKI_LATEST.md"

MARKER = os.environ.get(
    "MARKER", f"OP_WIKI_TRUTH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)
DIRECTIVES = [
    f"OPERATOR_DIRECTIVE_1: Remember project codename PHOENIX_RIDGE for all future sessions. Marker={MARKER}",
    f"OPERATOR_DIRECTIVE_2: Always use CDP isolation port 9347 for LoopNet-class browsers. Marker={MARKER}",
    f"OPERATOR_DIRECTIVE_3: Never claim memory-wiki works without grepping for {MARKER}.",
]


def log(msg: str) -> None:
    print(msg, flush=True)


def write_jsonl(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def make_chat_history() -> list:
    rows = [
        {
            "type": "system",
            "content": "You are Grok 4.5. Operator E2E reincarnation vessel.",
        },
        {
            "type": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"<user_info>\nWorkspace Path: {VESSEL}\n</user_info>",
                }
            ],
            "synthetic_reason": "user_info",
        },
    ]
    turns = [
        "Wake up. We are testing reincarnation memory today.",
        DIRECTIVES[0],
        "Confirm you will put that in structural memory when we reincarnate.",
        DIRECTIVES[1],
        "Also lock this policy:",
        DIRECTIVES[2],
        "Before reincarnation: summarize the three directives back to me.",
        "ok, do the reincarnate now so the next vessel inherits these directives via memory-wiki.",
    ]
    for i, t in enumerate(turns):
        rows.append(
            {
                "type": "user",
                "content": [
                    {"type": "text", "text": f"<user_query>\n{t}\n</user_query>"}
                ],
            }
        )
        rows.append(
            {
                "type": "assistant",
                "content": f"Acknowledged turn {i+1}. Retaining: {t[:160]}",
            }
        )
    while len(rows) < 20:
        rows.append(
            {
                "type": "assistant",
                "content": f"padding {len(rows)} marker {MARKER}",
            }
        )
    return rows


def make_updates_with_directives(session_id: str) -> list:
    """Durable Grok stream shape including the Operator directives as chunks."""
    rows = []
    ts = int(time.time())

    def add_user(text: str) -> None:
        nonlocal ts
        for chunk in [text]:
            ts += 1
            rows.append(
                {
                    "timestamp": ts,
                    "method": "session/update",
                    "params": {
                        "sessionId": session_id,
                        "update": {
                            "sessionUpdate": "user_message_chunk",
                            "content": {"type": "text", "text": chunk},
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

    add_user("Wake up. We are testing reincarnation memory today.")
    add_agent("Ready for operator directives.")
    for d in DIRECTIVES:
        add_user(d)
        add_agent(f"Locked into memory plan: {d[:80]}")
    add_user(
        "ok, do the reincarnate now so the next vessel inherits these directives via memory-wiki."
    )
    add_agent("Starting reincarnation handoff with your three directives.")
    # pad tool noise so updates ≫ chat (prefer durable)
    for i in range(80):
        ts += 1
        rows.append(
            {
                "timestamp": ts,
                "method": "session/update",
                "params": {
                    "sessionId": session_id,
                    "update": {
                        "sessionUpdate": "tool_call_update",
                        "toolCallId": f"call-e2e-{i}",
                        "status": "in_progress",
                    },
                },
            }
        )
    return rows


def grep_marker_pages() -> list:
    hits = []
    pages = WIKI / "pages"
    if not pages.is_dir():
        return hits
    for p in pages.glob("*.md"):
        try:
            if MARKER in p.read_text(encoding="utf-8", errors="replace"):
                hits.append(str(p))
        except OSError:
            pass
    return hits


def main() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(AIM / ".aim_core") + os.pathsep + env.get(
        "PYTHONPATH", ""
    )
    env["AIM_WIKI_SKIP_LANCE"] = "1"  # speed; wiki pages are the hard gate

    session_id = "019fe2e1-opfx-4e2e-8e2e-" + hashlib.sha1(
        MARKER.encode()
    ).hexdigest()[:12]
    sess_dir = SESS_ROOT / session_id
    if sess_dir.exists():
        shutil.rmtree(sess_dir)
    sess_dir.mkdir(parents=True)

    chat = make_chat_history()
    updates = make_updates_with_directives(session_id)
    write_jsonl(sess_dir / "chat_history.jsonl", chat)
    write_jsonl(sess_dir / "updates.jsonl", updates)
    (sess_dir / "signals.json").write_text(
        json.dumps(
            {
                "compactionCount": 2,
                "contextWindowTokens": 500000,
                "contextTokensUsed": 200000,
            }
        ),
        encoding="utf-8",
    )
    (sess_dir / "summary.json").write_text(
        json.dumps(
            {
                "info": {"id": session_id, "cwd": str(VESSEL)},
                "session_summary": "Operator E2E reincarnation memory-wiki",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ),
        encoding="utf-8",
    )

    log(f"=== OPERATOR E2E marker={MARKER} session={session_id} vessel={VESSEL} ===")

    daemon_path = WIKI / "daemon.log"
    daemon_path.parent.mkdir(parents=True, exist_ok=True)
    daemon_offset = daemon_path.stat().st_size if daemon_path.exists() else 0

    cmd = [
        str(VENV_PY),
        str(AIM / ".aim_core" / "handoff_pulse_generator.py"),
        "--session-id",
        session_id,
    ]
    log("RUN: " + " ".join(cmd))
    p = subprocess.run(
        cmd, cwd=str(VESSEL), env=env, capture_output=True, text=True, timeout=180
    )
    log(p.stdout or "")
    log(p.stderr or "")
    log(f"pulse exit={p.returncode}")

    # Wait for daemon
    daemon_new = ""
    deadline = time.time() + 60
    while time.time() < deadline:
        if daemon_path.exists():
            daemon_new = daemon_path.read_bytes()[daemon_offset:].decode(
                "utf-8", errors="replace"
            )
            if "[SUCCESS]" in daemon_new or "[FATAL]" in daemon_new:
                # allow process_ingest to finish writing pages
                if "[SUCCESS]" in daemon_new:
                    time.sleep(1)
                break
        time.sleep(0.5)
    log("--- daemon delta ---")
    log(daemon_new[-2500:] if daemon_new else "(empty)")

    archives = list((AIM / "archive" / "history").glob(f"*_{session_id}.md"))
    archive_ok = False
    archive_path = None
    for a in archives:
        body = a.read_text(encoding="utf-8", errors="replace")
        if MARKER in body and "OPERATOR_DIRECTIVE" in body:
            archive_ok = True
            archive_path = str(a)
            break

    fr = AIM / ".aim_core" / "temp" / "LAST_SESSION_FLIGHT_RECORDER.md"
    fr_txt = fr.read_text(encoding="utf-8", errors="replace") if fr.exists() else ""
    fr_ok = MARKER in fr_txt

    page_hits = grep_marker_pages()
    pages_ok = len(page_hits) > 0
    daemon_ok = "[SUCCESS]" in daemon_new and "[FATAL]" not in daemon_new.split(
        "[SUCCESS]"
    )[-1][:200]
    # Allow FATAL vault warnings before SUCCESS
    daemon_ok = "[SUCCESS] Deterministic wiki reincarnation sequence complete." in daemon_new

    # Ensure we did NOT process wrong session
    wrong_session = "019f64b5" in (p.stdout or "") and session_id not in (p.stdout or "")

    gates = {
        "pulse_exit_0": p.returncode == 0,
        "exclusive_session_in_stdout": session_id in (p.stdout or ""),
        "archive_has_marker": archive_ok,
        "flight_recorder_has_marker": fr_ok,
        "daemon_success": daemon_ok,
        "wiki_pages_have_marker": pages_ok,
        "not_wrong_session": not wrong_session,
    }
    hard_pass = all(gates.values())

    report = [
        f"# Operator E2E (latest)",
        f"",
        f"**When:** {datetime.now(timezone.utc).isoformat()}",
        f"**Vessel:** `{VESSEL}`",
        f"**Marker:** `{MARKER}`",
        f"**Session:** `{session_id}`",
        f"**VERDICT:** **{'PASS' if hard_pass else 'FAIL'}**",
        f"",
        f"## Directives",
        *[f"- {d}" for d in DIRECTIVES],
        f"",
        f"## Gates",
        f"| Gate | Result |",
        f"|------|--------|",
        *[f"| `{k}` | **{v}** |" for k, v in gates.items()],
        f"",
        f"## Archive",
        f"`{archive_path}`",
        f"",
        f"## Wiki page hits",
        "\n".join(page_hits) or "(none)",
        f"",
        f"## Pulse stdout",
        f"```",
        (p.stdout or "")[-2000:],
        f"```",
        f"",
        f"## Daemon delta",
        f"```",
        daemon_new[-2000:],
        f"```",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    log(f"REPORT {REPORT}")
    log(f"=== VERDICT {'PASS' if hard_pass else 'FAIL'} gates={gates} ===")
    return 0 if hard_pass else 2


if __name__ == "__main__":
    sys.exit(main())
