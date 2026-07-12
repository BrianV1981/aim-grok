import os
import glob
import sqlite3
import time

try:
    from .aim_core.reasoning_utils import generate_reasoning
except ImportError:
    try:
        from reasoning_utils import generate_reasoning
    except ImportError:
        generate_reasoning = None


def get_base_dir():
    current = os.path.abspath(os.getcwd())
    while current != "/":
        if os.path.exists(os.path.join(current, "aim-agy_os", "setup.sh")):
            return os.path.join(current, "aim-agy_os")
        if os.path.exists(os.path.join(current, "setup.sh")) and os.path.isdir(
            os.path.join(current, ".aim_core")
        ):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def search_wiki(query):
    """
    Lightning-fast local FTS5 search over memory-wiki/**/*.md
    """
    base_dir = get_base_dir()
    wiki_dir = os.path.join(base_dir, "memory-wiki")

    if not os.path.exists(wiki_dir):
        print("Error: memory-wiki/ directory not found. Please initialize the wiki first.")
        return

    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.execute("""CREATE VIRTUAL TABLE wiki_fts USING fts5(filepath, content)""")

    md_files = glob.glob(os.path.join(wiki_dir, "**", "*.md"), recursive=True)
    for file_path in md_files:
        base = os.path.basename(file_path)
        if base in ("GEMINI.md", "AGENTS.md"):
            continue
        if "/_ingest/" in file_path.replace("\\", "/") or "/_raw_logs/" in file_path.replace(
            "\\", "/"
        ):
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            rel = os.path.relpath(file_path, wiki_dir)
            c.execute(
                "INSERT INTO wiki_fts (filepath, content) VALUES (?, ?)",
                (rel, content),
            )
        except Exception as e:
            import sys

            print(f"[WARN] Failed to read {file_path}: {e}", file=sys.stderr)

    try:
        c.execute(
            "SELECT filepath, snippet(wiki_fts, 1, '>>', '<<', '...', 64) "
            "FROM wiki_fts WHERE wiki_fts MATCH ? ORDER BY rank LIMIT 8",
            (query,),
        )
        results = c.fetchall()
    except sqlite3.OperationalError:
        c.execute(
            "SELECT filepath, substr(content, 1, 200) FROM wiki_fts "
            "WHERE content LIKE ? LIMIT 8",
            (f"%{query}%",),
        )
        results = c.fetchall()

    conn.close()

    if not results:
        print(f"No results found in Wiki for '{query}'.")
        return

    print(f"\n--- WIKI SEARCH RESULTS: '{query}' ---")
    for filepath, snippet in results:
        print(f"\n{filepath}:\n{snippet}\n")
    print("-----------------------------------")


def process_wiki_deterministic():
    """Compile _ingest into pages/index/log without spawning an agent."""
    try:
        from wiki_compiler import process_ingest, process_raw_logs_to_ingest
    except ImportError:
        from aim_core.wiki_compiler import process_ingest, process_raw_logs_to_ingest  # type: ignore

    print("--- WIKI PROCESS (deterministic) ---")
    for line in process_raw_logs_to_ingest():
        print(" ", line)
    results = process_ingest()
    for line in results:
        print(" ", line)
    return results


