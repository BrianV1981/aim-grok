"""Compat shim: prefer soul session_naming.py (Grok default vessel)."""
from __future__ import annotations

from session_naming import (  # noqa: F401
    build_agent_session_name,
    is_agent_session_role,
    reincarnation_session_name,
    vessel_cli_id,
)

# Aliases used by earlier grok #3 API
def project_slug(project_root=None, env=None):
    from session_naming import get_project_slug
    return get_project_slug(project_root)

def agent_session_name(role, project_root=None, env=None, *, timestamp=None):
    return build_agent_session_name(role, workspace_dir=project_root, env=env, timestamp=timestamp)

def scribe_session_name(project_root=None, env=None, *, timestamp=None):
    return agent_session_name("scribe", project_root=project_root, env=env, timestamp=timestamp)

def wiki_session_name(project_root=None, env=None, *, timestamp=None):
    return agent_session_name("wiki", project_root=project_root, env=env, timestamp=timestamp)

def is_agent_session(name, role, env=None, project_root=None, *, require_same_project=False):
    return is_agent_session_role(name, role, env=env)

def is_reincarnation_session(name, env=None, project_root=None, *, require_same_project=False):
    return is_agent_session_role(name, "reincarnate", env=env) or is_agent_session_role(
        name, "reincarnation", env=env
    )

def session_prefix(role, env=None):
    return f"{vessel_cli_id(env)}_{role}_"
