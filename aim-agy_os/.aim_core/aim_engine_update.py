#!/usr/bin/env python3
"""
Surgical A.I.M. OS engine update (vessel-agnostic).

Purpose
-------
Update **only** the nested operating system under ``aim-agy_os/`` without
depending on the project's own git remote (the project may be a forked client
app with origin pointing elsewhere, or no origin at all).

Does **not**:
  - touch project app source outside aim-agy_os/
  - wipe user data (archive, memory, memory-wiki, continuity, planning-artifacts)
  - clobber vessel overlays (Grok paths, teleport, vessel_paths, …)
  - require ``git pull`` on the project repo

Does:
  - clone/fetch the **engine upstream** (default soul: aim-agy) into a temp dir
  - rsync surgical engine paths into local ``aim-agy_os/``
  - restore preserved overlays
  - optionally rebuild venv deps
  - write SOURCE pin / update receipt under aim-agy_os/

Env
---
  AIM_ENGINE_URL   git URL for engine payload (default BrianV1981/aim-agy)
  AIM_ENGINE_REF   branch/tag (default main)
  AIM_UPDATE_DRY_RUN=1  plan only
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Sequence

DEFAULT_ENGINE_URL = "https://github.com/BrianV1981/aim-agy.git"
DEFAULT_ENGINE_REF = "main"

# Paths relative to aim-agy_os/ that are **never** updated from remote
PRESERVE_REL = [
    "venv",
    "memory",
    "memory_lance",
    "memory-wiki",
    "archive",
    "continuity",
    "planning-artifacts",
    "workspace",
    "temp",
    ".aim_temp_update",
    "__pycache__",
    # vessel / host overlays (do not clobber)
    ".aim_core/vessel_paths.py",
    ".aim_core/wiki_compiler.py",
    ".aim_core/agent_session_names.py",
    ".aim_core/reincarnation/teleport_engine.py",
    ".aim_core/VESSEL_HOST",
    ".aim_core/CONFIG.json",
    "handoff",  # vessel may carry handoff vNext ahead of soul
]

# Top-level project paths never touched (relative to vessel / project root)
PROJECT_NEVER_TOUCH = [
    "AGENTS.md",
    "SOURCE.md",
    "README.md",
    "LICENSE",
    ".git",
    ".grok",
    ".opencode",
    ".codex",
    ".gemini",
    "aim",  # vessel wrapper
]


def find_os_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for _ in range(12):
        if (cur / "aim-agy_os" / ".aim_core").is_dir():
            return cur / "aim-agy_os"
        if (cur / ".aim_core").is_dir() and (cur / "setup.sh").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise FileNotFoundError("Cannot locate aim-agy_os / .aim_core engine root")


def _run(cmd: Sequence[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, **kw)


def _rsync_engine(
    src_os: Path,
    dst_os: Path,
    *,
    dry_run: bool,
    extra_excludes: Iterable[str] = (),
) -> None:
    if not shutil.which("rsync"):
        raise RuntimeError("rsync required for surgical engine update")
    excludes: List[str] = []
    for rel in PRESERVE_REL:
        excludes += ["--exclude", rel]
    for rel in extra_excludes:
        excludes += ["--exclude", rel]
    excludes += [
        "--exclude",
        "__pycache__",
        "--exclude",
        "*.pyc",
        "--exclude",
        ".git",
    ]
    cmd = ["rsync", "-a"]
    if dry_run:
        cmd.append("-n")
    # No --delete by default: never remove local-only OS files blindly
    # Use AIM_UPDATE_DELETE=1 for delete mode (advanced)
    if os.environ.get("AIM_UPDATE_DELETE", "").lower() in ("1", "true", "yes"):
        cmd.append("--delete")
        for rel in PRESERVE_REL:
            # protect preserved dirs from delete
            cmd += ["--filter", f"P {rel}"]
    cmd += excludes
    cmd += [str(src_os) + "/", str(dst_os) + "/"]
    print("[update]", " ".join(cmd))
    _run(cmd)


def _preserve_overlays(os_root: Path, backup: Path) -> List[str]:
    saved = []
    backup.mkdir(parents=True, exist_ok=True)
    for rel in PRESERVE_REL:
        src = os_root / rel
        if not src.exists():
            continue
        # only file overlays need restore after rsync without --delete of files
        # Always snapshot known overlay **files**
        if src.is_file():
            dest = backup / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            saved.append(rel)
        elif rel in (
            ".aim_core/vessel_paths.py",
            ".aim_core/wiki_compiler.py",
            ".aim_core/agent_session_names.py",
            ".aim_core/reincarnation/teleport_engine.py",
            ".aim_core/VESSEL_HOST",
            ".aim_core/CONFIG.json",
        ):
            pass
    # Explicit file overlays again
    for rel in (
        ".aim_core/vessel_paths.py",
        ".aim_core/wiki_compiler.py",
        ".aim_core/agent_session_names.py",
        ".aim_core/reincarnation/teleport_engine.py",
        ".aim_core/VESSEL_HOST",
        ".aim_core/CONFIG.json",
    ):
        src = os_root / rel
        if src.is_file():
            dest = backup / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if rel not in saved:
                saved.append(rel)
    return saved


def _restore_overlays(os_root: Path, backup: Path, saved: List[str]) -> None:
    for rel in saved:
        src = backup / rel
        if not src.is_file():
            continue
        dest = os_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"[update] restored overlay: {rel}")


def update_engine(
    *,
    project_root: Path | None = None,
    engine_url: str | None = None,
    engine_ref: str | None = None,
    dry_run: bool = False,
    rebuild_deps: bool = False,
) -> dict:
    os_root = find_os_root(project_root)
    vessel_root = os_root.parent if os_root.name == "aim-agy_os" else os_root
    engine_url = (
        engine_url
        or os.environ.get("AIM_ENGINE_URL")
        or DEFAULT_ENGINE_URL
    )
    engine_ref = (
        engine_ref
        or os.environ.get("AIM_ENGINE_REF")
        or DEFAULT_ENGINE_REF
    )
    dry_run = dry_run or os.environ.get("AIM_UPDATE_DRY_RUN", "").lower() in (
        "1",
        "true",
        "yes",
    )

    print("--- A.I.M. SURGICAL ENGINE UPDATE ---")
    print(f"[*] Vessel / project root: {vessel_root}")
    print(f"[*] OS root:               {os_root}")
    print(f"[*] Engine upstream:       {engine_url} @ {engine_ref}")
    print(f"[*] Dry-run:               {dry_run}")
    print("[*] Project git remote is NOT used (OS updates independently).")

    receipt = {
        "schema_version": 1,
        "started": datetime.now(timezone.utc).isoformat(),
        "vessel_root": str(vessel_root),
        "os_root": str(os_root),
        "engine_url": engine_url,
        "engine_ref": engine_ref,
        "dry_run": dry_run,
        "status": "error",
    }

    tmp = Path(tempfile.mkdtemp(prefix="aim_engine_update_"))
    backup = tmp / "overlay_backup"
    try:
        clone_dir = tmp / "engine"
        print("[*] Fetching engine payload (shallow clone)...")
        _run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                engine_ref,
                engine_url,
                str(clone_dir),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        # Resolve SHA
        sha = subprocess.check_output(
            ["git", "-C", str(clone_dir), "rev-parse", "HEAD"], text=True
        ).strip()
        receipt["engine_sha"] = sha
        print(f"    [SUCCESS] payload @ {sha[:12]}")

        src_os = clone_dir / "aim-agy_os"
        if not src_os.is_dir():
            # flat layout fallback
            if (clone_dir / ".aim_core").is_dir() or (clone_dir / "aim_core").is_dir():
                src_os = clone_dir
            else:
                raise FileNotFoundError("Remote payload missing aim-agy_os/")

        saved = _preserve_overlays(os_root, backup)
        receipt["overlays_saved"] = saved
        print(f"[*] Preserved {len(saved)} overlay file(s)")

        print("[*] Surgical rsync into local aim-agy_os/ ...")
        _rsync_engine(src_os, os_root, dry_run=dry_run)

        if not dry_run:
            _restore_overlays(os_root, backup, saved)
            # Write pin receipt (does not rewrite project SOURCE.md unless present and owned)
            pin_path = os_root / "ENGINE_UPDATE_RECEIPT.json"
            receipt["status"] = "ok"
            receipt["finished"] = datetime.now(timezone.utc).isoformat()
            pin_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            # Best-effort SOURCE.md pin in vessel root if it looks like a pin table
            source_md = vessel_root / "SOURCE.md"
            if source_md.is_file():
                try:
                    text = source_md.read_text(encoding="utf-8")
                    if "Upstream" in text or "Commit" in text:
                        note = (
                            f"\n\n<!-- engine update {receipt['finished']} "
                            f"sha={sha[:12]} url={engine_url} -->\n"
                        )
                        if sha[:12] not in text[-500:]:
                            source_md.write_text(text.rstrip() + note, encoding="utf-8")
                except OSError:
                    pass

            if rebuild_deps:
                setup = os_root / "setup.sh"
                if setup.is_file():
                    print("[*] Rebuilding dependencies (setup.sh)...")
                    _run(["bash", str(setup)], cwd=str(vessel_root))
        else:
            receipt["status"] = "dry_run"
            print("[*] Dry-run complete — no files written.")

        print("\n[SUCCESS] Surgical engine update complete.")
        print("    Project files outside aim-agy_os/ were not modified.")
        return receipt
    except subprocess.CalledProcessError as e:
        err = (e.stderr or str(e))[:500]
        print(f"[ERROR] Engine fetch/update failed: {err}", file=sys.stderr)
        receipt["error"] = err
        return receipt
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Surgical A.I.M. OS engine update")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--rebuild-deps", action="store_true")
    p.add_argument("--engine-url", default=None)
    p.add_argument("--engine-ref", default=None)
    p.add_argument("--project-root", default=None)
    args = p.parse_args(argv)
    rec = update_engine(
        project_root=Path(args.project_root) if args.project_root else None,
        engine_url=args.engine_url,
        engine_ref=args.engine_ref,
        dry_run=args.dry_run,
        rebuild_deps=args.rebuild_deps,
    )
    return 0 if rec.get("status") in ("ok", "dry_run") else 1


if __name__ == "__main__":
    raise SystemExit(main())
