"""Smoke tests for the aim-grok vessel / A.I.M. engine layout."""
import os
import subprocess
import sys
from pathlib import Path

# Engine layout: tests live at aim-agy_os/tests/ → parent is OS root
OS_ROOT = Path(__file__).resolve().parents[1]
CORE = OS_ROOT / ".aim_core"
VESSEL_ROOT = OS_ROOT.parent
AIM_WRAPPER = VESSEL_ROOT / "aim"


def test_core_layout():
    assert (CORE / "aim_cli.py").is_file()
    assert (CORE / "aim_doctor.py").is_file()
    assert (CORE / "vessel_paths.py").is_file()
    assert (CORE / "wiki_tools.py").is_file()
    assert (CORE / "wiki_compiler.py").is_file()
    assert (CORE / "config_utils.py").is_file()


def test_import_config_and_vessel_paths():
    sys.path.insert(0, str(CORE))
    sys.path.insert(0, str(OS_ROOT))
    import config_utils
    import vessel_paths

    root = config_utils.find_project_root()
    assert root == str(VESSEL_ROOT) or (Path(root) / "aim-agy_os").is_dir()
    assert hasattr(vessel_paths, "find_session_transcripts")
    assert hasattr(vessel_paths, "grok_sessions_root")


def test_aim_wrapper_doctor():
    """End-to-end: ./aim doctor must succeed in a healthy vessel install."""
    if not AIM_WRAPPER.is_file():
        # Engine-only checkout without vessel wrapper
        return
    venv_py = OS_ROOT / "venv" / "bin" / "python3"
    if not venv_py.is_file():
        return
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{OS_ROOT}:{CORE}" + (
        f":{env['PYTHONPATH']}" if env.get("PYTHONPATH") else ""
    )
    r = subprocess.run(
        [str(AIM_WRAPPER), "doctor"],
        cwd=str(VESSEL_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "DOCTOR COMPLETE" in r.stdout or "DOCTOR COMPLETE" in r.stderr


def test_wiki_search_cli():
    if not AIM_WRAPPER.is_file():
        return
    venv_py = OS_ROOT / "venv" / "bin" / "python3"
    if not venv_py.is_file():
        return
    r = subprocess.run(
        [str(AIM_WRAPPER), "wiki", "search", "vessel"],
        cwd=str(VESSEL_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Empty wiki still returns a clean message; seeded wiki returns results
    out = r.stdout + r.stderr
    assert r.returncode == 0, out
    assert ("WIKI SEARCH" in out) or ("No results found in Wiki" in out) or (
        "memory-wiki" in out.lower()
    )
