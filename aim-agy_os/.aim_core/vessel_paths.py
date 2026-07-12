#!/usr/bin/env python3
"""
Vessel path resolution for multi-CLI A.I.M. (Grok primary on aim-grok, AGY fallback).

Grok session layout (observed):
  ~/.grok/sessions/<urlencode(cwd)>/<session_id>/chat_history.jsonl

Antigravity layout (legacy):
  ~/.gemini/antigravity-cli/brain/<session_id>/.system_generated/logs/transcript.jsonl
"""
from __future__ import annotations

import glob
import os
import urllib.parse
from typing import List, Optional


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


def find_grok_transcripts(
    project_root: str,
    explicit_session_id: Optional[str] = None,
) -> List[str]:
    """Return chat_history.jsonl paths for this workspace, newest first."""
    found: List[str] = []
    ws_dir = grok_workspace_session_dir(project_root)

    if explicit_session_id:
        # Direct session folder under workspace encode
        candidate = os.path.join(ws_dir, explicit_session_id, "chat_history.jsonl")
        if os.path.isfile(candidate):
            found.append(candidate)
        # Also allow bare path under sessions root
        candidate2 = os.path.join(grok_sessions_root(), explicit_session_id, "chat_history.jsonl")
        if os.path.isfile(candidate2) and candidate2 not in found:
            found.append(candidate2)

    if os.path.isdir(ws_dir):
        pattern = os.path.join(ws_dir, "*", "chat_history.jsonl")
        for path in glob.glob(pattern):
            if path not in found:
                found.append(path)

    # Fallback: any chat_history under sessions (last resort)
    if not found and os.path.isdir(grok_sessions_root()):
        pattern = os.path.join(grok_sessions_root(), "*", "*", "chat_history.jsonl")
        found.extend(glob.glob(pattern))

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
            import json

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
) -> List[str]:
    """
    Discover session transcripts.

    prefer:
      - "grok": Grok only
      - "agy": Antigravity only
      - "auto": Grok first if any, else AGY (default for aim-grok vessel)
    """
    prefer = (prefer or "auto").lower()
    if prefer == "grok":
        return find_grok_transcripts(project_root, explicit_session_id)
    if prefer == "agy":
        return find_agy_transcripts(project_root, explicit_session_id)

    grok = find_grok_transcripts(project_root, explicit_session_id)
    if grok:
        return grok
    return find_agy_transcripts(project_root, explicit_session_id)


def default_tmp_chats_dir() -> str:
    return grok_sessions_root()
