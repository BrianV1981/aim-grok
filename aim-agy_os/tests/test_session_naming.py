"""TDD coverage for vessel-prefixed tmux session names (soul API; grok default)."""
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

CORE = Path(__file__).resolve().parents[1] / ".aim_core"
sys.path.insert(0, str(CORE))

from session_naming import (  # noqa: E402
    build_agent_session_name,
    get_project_slug,
    is_agent_session_role,
    is_reincarnation_session,
    reincarnation_session_name,
    vessel_cli_id,
)


def test_default_vessel_is_grok():
    """aim-grok overlay: default vessel id is grok (agy tree defaults to agy)."""
    assert vessel_cli_id({}) == "grok"
    assert vessel_cli_id({"AIM_VESSEL_CLI": ""}) == "grok"


def test_vessel_cli_from_env():
    assert vessel_cli_id({"AIM_VESSEL_CLI": "agy"}) == "agy"
    assert vessel_cli_id({"AIM_VESSEL_CLI": "OpenCode"}) == "opencode"


def test_get_project_slug():
    assert get_project_slug("/path/to/my-cool-project") == "my-cool-project"
    assert get_project_slug("/path/to/my_project_123") == "my_project_123"


def test_build_agent_session_name():
    name = build_agent_session_name(
        "scribe", "/home/workspace/test-project", {}, timestamp=1783840823
    )
    assert name == "grok_scribe_test-project_1783840823"

    name2 = build_agent_session_name(
        "wiki", "/home/workspace/foo", {"AIM_VESSEL_CLI": "agy"}, timestamp=99
    )
    assert name2 == "agy_wiki_foo_99"


def test_is_agent_session_role():
    env = {"AIM_VESSEL_CLI": "grok"}
    assert is_agent_session_role("grok_scribe_test_123", "scribe", env)
    assert not is_agent_session_role("grok_wiki_test_123", "scribe", env)
    assert not is_agent_session_role("agy_scribe_test_123", "scribe", env)


def test_reincarnation_legacy_wrap():
    name = reincarnation_session_name(
        "/home/workspace/test-project", {}, timestamp=123
    )
    assert name == "grok_reincarnate_test-project_123"
    assert is_reincarnation_session("grok_reincarnate_test-project_123", {})
    assert not is_reincarnation_session("grok_reincarnation_123", {})


@pytest.mark.skipif(
    subprocess.run(["which", "tmux"], capture_output=True).returncode != 0,
    reason="tmux not installed",
)
def test_tmux_e2e_session_visible_under_vessel_prefix():
    name = build_agent_session_name(
        "testrole",
        "/tmp/project",
        {"AIM_VESSEL_CLI": "grok"},
        timestamp=int(time.time()),
    )
    assert re.fullmatch(r"grok_testrole_project_[0-9]+", name)
    subprocess.run(["tmux", "kill-session", "-t", name], capture_output=True)
    try:
        r = subprocess.run(
            ["tmux", "new-session", "-d", "-s", name, "sleep", "30"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert r.returncode == 0, r.stderr
        listed = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        ).stdout
        assert name in listed.splitlines()
    finally:
        subprocess.run(["tmux", "kill-session", "-t", name], capture_output=True)
