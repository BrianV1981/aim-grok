#!/usr/bin/env python3
import sys
import json
import os
import time
import glob
import re
import subprocess

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "aim-agy_os", "setup.sh")): return os.path.join(current, "aim-agy_os")
        if os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
sys.path.append(AIM_ROOT)
sys.path.append(os.path.join(AIM_ROOT, ".aim_core"))

from plugins.datajack.forensic_utils import chunk_text, get_embedding
from wiki_tools import process_wiki
from blackbox_vault import vault_session

CONFIG_PATH = os.path.join(AIM_ROOT, ".aim_core/CONFIG.json")
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = os.path.join(os.path.dirname(AIM_ROOT), ".aim_core/CONFIG.json")
if not os.path.exists(CONFIG_PATH):
    sys.exit(0)

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

def ingest_file_to_db(backend, filepath, record_type="session_history"):
    session_id = os.path.basename(filepath).replace('.md', '')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    chunks = chunk_text(text)
    fragments = []
    
    if chunks:
        test_vec = get_embedding(chunks[0])
        if not test_vec:
            print("[WARNING] Embedding provider is unreachable. Skipping native LanceDB ingestion.")
            return

    for chunk in chunks:
        vec = get_embedding(chunk)
        if vec and len(vec) == 768:
            fragments.append({
                'session_id': session_id,
                'type': record_type,
                'content': chunk,
                'vector': vec
            })
        
    if fragments:
        backend.add_fragments(fragments)