def process_wiki_agent():
    """
    Legacy: hand off ingest processing to a tmux agent (agy or grok).
    Set AIM_WIKI_AGENT=agy|grok to choose CLI (default agy).
    """
    import subprocess

    base_dir = get_base_dir()
    ingest_dir = os.path.join(base_dir, "memory-wiki/_ingest")

    if not os.path.exists(ingest_dir):
        print("Error: memory-wiki/_ingest/ directory not found.")
        return

    files = [
        f
        for f in glob.glob(os.path.join(ingest_dir, "*.*"))
        if os.path.basename(f) not in (".gitkeep", ".keep")
    ]
    if not files:
        print("No files found in memory-wiki/_ingest/ to process.")
        return

    try:
        from agent_session_names import wiki_session_name

        session_name = wiki_session_name(project_root=base_dir)
    except Exception:
        # Last-resort unique name (still not a global singleton)
        session_name = f"grok_wiki_fallback_{int(time.time())}"
    wiki_dir = os.path.join(base_dir, "memory-wiki")
    agent_cli = os.environ.get("AIM_WIKI_AGENT", "agy")
    if agent_cli == "grok":
        launch = "grok"
    else:
        launch = "agy --dangerously-skip-permissions"

    # Only skip if THIS exact namespaced session is already live (not any wiki agent).
    check_cmd = subprocess.run(
        ["tmux", "has-session", "-t", session_name], capture_output=True
    )
    if check_cmd.returncode == 0:
        print(f"[{session_name}] is already active and processing the queue. Skipping new spawn.")
        return

    print(f"Starting fresh '{session_name}' tmux session ({agent_cli})...")
    subprocess.run(
        [
            "tmux",
            "new-session",
            "-d",
            "-s",
            session_name,
            "-c",
            wiki_dir,
            "bash",
            "-c",
            f"cd {wiki_dir} && source ~/.bashrc 2>/dev/null; {launch}",
        ]
    )
    print(f"Handing off {len(files)} file(s) to {session_name} for processing...")

    prompt = (
        "Wake up. You are the disciplined LLM Wiki Maintainer. Your job is to read the "
        "factual summaries waiting in the `_ingest/` directory ONE BY ONE. For each file: "
        "1. Read the summary. 2. If it contains valuable information, update `index.md`, "
        "append to `log.md`, and create/update concept pages under `pages/`. "
        "3. DELETE the summary from `_ingest/` when absorbed. 4. Repeat until empty. "
        f"5. Execute `tmux kill-session -t {session_name}`."
    )

    try:
        max_retries = 30
        trusted = False
        injected = False

        for _ in range(max_retries):
            result = subprocess.run(
                ["tmux", "capture-pane", "-p", "-t", session_name],
                capture_output=True,
                text=True,
            )
            out = result.stdout

            if (
                "trust this directory" in out.lower()
                or "trust the contents" in out.lower()
            ) and not trusted:
                subprocess.run(
                    ["tmux", "send-keys", "-t", session_name, "y"], check=True
                )
                subprocess.run(
                    ["tmux", "send-keys", "-t", session_name, "Enter"], check=True
                )
                trusted = True
                time.sleep(1)
                continue

            ready = (
                "Antigravity" in out
                or "Enter your" in out
                or "Grok" in out
                or "❯" in out
            )
            if ready:
                subprocess.run(["tmux", "set-buffer", prompt], check=True)
                subprocess.run(
                    ["tmux", "paste-buffer", "-p", "-t", session_name], check=True
                )
                time.sleep(1)
                subprocess.run(
                    ["tmux", "send-keys", "-t", session_name, "Enter"], check=True
                )
                injected = True
                break

            time.sleep(0.5)

        if not injected:
            print("[WARNING] Could not confirm Wiki Agent readiness. Injecting blindly.")
            subprocess.run(["tmux", "set-buffer", prompt], check=True)
            subprocess.run(
                ["tmux", "paste-buffer", "-p", "-t", session_name], check=True
            )
            time.sleep(1)
            subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "Enter"], check=True
            )

        print(f"[SUCCESS] Directives dispatched to {session_name}.")
    except Exception as e:
        print(f"[ERROR] Failed to hand off to {session_name}: {e}")


def process_wiki():
    """
    Default: deterministic compiler (works on aim-grok without agy).
    Set AIM_WIKI_MODE=agent to use tmux + agy/grok maintainer.
    """
    mode = os.environ.get("AIM_WIKI_MODE", "deterministic").lower()
    if mode in ("agent", "agy", "grok", "llm"):
        if mode in ("agy", "grok"):
            os.environ.setdefault("AIM_WIKI_AGENT", mode if mode != "agent" else "agy")
        return process_wiki_agent()
    return process_wiki_deterministic()
