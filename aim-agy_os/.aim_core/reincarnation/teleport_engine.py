import os
import sys
import subprocess
import signal
import time
import shutil
from pathlib import Path


def get_current_tmux_session():
    current_session = None
    if os.environ.get("TMUX"):
        try:
            result = subprocess.run(
                ["tmux", "display-message", "-p", "#S"],
                capture_output=True,
                text=True,
            )
            current_session = result.stdout.strip()
        except Exception:
            pass
    return current_session


# Path / name markers for Grok-family vessels (never spawn AGY for these)
_GROK_MARKERS = (
    "aim-grok",
    "grok-audit",
    "test_aim_grok",
    "test_fleet",  # fleet life tests often under grok trees
)


def detect_vessel_kind(workspace: str) -> str:
    """
    Return host CLI family: grok | agy | opencode | codex.

    Priority:
      1. AIM_VESSEL_CLI or AIM_HOST env
      2. Vessel pin file aim-agy_os/.aim_core/VESSEL_HOST (one word)
      3. Path / layout heuristics
      4. Safe default: grok if on PATH (never fall through to AGY merely because agy exists)
    """
    override = (
        os.environ.get("AIM_VESSEL_CLI") or os.environ.get("AIM_HOST") or ""
    ).strip().lower()
    if override in ("grok", "agy", "opencode", "codex"):
        return override

    ws = os.path.abspath(workspace or ".")
    base = os.path.basename(ws)
    pin = Path(ws) / "aim-agy_os" / ".aim_core" / "VESSEL_HOST"
    if pin.is_file():
        val = pin.read_text(encoding="utf-8", errors="replace").strip().lower().split()
        if val and val[0] in ("grok", "agy", "opencode", "codex"):
            return val[0]

    # Grok-family paths (issue #34: grok-audit must not become AGY)
    ws_l = ws.lower()
    base_l = base.lower()
    for m in _GROK_MARKERS:
        if m in ws_l or base_l.startswith(m) or base_l.startswith("grok"):
            return "grok"
    if (Path(ws) / ".grok").is_dir():
        return "grok"

    if "aim-opencode" in ws_l or base_l.startswith("aim-opencode"):
        return "opencode"
    if "aim-codex" in ws_l or base_l.startswith("aim-codex"):
        return "codex"
    if "aim-agy" in ws_l or base_l.startswith("aim-agy"):
        return "agy"
    if (Path(ws) / ".gemini").is_dir() or (Path(ws) / ".opencode").is_dir():
        if (Path(ws) / ".opencode").is_dir():
            return "opencode"
        return "agy"

    # Ambiguous: prefer grok when available so dual-CLI hosts don't poison Grok work
    if shutil.which("grok"):
        return "grok"
    if shutil.which("agy"):
        return "agy"
    if shutil.which("opencode"):
        return "opencode"
    if shutil.which("codex"):
        return "codex"
    return "grok"


def _resolve_vessel_cli(workspace: str) -> list:
    """
    Choose host CLI argv for the new reincarnate vessel.

    aim-grok / Grok-family: always `grok --always-approve --cwd <ws>`
    (Operator: auto-approve / skip-permissions style for Grok — NOT agy flags.)
    Never spawn `agy --dangerously-skip-permissions` for Grok-family workspaces.
    """
    kind = detect_vessel_kind(workspace)
    ws = os.path.abspath(workspace)

    if kind == "grok":
        grok = (
            os.environ.get("GROK_BIN")
            or shutil.which("grok")
            or os.path.expanduser("~/.local/bin/grok")
        )
        # Documented Grok auto-approve (see `grok --help`: --always-approve)
        return [grok, "--always-approve", "--cwd", ws]

    if kind == "opencode":
        oc = (
            os.environ.get("OPENCODE_BIN")
            or shutil.which("opencode")
            or os.path.expanduser("~/.opencode/bin/opencode")
        )
        return [oc]

    if kind == "codex":
        codex = (
            os.environ.get("CODEX_BIN")
            or shutil.which("codex")
            or os.path.expanduser("~/.npm-global/bin/codex")
        )
        return [codex]

    # agy vessel only
    agy = (
        os.environ.get("AGY_BIN")
        or shutil.which("agy")
        or os.path.expanduser("~/.local/bin/agy")
    )
    return [agy, "--dangerously-skip-permissions"]