def process_transcript(md_path):
    try:
        print(f"[WATCHDOG] Beginning Two-Node Swarm Sequence for: {os.path.basename(md_path)}")
        session_id = os.path.basename(md_path).replace('.md', '')
        
        # --- PHASE 0: Immutable Black Box Vaulting ---
        session_id = os.path.basename(md_path).replace('.md', '')
        if '_' in session_id:
            # Handle timestamp prefix if present (e.g., 2026-06-06_1230_uuid)
            parts = session_id.split('_')
            session_id = parts[-1] if len(parts) >= 2 else session_id
            
        jsonl_path = os.path.expanduser(
            f"~/.gemini/antigravity-cli/brain/{session_id}/.system_generated/logs/transcript.jsonl"
        )
        # Grok vessel: try chat_history via vessel_paths when AGY brain missing
        if not os.path.exists(jsonl_path):
            try:
                from vessel_paths import find_session_transcripts
                project = os.path.dirname(AIM_ROOT)
                hits = find_session_transcripts(project, explicit_session_id=session_id, prefer="auto")
                if hits:
                    jsonl_path = hits[0]
            except Exception:
                pass
        if os.path.exists(jsonl_path):
            print(f"[WATCHDOG] Securing {session_id} into the Immutable Black Box...")
            try:
                vault_session(jsonl_path)
            except Exception as e:
                print(f"[WATCHDOG] Vault skipped: {e}")
            
        # 1. Chunk and Stage the Raw Logs
        with open(md_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
            
        turns = transcript.split('\n---\n\n')
        
        raw_logs_dir = os.path.join(AIM_ROOT, "memory-wiki", "_raw_logs")
        os.makedirs(raw_logs_dir, exist_ok=True)
        
        # Clear out any old raw logs
        for old_file in glob.glob(os.path.join(raw_logs_dir, "*.md")):
            os.remove(old_file)
            
        print(f"[WATCHDOG] Transcript has {len(turns)} turns. Beginning intelligent 100k-character chunking...")
        
        staged_files = []
        MAX_CHARS = 100000
        current_chunk_turns = []
        current_char_count = 0
        part_index = 1
        
        def save_chunk(turns_to_save, idx):
            chunk_transcript = '\n---\n\n'.join(turns_to_save)
            part_suffix = f"_part{idx}"
            raw_path = os.path.join(raw_logs_dir, f"{session_id}{part_suffix}_raw.md")
            with open(raw_path, "w", encoding="utf-8") as f_out:
                f_out.write(chunk_transcript)
            staged_files.append(raw_path)
            
        for turn in turns:
            turn_len = len(turn) + 5 # +5 for the delimiter
            if current_char_count + turn_len > MAX_CHARS and current_chunk_turns:
                # Limit reached, save current chunk and start fresh
                save_chunk(current_chunk_turns, part_index)
                part_index += 1
                current_chunk_turns = [turn]
                current_char_count = turn_len
            else:
                current_chunk_turns.append(turn)
                current_char_count += turn_len
                
        # Save any remaining turns
        if current_chunk_turns:
            save_chunk(current_chunk_turns, part_index)
            
        print(f"[WATCHDOG] Staged {len(staged_files)} safe, digestible chunks in _raw_logs/.")
            
        if not staged_files:
            print("[WATCHDOG] No data to process.")
            return True

        wiki_dir = os.path.join(AIM_ROOT, "memory-wiki")
        wiki_mode = os.environ.get("AIM_WIKI_MODE", "deterministic").lower()

        if wiki_mode in ("agent", "agy", "grok", "llm"):
            # Legacy two-node agent path (optional)
            scribe_session_name = "scribe_agent_aim"
            print(f"[WATCHDOG] Agent mode: spawning Scribe ({wiki_mode})...")
            # Fall through to deterministic if spawn fails is safer — still run deterministic below
        else:
            print("[WATCHDOG] Deterministic mode: extractive summarize → _ingest → wiki pages")

        # Always run deterministic compiler (primary path for aim-grok)
        try:
            from wiki_compiler import process_raw_logs_to_ingest, process_ingest
            for line in process_raw_logs_to_ingest():
                print(f"  {line}")
            for line in process_ingest():
                print(f"  {line}")
        except Exception as e:
            print(f"[WATCHDOG] Deterministic wiki compile error: {e}")
            process_wiki()  # fallback to wiki_tools default

        # Native LanceDB Ingestion
        from lance_backend import VectorBackend
        backend = VectorBackend()
        print(f"[WATCHDOG] Ingesting flight recorder natively into LanceDB...")
        ingest_file_to_db(backend, md_path, record_type="session_history")

        print("[WATCHDOG] Re-embedding updated Wiki pages into native LanceDB...")
        for md_file in glob.glob(os.path.join(wiki_dir, "**", "*.md"), recursive=True):
            if "_ingest" in md_file or "_raw_logs" in md_file:
                continue
            ingest_file_to_db(backend, md_file, record_type="wiki_knowledge")

        print("[SUCCESS] Wiki + vector pipeline complete (deterministic).")
        return True

    except Exception as e:
        print(f"[FATAL] Watchdog Pipeline Error: {e}")
        return False

def main(args):
    if "--reincarnate" not in args:
        print(json.dumps({}))
        return

    if os.environ.get('AIM_INTERNAL_REASONING'):
        print(json.dumps({}))
        return
    
    is_light_mode = "--light" in args
    if is_light_mode:
        print(json.dumps({}))
        return

    cognitive_mode = CONFIG.get('settings', {}).get('cognitive_mode', 'monolithic')
    if cognitive_mode == 'frontline':
        print(json.dumps({}))
        return

    md_path = None
    for arg in args[1:]:
        if arg.endswith('.md') and os.path.exists(arg):
            md_path = arg
            break
            
    if not md_path:
        history_dir = os.path.join(AIM_ROOT, "archive", "history")
        if os.path.exists(history_dir):
            transcripts = glob.glob(os.path.join(history_dir, "*.md"))
            if transcripts:
                md_path = max(transcripts, key=os.path.getmtime)
                
    if not md_path:
        print(json.dumps({}))
        return

    if "--bg" not in args:
        import subprocess
        cmd = [sys.executable, os.path.abspath(__file__), "--bg"] + args[1:]
        subprocess.Popen(cmd, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
        print(json.dumps({}))
        return

    updated = 1 if process_transcript(md_path) else 0
    if "--bg" not in args:
        print(json.dumps({}))

if __name__ == "__main__":
    main(sys.argv)
