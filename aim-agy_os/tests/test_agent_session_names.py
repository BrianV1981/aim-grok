"""TDD: vessel+role+project+timestamp tmux agent names (aim-grok #3)."""
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

CORE = Path(__file__).resolve().parents[1] / ".aim_core"
sys.path.insert(0, str(CORE))

from agent_session_names import (  # noqa: E402
    agent_session_name,
    is_agent_session,
    is_reincarnation_session,
    project_slug,
    reincarnation_session_name,
    scribe_session_name,
    session_prefix,
    vessel_cli_id,
    wiki_session_name,
)


def test_default_vessel_is_grok():
    assert vessel_cli_id({}) == "grok"
    assert vessel_cli_id({"AIM_VESSEL_CLI": ""}) == "grok"


def test_vessel_from_env():
    assert vessel_cli_id({"AIM_VESSEL_CLI": "agy"}) == "agy"
    assert vessel_cli_id({"AIM_VESSEL_CLI": "OpenCode"}) == "opencode"


def test_project_slug_disambiguates_same_basename(tmp_path):
    a = tmp_path / "aim-grok"
    b = tmp_path / "other" / "aim-grok"
    a.mkdir()
    b.mkdir(parents=True)
    sa = project_slug(str(a), {})
    sb = project_slug(str(b), {})
    assert sa != sb
    assert sa.startswith("aim-grok-")
    assert sb.startswith("aim-grok-")


def test_full_contract_shape():
    name = agent_session_name(
        "scribe",
        project_root="/home/kingb/aim-grok",
        env={"AIM_VESSEL_CLI": "grok"},
        timestamp=1783840823,
    )
    # grok_scribe_<slug>_1783840823
    assert name.startswith("grok_scribe_")
    assert name.endswith("_1783840823")
    assert "scribe_agent_aim" not in name
    assert re.fullmatch(r"grok_scribe_[a-z0-9_-]+_1783840823", name)


def test_role_builders():
    env = {"AIM_VESSEL_CLI": "grok"}
    root = "/home/kingb/aim-grok"
    r = reincarnation_session_name(root, env, timestamp=1)
    s = scribe_session_name(root, env, timestamp=1)
    w = wiki_session_name(root, env, timestamp=1)
    assert "_reincarnation_" in r
    assert "_scribe_" in s
    assert "_wiki_" in w
    assert r != s != w
    assert is_reincarnation_session(r, env)
    assert is_agent_session(s, "scribe", env)
    assert is_agent_session(w, "wiki", env)


def test_legacy_global_scribe_rejected():
    assert not is_agent_session("scribe_agent_aim", "scribe", {"AIM_VESSEL_CLI": "grok"})
    assert not is_reincarnation_session(
        "aim_reincarnation_123", {"AIM_VESSEL_CLI": "grok"}
    )


def test_vessels_do_not_match_each_other():
    name = reincarnation_session_name(
        "/x/aim-grok", {"AIM_VESSEL_CLI": "grok"}, timestamp=9
    )
    assert is_reincarnation_session(name, {"AIM_VESSEL_CLI": "grok"})
    assert not is_reincarnation_session(name, {"AIM_VESSEL_CLI": "agy"})


def test_session_prefix_for_greps():
    assert session_prefix("reincarnation", {"AIM_VESSEL_CLI": "grok"}) == (
        "grok_reincarnation_"
    )


def test_live_timestamp_numeric():
    before = int(time.time())
    name = scribe_session_name("/tmp/proj", {"AIM_VESSEL_CLI": "grok"})
    after = int(time.time())
    ts = int(name.rsplit("_", 1)[-1])
    assert before <= ts <= after


@pytest.mark.skipif(
    subprocess.run(["which", "tmux"], capture_output=True).returncode != 0,
    reason="tmux not installed",
)
def test_tmux_accepts_namespaced_session():
    name = agent_session_name(
        "scribe",
        project_root="/home/kingb/aim-grok",
        env={"AIM_VESSEL_CLI": "grok"},
        timestamp=int(time.time()),
    )
    subprocess.run(["tmux", "kill-session", "-t", name], capture_output=True)
    try:
        r = subprocess.run(
            ["tmux", "new-session", "-d", "-s", name, "sleep", "15"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert r.returncode == 0, r.stderr
        listed = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        ).stdout
        assert name in listed.splitlines()
    finally:
        subprocess.run(["tmux", "kill-session", "-t", name], capture_output=True)