def spawn_new_agent(workspace, session_name, wake_up_prompt):
    print("[2/4] Spawning new host vessel (tmux session) with Ephemeral Context Injection...")
    cli = _resolve_vessel_cli(workspace)
    kind = detect_vessel_kind(workspace)
    print(f"      Vessel CLI: {kind} ({cli[0]})")
    if kind == "grok" and "agy" in os.path.basename(cli[0]):
        print("[ERROR] Refusing to spawn AGY binary for Grok-family vessel")
        sys.exit(1)

    try:
        if kind == "grok":
            cmd = [
                "tmux",
                "new-session",
                "-d",
                "-s",
                session_name,
                "-c",
                workspace,
            ] + cli + [wake_up_prompt]
        elif kind == "agy":
            cmd = [
                "tmux",
                "new-session",
                "-d",
                "-s",
                session_name,
                "-c",
                workspace,
            ] + cli + ["-i", wake_up_prompt]
        else:
            # opencode / codex: inject wake via shell after spawn is flaky;
            # start CLI in workspace; write wake file for attach.
            wake_file = os.path.join(workspace, "aim-agy_os", ".aim_core", "temp", "LAST_WAKE_PROMPT.md")
            os.makedirs(os.path.dirname(wake_file), exist_ok=True)
            with open(wake_file, "w", encoding="utf-8") as f:
                f.write(wake_up_prompt)
            cmd = [
                "tmux",
                "new-session",
                "-d",
                "-s",
                session_name,
                "-c",
                workspace,
            ] + cli

        subprocess.run(cmd, check=True)

        for _ in range(20):
            result = subprocess.run(
                ["tmux", "capture-pane", "-p", "-t", session_name],
                capture_output=True,
                text=True,
            )
            out = result.stdout.lower()
            if "trust this directory" in out or "trust the contents" in out:
                subprocess.run(
                    ["tmux", "send-keys", "-t", session_name, "y"], check=True
                )
                subprocess.run(
                    ["tmux", "send-keys", "-t", session_name, "Enter"], check=True
                )
                break
            if "grok" in out or "antigravity" in out or "❯" in out or ">" in result.stdout:
                break
            time.sleep(0.5)

        print(f"      [Success] New agent is awake in tmux session: {session_name}")
    except FileNotFoundError:
        print("[ERROR] 'tmux' is not installed. The Reincarnation Protocol requires tmux.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to spawn tmux session: {e}")
        sys.exit(1)

    print(f"[3/4] Wake-up prompt handled for {kind} vessel...")


def execute_teleport(current_session, session_name):
    print("[4/4] Executing Teleport Sequence...")

    if os.environ.get("AIM_REINCARNATE_NO_TELEPORT", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        print(
            f"      [NO_TELEPORT] Leaving current session intact. "
            f"New vessel: tmux attach -t {session_name}"
        )
        return

    time.sleep(2)

    if os.environ.get("TMUX") and current_session:
        print(
            f"      [Teleport] TMUX detected. Switching clients from {current_session} to {session_name}..."
        )
        try:
            clients_result = subprocess.run(
                [
                    "tmux",
                    "list-clients",
                    "-t",
                    current_session,
                    "-F",
                    "#{client_name}",
                ],
                capture_output=True,
                text=True,
            )
            clients = clients_result.stdout.strip().split("\n")

            for client in clients:
                client = client.strip()
                if client:
                    subprocess.run(
                        ["tmux", "switch-client", "-c", client, "-t", session_name],
                        check=True,
                    )

            subprocess.run(["tmux", "kill-session", "-t", current_session])
        except Exception as e:
            print(f"[ERROR] Teleport failed: {e}")
            sys.exit(1)
    else:
        print(
            f"\n[!] You are not in tmux. To view the new agent, run:\n"
            f"    tmux attach-session -t {session_name}"
        )
        try:
            input(
                "\nPress Enter to safely exit this session and kill the current agent..."
            )
        except (EOFError, KeyboardInterrupt):
            pass
        parent_pid = os.getppid()
        try:
            os.kill(parent_pid, signal.SIGTERM)
        except Exception as e:
            print(f"[ERROR] Could not self-terminate: {e}")
