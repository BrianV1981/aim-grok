"""Issue #34: Grok-family vessels never spawn AGY."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

CORE = Path(__file__).resolve().parents[1] / ".aim_core"
sys.path.insert(0, str(CORE))

from reincarnation.teleport_engine import (  # noqa: E402
    _resolve_vessel_cli,
    detect_vessel_kind,
)


class TestGrokSpawnNeverAgy(unittest.TestCase):
    def test_aim_grok_path(self):
        os.environ.pop("AIM_VESSEL_CLI", None)
        os.environ.pop("AIM_HOST", None)
        kind = detect_vessel_kind("/home/kingb/aim-grok")
        self.assertEqual(kind, "grok")
        cli = _resolve_vessel_cli("/home/kingb/aim-grok")
        self.assertIn("grok", cli[0])
        self.assertNotIn("agy", os.path.basename(cli[0]))
        self.assertIn("--always-approve", cli)
        self.assertNotIn("--dangerously-skip-permissions", cli)

    def test_grok_audit_path_never_agy(self):
        os.environ.pop("AIM_VESSEL_CLI", None)
        os.environ.pop("AIM_HOST", None)
        with mock.patch("shutil.which", side_effect=lambda b: f"/bin/{b}"):
            kind = detect_vessel_kind("/home/kingb/grok-audit")
            self.assertEqual(kind, "grok")
            cli = _resolve_vessel_cli("/home/kingb/grok-audit")
            self.assertTrue(cli[0].endswith("grok") or "grok" in cli[0])
            self.assertIn("--always-approve", cli)
            self.assertNotIn("--dangerously-skip-permissions", cli)

    def test_both_clis_on_path_ambiguous_prefers_grok(self):
        os.environ.pop("AIM_VESSEL_CLI", None)
        os.environ.pop("AIM_HOST", None)

        def which(name):
            if name in ("grok", "agy"):
                return f"/usr/bin/{name}"
            return None

        with mock.patch("shutil.which", side_effect=which):
            # path without markers still prefers grok when both present
            kind = detect_vessel_kind("/tmp/random-project")
            self.assertEqual(kind, "grok")
            cli = _resolve_vessel_cli("/tmp/random-project")
            self.assertIn("grok", cli[0])
            self.assertNotIn("dangerously-skip", " ".join(cli))

    def test_env_override_agy(self):
        os.environ["AIM_VESSEL_CLI"] = "agy"
        try:
            with mock.patch("shutil.which", side_effect=lambda b: f"/bin/{b}"):
                cli = _resolve_vessel_cli("/home/kingb/aim-grok")
                self.assertIn("agy", cli[0])
                self.assertIn("--dangerously-skip-permissions", cli)
        finally:
            os.environ.pop("AIM_VESSEL_CLI", None)

    def test_vessel_host_pin_file(self):
        import tempfile
        from pathlib import Path

        os.environ.pop("AIM_VESSEL_CLI", None)
        os.environ.pop("AIM_HOST", None)
        with tempfile.TemporaryDirectory() as td:
            pin = Path(td) / "aim-agy_os" / ".aim_core"
            pin.mkdir(parents=True)
            (pin / "VESSEL_HOST").write_text("grok\n")
            self.assertEqual(detect_vessel_kind(td), "grok")


if __name__ == "__main__":
    unittest.main()
