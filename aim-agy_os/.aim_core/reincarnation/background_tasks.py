import os
import sys
import subprocess


def trigger_background_pipelines(aim_root, workspace, session_id=None):
    print("[1/4] Mechanically extracting session signal & routing to pipelines...")

    venv_python = os.path.join(aim_root, "venv", "bin", "python3")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    workspace = os.path.abspath(workspace or ".")

    try:
        pulse_args = [
            venv_python,
            os.path.join(aim_root, ".aim_core", "handoff_pulse_generator.py"),
        ]
        if session_id:
            pulse_args.extend(["--session-id", session_id])

        subprocess.run(pulse_args, cwd=workspace, check=True, timeout=120)

        # Vessel black box: seal ONLY the reincarnating session's raw transcript.
        # Non-fatal — never aborts reincarnation.
        print("      [VAULT] Sealing reincarnating session into vessel black box...")
        try:
            sys.path.insert(0, os.path.join(aim_root, ".aim_core"))
            from blackbox_vault import seal_for_reincarnate

            seal_for_reincarnate(workspace, session_id=session_id)
        except Exception as ve:
            print(f"      [VAULT] WARN seal step skipped: {ve}")

        print("      Triggering Subconscious Scribe (Session Summarizer)...")
        subprocess.Popen(
            [
                venv_python,
                os.path.join(aim_root, "hooks", "session_summarizer.py"),
                "--reincarnate",
                "--bg",
            ],
            cwd=workspace,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

        print("      Syncing remote issues and harvesting closed bugs...")
        subprocess.run(
            [
                venv_python,
                os.path.join(aim_root, ".aim_core", "aim_scraper.py"),
                "--source",
                "github",
                "--query",
                "is:closed",
                "--limit",
                "5",
            ],
            cwd=workspace,
            check=False,
            timeout=30,
        )

    except subprocess.TimeoutExpired as e:
        print(
            f"\n[WARNING] A reincarnation subprocess timed out: {e}\n"
            "Continuing reincarnation protocol anyway to preserve context..."
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to generate handoff: {e}")
        sys.exit(1)
