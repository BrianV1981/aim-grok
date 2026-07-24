"""Surgical engine update preserves project data + overlays."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

CORE = Path(__file__).resolve().parents[1] / ".aim_core"
sys.path.insert(0, str(CORE))

from aim_engine_update import (  # noqa: E402
    PRESERVE_REL,
    PROJECT_NEVER_TOUCH,
    find_os_root,
    _preserve_overlays,
    _restore_overlays,
)


class TestEngineUpdateSafety(unittest.TestCase):
    def test_preserve_list_covers_user_data(self):
        joined = " ".join(PRESERVE_REL)
        for must in ("memory-wiki", "archive", "continuity", "venv", "vessel_paths"):
            self.assertTrue(any(must in p for p in PRESERVE_REL), must)

    def test_project_never_touch(self):
        for p in ("AGENTS.md", ".git", "aim", ".grok"):
            self.assertIn(p, PROJECT_NEVER_TOUCH)

    def test_find_os_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "aim-agy_os" / ".aim_core").mkdir(parents=True)
            found = find_os_root(root)
            self.assertEqual(found, root / "aim-agy_os")

    def test_overlay_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            os_root = Path(td) / "aim-agy_os"
            tele = os_root / ".aim_core" / "reincarnation"
            tele.mkdir(parents=True)
            f = tele / "teleport_engine.py"
            f.write_text("GROK_PIN = True\n")
            backup = Path(td) / "bak"
            saved = _preserve_overlays(os_root, backup)
            self.assertIn(".aim_core/reincarnation/teleport_engine.py", saved)
            f.write_text("WIPED\n")
            _restore_overlays(os_root, backup, saved)
            self.assertEqual(f.read_text(), "GROK_PIN = True\n")


if __name__ == "__main__":
    unittest.main()
