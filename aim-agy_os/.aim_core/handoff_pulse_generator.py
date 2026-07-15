#!/usr/bin/env python3
"""Handoff / pulse: extract session signal → flight recorder + archive → wiki daemon."""
from config_utils import PROJECT_ROOT
import os
import json
import sys
import glob
from datetime import datetime
from reasoning_utils import AIM_ROOT
import argparse

try:
    from extract_signal import (
        extract_signal,
        skeleton_to_markdown,
        conversational_turn_count,
    )
except ImportError:
    sys.path.append(os.path.join(AIM_ROOT, ".aim_core"))
    from extract_signal import (
        extract_signal,
        skeleton_to_markdown,
        conversational_turn_count,
    )

CONFIG_PATH = os.path.join(PROJECT_ROOT, ".aim_core/CONFIG.json")
CONFIG = {}
if os.path.isfile(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r") as f:
            CONFIG = json.load(f)
    except Exception as e:
        print(f"Handoff Generator: Warning loading CONFIG.json: {e}")
else:
    print(
        f"Handoff Generator: No CONFIG at {CONFIG_PATH}; using defaults (vessel paths only)"
    )

CONTINUITY_DIR = os.path.join(AIM_ROOT, ".aim_core", "temp")
ARCHIVE_RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")
os.makedirs(CONTINUITY_DIR, exist_ok=True)
os.makedirs(ARCHIVE_RAW_DIR, exist_ok=True)

MIN_CONVERSATIONAL_TURNS = 1


def atomic_write(file_path, content):
    temp_path = f"{file_path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, file_path)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def _resolve_session_id(transcript_path: str) -> str:
    try:
        from vessel_paths import session_id_from_transcript_path

        return session_id_from_transcript_path(transcript_path)
    except Exception:
        base = os.path.basename(transcript_path)
        if base in ("chat_history.jsonl", "updates.jsonl", "transcript.jsonl"):
            return os.path.basename(os.path.dirname(transcript_path))
        return base.replace(".jsonl", "")


def _extract_with_fallback(transcript_path: str):
    """Extract signal; if updates empty, try sibling chat_history."""
    skeleton = extract_signal(transcript_path)
    turns = conversational_turn_count(skeleton)
    used = transcript_path
    if turns < MIN_CONVERSATIONAL_TURNS and transcript_path.endswith("updates.jsonl"):
        chat = os.path.join(os.path.dirname(transcript_path), "chat_history.jsonl")
        if os.path.isfile(chat):
            sk2 = extract_signal(chat)
            t2 = conversational_turn_count(sk2)
            if t2 > turns:
                print(
                    f"Handoff Generator: updates.jsonl yielded {turns} turns; "
                    f"falling back to chat_history.jsonl ({t2} turns)"
                )
                skeleton, turns, used = sk2, t2, chat
    return skeleton, turns, used


def generate_handoff_pulse(explicit_session_id=None) -> int:
    """
    Extract session signal, write archive + flight recorder, trigger wiki daemon.
    Returns 0 on success, 1 on hard failure (empty signal / no transcripts).
    """
    project_dir = os.path.abspath(PROJECT_ROOT if PROJECT_ROOT else AIM_ROOT)
    raw_files = []

    try:
        from vessel_paths import find_session_transcripts

        raw_files = find_session_transcripts(
            project_dir,
            explicit_session_id=explicit_session_id,
            prefer="auto",
        )
        if raw_files:
            print(
                f"Handoff Generator: Found {len(raw_files)} transcript(s) via vessel_paths"
            )
            if explicit_session_id:
                print(
                    f"Handoff Generator: EXCLUSIVE session_id={explicit_session_id}"
                )
    except Exception as e:
        print(
            f"Handoff Generator: vessel_paths unavailable ({e}); using legacy AGY paths"
        )

    if not raw_files and explicit_session_id:
        path = os.path.expanduser(
            f"~/.gemini/antigravity-cli/brain/{explicit_session_id}/"
            f".system_generated/logs/transcript.jsonl"
        )
        if os.path.exists(path):
            raw_files.append(path)
            print(
                f"Handoff Generator: Using explicit AGY session ID {explicit_session_id}"
            )

    if not raw_files and not explicit_session_id:
        history_file = os.path.expanduser("~/.gemini/antigravity-cli/history.jsonl")
        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        if data.get("workspace") == project_dir:
                            cid = data.get("conversationId")
                            path = os.path.expanduser(
                                f"~/.gemini/antigravity-cli/brain/{cid}/"
                                f".system_generated/logs/transcript.jsonl"
                            )
                            if cid and os.path.exists(path) and path not in raw_files:
                                raw_files.append(path)
            except Exception as e:
                print(f"Handoff Generator: Warning reading history: {e}")

    if not raw_files and not explicit_session_id:
        raw_files = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.jsonl"))

    if not raw_files:
        print(
            "Handoff Generator: [FATAL] No raw transcripts found "
            f"(session_id={explicit_session_id!r})."
        )
        return 1

    raw_files.sort(key=os.path.getmtime, reverse=True)
    latest_transcript = raw_files[0]

    # Anti-cannibalization ONLY when NOT targeting an explicit session
    if not explicit_session_id and len(raw_files) > 1:
        try:
            with open(latest_transcript, "r") as f:
                valid_lines = [line for line in f if line.strip()]
            if len(valid_lines) < 15:
                print(
                    f"Handoff Generator: {os.path.basename(latest_transcript)} has "
                    f"< 15 lines. Skipping to previous session (anti-cannibalization)."
                )
                latest_transcript = raw_files[1]
        except Exception:
            pass

    try:
        skeleton, turn_count, latest_transcript = _extract_with_fallback(
            latest_transcript
        )
        session_id = _resolve_session_id(latest_transcript)
        print(
            f"Handoff Generator: session_id={session_id} source={latest_transcript} "
            f"conversational_turns={turn_count}"
        )

        if turn_count < MIN_CONVERSATIONAL_TURNS:
            print(
                "Handoff Generator: [FATAL] Zero conversational turns extracted. "
                "Refusing empty archive / false HANDOFF READY."
            )
            # Still write a tiny diagnostic for debugging, but do NOT trigger wiki SUCCESS path
            os.makedirs(CONTINUITY_DIR, exist_ok=True)
            diag = (
                f"# HANDOFF FAILED — empty signal\n\n"
                f"- session_id: `{session_id}`\n"
                f"- source: `{latest_transcript}`\n"
                f"- turns: {turn_count}\n"
            )
            with open(
                os.path.join(CONTINUITY_DIR, "CURRENT_PULSE.md"), "w", encoding="utf-8"
            ) as f:
                f.write(diag)
            return 1

        if explicit_session_id and session_id != explicit_session_id:
            # path might be under nested encoding; require id in path
            if explicit_session_id not in latest_transcript:
                print(
                    f"Handoff Generator: [FATAL] Resolved session {session_id} "
                    f"!= requested {explicit_session_id}"
                )
                return 1

        md_content = skeleton_to_markdown(skeleton, session_id)
        os.makedirs(CONTINUITY_DIR, exist_ok=True)
        clean_path = os.path.join(CONTINUITY_DIR, "LAST_SESSION_FLIGHT_RECORDER.md")

        now = datetime.now()
        file_ts = now.strftime("%Y-%m-%d_%H%M")
        archive_dir = os.path.join(AIM_ROOT, "archive/history")
        os.makedirs(archive_dir, exist_ok=True)
        archive_path = os.path.join(archive_dir, f"{file_ts}_{session_id}.md")
        atomic_write(archive_path, md_content)
        print(f"      Historical Archive updated: {archive_path}")

        tail_lines = CONFIG.get("settings", {}).get("handoff_context_lines", 0)
        if tail_lines and tail_lines > 0:
            md_lines = md_content.splitlines()
            truncated = (
                md_lines[-tail_lines:] if len(md_lines) > tail_lines else md_lines
            )
            clean_content = (
                "# A.I.M. Session Flight Recorder (Rolling Delta)\n"
                f"*Last {tail_lines} lines only. NOT auto-injected into LLM context.*\n\n"
                + "\n".join(truncated)
                + "\n"
            )
        else:
            clean_content = (
                "# A.I.M. Session Flight Recorder (Full History)\n"
                "*NOT automatically injected into LLM context.*\n\n"
                + md_content
                + "\n"
            )
        atomic_write(clean_path, clean_content)

        cognitive_mode = CONFIG.get("settings", {}).get("cognitive_mode", "monolithic")
        vault_path = CONFIG.get("settings", {}).get("obsidian_vault_path", "")
        if cognitive_mode == "frontline" and vault_path:
            inbox_dir = os.path.join(vault_path, "AIM_Inbox")
            os.makedirs(inbox_dir, exist_ok=True)
            atomic_write(os.path.join(inbox_dir, f"{session_id}.md"), md_content)
            print(
                f"      [Frontline] Dropped Markdown session {session_id} into Obsidian AIM_Inbox."
            )
        elif cognitive_mode == "monolithic":
            import subprocess

            try:
                log_path = os.path.join(AIM_ROOT, "memory-wiki", "daemon.log")
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                daemon_log = open(log_path, "a")
                daemon_log.write(
                    f"\n--- handoff spawn {datetime.now().isoformat()} "
                    f"archive={archive_path} ---\n"
                )
                daemon_log.flush()
                subprocess.Popen(
                    [
                        sys.executable,
                        os.path.join(AIM_ROOT, "hooks", "session_summarizer.py"),
                        "--reincarnate",
                        archive_path,
                        "--bg",
                    ],
                    stdout=daemon_log,
                    stderr=daemon_log,
                    start_new_session=True,
                )
                print(
                    "      [Monolithic] Triggered wiki daemon "
                    "(memory-wiki/daemon.log)."
                )
            except Exception as e:
                print(f"      [Monolithic] Subconscious daemon error: {e}")

        pulse_turns = []
        if isinstance(skeleton, list):
            for turn in skeleton:
                role = turn.get("role", "unknown").upper()
                text = (turn.get("text") or "").strip()
                if role in ("USER", "GEMINI", "MODEL", "ASSISTANT", "AGY") and text:
                    pulse_turns.append(turn)

        last_5 = pulse_turns[-5:]
        pulse_content = "## Last 5 Conversational Turns\n\n"
        for turn in last_5:
            role_label = (
                "USER" if turn.get("role", "").upper() == "USER" else "A.I.M."
            )
            ts = turn.get("timestamp", "")
            text = (turn.get("text") or "").strip()
            pulse_content += f"### {role_label} ({ts})\n{text}\n\n---\n\n"
        if not last_5:
            pulse_content += "*(No conversational turns found)*\n\n"

        pulse_path = os.path.join(CONTINUITY_DIR, "CURRENT_PULSE.md")
        with open(pulse_path, "w", encoding="utf-8") as f:
            f.write(pulse_content)

        print("\n\033[92m--- A.I.M. HANDOFF READY ---\033[0m")
        return 0

    except Exception as e:
        print(f"Handoff Generator: Signal extraction failure: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A.I.M. Handoff Pulse Generator")
    parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="Exclusive conversation UUID (required for targeted reincarnation).",
    )
    args = parser.parse_args()
    rc = generate_handoff_pulse(explicit_session_id=args.session_id)
    sys.exit(rc)
