"""
Vessel-scoped, project-scoped, timestamped tmux session names for spawned agents.

Contract (aim-grok #3 / multi-vessel hosts):
  {vessel}_{role}_{project_slug}_{timestamp}

Defaults on this vessel: vessel=``grok`` (override with ``AIM_VESSEL_CLI``).
"""
from __future__ import annotations

import hashlib
import os
import re
import time


def sanitize_token(value: str, *, max_len: int = 48) -> str:
    raw = (value or "").strip().lower()
    cleaned = "".join(c if c.isalnum() or c in "-_" else "_" for c in raw)
    cleaned = re.sub(r"[_-]{2,}", "_", cleaned).strip("_-")
    if not cleaned:
        return "x"
    return cleaned[:max_len]


def vessel_cli_id(env: dict | None = None) -> str:
    """aim-grok default is ``grok``. Override with AIM_VESSEL_CLI (agy, opencode, …)."""
    source = env if env is not None else os.environ
    raw = (source.get("AIM_VESSEL_CLI") or "grok").strip().lower()
    return sanitize_token(raw, max_len=32) or "grok"


def project_slug(
    project_root: str | None = None,
    env: dict | None = None,
) -> str:
    """Basename + short path hash so two checkouts with the same folder name don't collide."""
    source = env if env is not None else os.environ
    root = (
        project_root
        or source.get("AIM_WORKSPACE")
        or source.get("AIM_PROJECT_ROOT")
        or os.getcwd()
    )
    abspath = os.path.abspath(os.path.expanduser(str(root)))
    base = sanitize_token(os.path.basename(abspath) or "project", max_len=32)
    digest = hashlib.sha1(abspath.encode("utf-8")).hexdigest()[:6]
    return f"{base}-{digest}"


def agent_session_name(
    role: str,
    project_root: str | None = None,
    env: dict | None = None,
    *,
    timestamp: int | None = None,
) -> str:
    """Build ``{vessel}_{role}_{project_slug}_{unix_ts}`` for a new tmux agent session."""
    vessel = vessel_cli_id(env)
    role_s = sanitize_token(role, max_len=32) or "agent"
    slug = project_slug(project_root, env)
    ts = int(time.time()) if timestamp is None else int(timestamp)
    return f"{vessel}_{role_s}_{slug}_{ts}"


def reincarnation_session_name(
    project_root: str | None = None,
    env: dict | None = None,
    *,
    timestamp: int | None = None,
) -> str:
    return agent_session_name(
        "reincarnation", project_root=project_root, env=env, timestamp=timestamp
    )


def scribe_session_name(
    project_root: str | None = None,
    env: dict | None = None,
    *,
    timestamp: int | None = None,
) -> str:
    return agent_session_name(
        "scribe", project_root=project_root, env=env, timestamp=timestamp
    )


def wiki_session_name(
    project_root: str | None = None,
    env: dict | None = None,
    *,
    timestamp: int | None = None,
) -> str:
    return agent_session_name(
        "wiki", project_root=project_root, env=env, timestamp=timestamp
    )


def is_agent_session(
    name: str,
    role: str,
    env: dict | None = None,
    project_root: str | None = None,
    *,
    require_same_project: bool = False,
) -> bool:
    """True if *name* matches ``{vessel}_{role}_{slug}_{digits}`` for this vessel/role."""
    if not name:
        return False
    vessel = vessel_cli_id(env)
    role_s = sanitize_token(role, max_len=32) or "agent"
    prefix = f"{vessel}_{role_s}_"
    if not name.startswith(prefix):
        return False
    rest = name[len(prefix) :]
    if "_" not in rest:
        return False
    slug, ts = rest.rsplit("_", 1)
    if not re.fullmatch(r"[0-9]+", ts):
        return False
    if not slug:
        return False
    if require_same_project:
        return slug == project_slug(project_root, env)
    return True


def is_reincarnation_session(
    name: str,
    env: dict | None = None,
    project_root: str | None = None,
    *,
    require_same_project: bool = False,
) -> bool:
    return is_agent_session(
        name,
        "reincarnation",
        env=env,
        project_root=project_root,
        require_same_project=require_same_project,
    )


def session_prefix(role: str, env: dict | None = None) -> str:
    """Prefix suitable for shell greps: ``{vessel}_{role}_``."""
    return f"{vessel_cli_id(env)}_{sanitize_token(role)}_"
