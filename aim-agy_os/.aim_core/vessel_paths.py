#!/usr/bin/env python3
"""
Vessel path resolution for multi-CLI A.I.M. (Grok primary on aim-grok, AGY fallback).

Grok session layout (observed):
  ~/.grok/sessions/<urlencode(cwd)>/<session_id>/chat_history.jsonl
  ~/.grok/sessions/<urlencode(cwd)>/<session_id>/updates.jsonl   # durable; survives compact
  ~/.grok/sessions/<urlencode(cwd)>/<session_id>/signals.json    # compactionCount, etc.

Antigravity layout (legacy):
  ~/.gemini/antigravity-cli/brain/<session_id>/.system_generated/logs/transcript.jsonl
"""
from __future__ import annotations

import glob
import json
import os
import urllib.parse
from typing import List, Optional, Tuple


def grok_sessions_root() -> str:
    return os.path.expanduser("~/.grok/sessions")


def agy_brain_root() -> str:
    return os.path.expanduser("~/.gemini/antigravity-cli/brain")


def encode_workspace_cwd(cwd: str) -> str:
    """Match Grok's session directory naming: URL-encode absolute path."""
    abs_cwd = os.path.abspath(cwd)
    return urllib.parse.quote(abs_cwd, safe="")


def grok_workspace_session_dir(project_root: str) -> str:
    return os.path.join(grok_sessions_root(), encode_workspace_cwd(project_root))


def session_id_from_transcript_path(path: str) -> str:
    """
    Prefer parent directory UUID when file is a known log basename.
    e.g. .../019f5545-…/chat_history.jsonl → 019f5545-…
         .../019f5545-…/updates.jsonl → 019f5545-…
    """
    base = os.path.basename(path)
    if base in (
        "chat_history.jsonl",
        "updates.jsonl",
        "transcript.jsonl",
        "history.jsonl",
    ):
        return os.path.basename(os.path.dirname(path))
    stem = base.replace(".jsonl", "")
    if stem in ("chat_history", "updates", "transcript", "history"):
        return os.path.basename(os.path.dirname(path))
    return stem


def _signals_prefer_updates(session_dir: str) -> bool:
    signals = os.path.join(session_dir, "signals.json")
    if not os.path.isfile(signals):
        return False
    try:
        with open(signals, "r", encoding="utf-8") as f:
            data = json.load(f)
        return int(data.get("compactionCount") or 0) > 0
    except Exception:
        return False


def _pick_grok_log_in_session(session_dir: str) -> Optional[str]:
    """Prefer durable updates.jsonl when larger or compactionCount > 0."""
    updates = os.path.join(session_dir, "updates.jsonl")
    chat = os.path.join(session_dir, "chat_history.jsonl")
    has_u = os.path.isfile(updates)
    has_c = os.path.isfile(chat)
    if has_u and has_c:
        try:
            u_sz = os.path.getsize(updates)
            c_sz = os.path.getsize(chat)
        except OSError:
            u_sz = c_sz = 0
        if _signals_prefer_updates(session_dir) or u_sz > max(c_sz * 2, 50_000):
            return updates
        return chat
    if has_u:
        return updates
    if has_c:
        return chat
    return None


def find_grok_transcripts(
    project_root: str,
    explicit_session_id: Optional[str] = None,
    prefer_durable: bool = True,
) -> List[str]:
    """Return Grok transcript paths for this workspace, newest first."""
    found: List[str] = []
    seen = set()
    ws_dir = grok_workspace_session_dir(project_root)

    def _add(path: Optional[str]) -> None:
        if path and os.path.isfile(path) and path not in seen:
            seen.add(path)
            found.append(path)

    def _session_pick(session_dir: str) -> None:
        if prefer_durable:
            _add(_pick_grok_log_in_session(session_dir))
        else:
            chat = os.path.join(session_dir, "chat_history.jsonl")
            if os.path.isfile(chat):
                _add(chat)
            else:
                _add(_pick_grok_log_in_session(session_dir))

    if explicit_session_id:
        for base in (ws_dir, grok_sessions_root()):
            _session_pick(os.path.join(base, explicit_session_id))

    if os.path.isdir(ws_dir):
        for entry in glob.glob(os.path.join(ws_dir, "*")):
            if os.path.isdir(entry):
                _session_pick(entry)

    if not found and os.path.isdir(grok_sessions_root()):
        for entry in glob.glob(os.path.join(grok_sessions_root(), "*", "*")):
            if os.path.isdir(entry):
                _session_pick(entry)

    found.sort(key=os.path.getmtime, reverse=True)
    return found


def find_agy_transcripts(
    project_root: str,
    explicit_session_id: Optional[str] = None,
) -> List[str]:
    """Return AGY transcript.jsonl paths, newest first."""
    found: List[str] = []
    brain = agy_brain_root()

    if explicit_session_id:
        path = os.path.join(
            brain, explicit_session_id, ".system_generated", "logs", "transcript.jsonl"
        )
        if os.path.isfile(path):
            found.append(path)

    history_file = os.path.expanduser("~/.gemini/antigravity-cli/history.jsonl")
    if os.path.isfile(history_file):
        try:
            project_dir = os.path.abspath(project_root)
            with open(history_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if data.get("workspace") != project_dir:
                        continue
                    cid = data.get("conversationId")
                    if not cid:
                        continue
                    path = os.path.join(
                        brain, cid, ".system_generated", "logs", "transcript.jsonl"
                    )
                    if os.path.isfile(path) and path not in found:
                        found.append(path)
        except Exception:
            pass

    if not found and os.path.isdir(brain):
        pattern = os.path.join(brain, "*", ".system_generated", "logs", "*.jsonl")
        found.extend(glob.glob(pattern))

    found.sort(key=os.path.getmtime, reverse=True)
    return found


def find_session_transcripts(
    project_root: str,
    explicit_session_id: Optional[str] = None,
    prefer: str = "auto",
    prefer_durable: bool = True,
) -> List[str]:
    """
    Discover session transcripts.

    prefer:
      - "grok": Grok only
      - "agy": Antigravity only
      - "auto": Grok first if any, else AGY (default for aim-grok vessel)
    prefer_durable: when True, Grok prefers updates.jsonl after compaction.
    """
    prefer = (prefer or "auto").lower()
    if prefer == "grok":
        return find_grok_transcripts(
            project_root, explicit_session_id, prefer_durable=prefer_durable
        )
    if prefer == "agy":
        return find_agy_transcripts(project_root, explicit_session_id)

    grok = find_grok_transcripts(
        project_root, explicit_session_id, prefer_durable=prefer_durable
    )
    if grok:
        return grok
    return find_agy_transcripts(project_root, explicit_session_id)


def default_tmp_chats_dir() -> str:
    return grok_sessions_root()
