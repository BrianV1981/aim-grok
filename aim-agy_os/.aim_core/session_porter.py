from config_utils import PROJECT_ROOT
#!/usr/bin/env python3
import os
import shutil
import glob
import json
import sys

# --- CONFIG BOOTSTRAP ---
def find_aim_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
CONFIG_PATH = os.path.join(PROJECT_ROOT, ".aim_core/CONFIG.json")

if not os.path.exists(CONFIG_PATH):
    sys.exit(0)

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

TMP_CHATS_DIR = CONFIG['paths'].get('tmp_chats_dir')
ARCHIVE_RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")

def mirror_transcripts():
    """Mirror vessel transcripts (Grok chat_history + legacy flat JSON) into archive/raw."""
    os.makedirs(ARCHIVE_RAW_DIR, exist_ok=True)
    count = 0
    candidates = []

    # Grok: recursive chat_history.jsonl under tmp_chats_dir / sessions root
    if TMP_CHATS_DIR and os.path.isdir(TMP_CHATS_DIR):
        candidates.extend(glob.glob(os.path.join(TMP_CHATS_DIR, "**", "chat_history.jsonl"), recursive=True))
        candidates.extend(glob.glob(os.path.join(TMP_CHATS_DIR, "*.json")))
        candidates.extend(glob.glob(os.path.join(TMP_CHATS_DIR, "*.jsonl")))

    try:
        from vessel_paths import find_session_transcripts
        from config_utils import PROJECT_ROOT as HOST_ROOT
        for t in find_session_transcripts(HOST_ROOT or AIM_ROOT, prefer="auto"):
            if t not in candidates:
                candidates.append(t)
    except Exception:
        pass

    for t in candidates:
        if not os.path.isfile(t):
            continue
        # Flatten: session_id__filename
        parent = os.path.basename(os.path.dirname(t))
        filename = f"{parent}__{os.path.basename(t)}"
        dest = os.path.join(ARCHIVE_RAW_DIR, filename)
        if not os.path.exists(dest) or os.path.getmtime(t) > os.path.getmtime(dest):
            shutil.copy2(t, dest)
            count += 1

    if count > 0:
        sys.stderr.write(f"[PORTER] Mirrored {count} transcripts to local archive.\n")

if __name__ == "__main__":
    mirror_transcripts()
