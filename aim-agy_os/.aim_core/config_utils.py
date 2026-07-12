import os
import json
import sys
import getpass

def _merge_defaults(target, defaults):
    changed = False
    for key, value in defaults.items():
        if key not in target:
            target[key] = value
            changed = True
        elif isinstance(value, dict) and isinstance(target.get(key), dict):
            if _merge_defaults(target[key], value):
                changed = True
    return changed

def find_project_root():
    """
    Dynamically discovers the A.I.M. *vessel* project root (host repo),
    not the engine payload directory (aim-agy_os/).

    Bug fix (#83 class): treating `setup.sh` inside `aim-agy_os/` as the project
    root made OS_ROOT = aim-agy_os/aim-agy_os and worktrees double-nest.
    """
    def _is_vessel_root(path):
        has_os = os.path.isdir(os.path.join(path, "aim-agy_os"))
        has_git = os.path.isdir(os.path.join(path, ".git")) or os.path.isfile(os.path.join(path, ".git"))
        has_agents = os.path.isfile(os.path.join(path, "AGENTS.md"))
        has_wrapper = os.path.isfile(os.path.join(path, "aim"))
        return has_os and (has_git or has_agents or has_wrapper)

    # 1. Walk up from CWD for a vessel root (repo hosting aim-agy_os/)
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if _is_vessel_root(current):
            return current
        current = os.path.dirname(current)

    # 2. If we are inside the engine tree (setup.sh + .aim_core), parent is vessel
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.isfile(os.path.join(current, "setup.sh")) and os.path.isdir(os.path.join(current, ".aim_core")):
            if os.path.basename(current) in ("aim-agy_os", "aim_os", "aim-grok_os"):
                return os.path.dirname(current)
            # Legacy flat layout: engine == project root
            return current
        # Explicit host CONFIG at vessel root
        if os.path.isfile(os.path.join(current, ".aim_core", "CONFIG.json")) and _is_vessel_root(current):
            return current
        current = os.path.dirname(current)

    # 3. Physical install: .../vessel/aim-agy_os/.aim_core/config_utils.py → vessel
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = find_project_root()
OS_ROOT = os.path.join(PROJECT_ROOT, "aim-agy_os")
AIM_ROOT = OS_ROOT  # Default for most scripts
CONFIG_PATH = os.path.join(PROJECT_ROOT, ".aim_core/CONFIG.json")

def load_config():
    """Loads, validates, and auto-repairs paths for the current machine."""
    home = os.path.expanduser("~")
    
    # Baseline defaults for a fresh system
    default_config = {
        "paths": {
            "aim_root": AIM_ROOT,
            "os_root": OS_ROOT,
            "core_dir": os.path.join(OS_ROOT, "core"),
            "docs_dir": os.path.join(OS_ROOT, "docs"),
            "hooks_dir": os.path.join(OS_ROOT, "hooks"),
            "archive_raw_dir": os.path.join(OS_ROOT, "archive/raw"),
            "continuity_dir": os.path.join(OS_ROOT, "continuity"),
            "src_dir": os.path.join(OS_ROOT, ".aim_core"),
            "tmp_chats_dir": os.path.expanduser("~/.grok/sessions")
        },
        "models": {
            "embedding_provider": "local",
            "embedding": "nomic-embed-text",
            "embedding_endpoint": "http://127.0.0.1:11434/api/embeddings",
            "default_reasoning": {
                "provider": "google",
                "model": "agy-flash-latest",
                "endpoint": "https://generativelanguage.googleapis.com",
                "auth_type": "API Key"
            }
        },
        "settings": {
            "allowed_root": home,
            "semantic_pruning_threshold": 0.85,
            "scrivener_interval_minutes": 30,
            "archive_retention_days": 30,
            "sentinel_mode": "full",
            "obsidian_vault_path": "",
            "auto_distill_tier": "T4",
            "auto_rebirth": False
        }
    }

    if not os.path.exists(CONFIG_PATH):
        return default_config

    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        changed = False
        
        # --- THE PORTABILITY SHIELD ---
        # If the root in the file doesn't match the current directory, 
        # we RE-CALCULATE everything based on the current system.
        if config.get('paths', {}).get('aim_root') != AIM_ROOT:
            sys.stderr.write(f"[PORTABILITY] System shift detected. Re-mapping paths for this machine...\n")
            
            config['paths']['aim_root'] = PROJECT_ROOT
            config['paths']['os_root'] = OS_ROOT
            for key in ['core_dir', 'docs_dir', 'hooks_dir', 'memory_dir', 'archive_raw_dir', 'archive_index_dir', 'continuity_dir', 'src_dir']:
                if key == 'src_dir':
                    config['paths'][key] = os.path.join(OS_ROOT, ".aim_core")
                else:
                    config['paths'][key] = os.path.join(OS_ROOT, key.replace('_dir', ''))
            
            # Recalculate home-based paths
            config['paths']['tmp_chats_dir'] = os.path.expanduser("~/.grok/sessions")
            
            # If we have an Obsidian path, we only update it if it started with /home/
            old_vault = config['settings'].get('obsidian_vault_path', "")
            if old_vault.startswith("/home/"):
                # Extract the old user part and replace it with current
                parts = old_vault.split('/')
                if len(parts) > 2:
                    new_vault = os.path.join(home, *parts[3:])
                    config['settings']['obsidian_vault_path'] = new_vault

            changed = True

        if _merge_defaults(config, default_config):
            changed = True

        if changed:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
                
        return config
    except Exception:
        return default_config

CONFIG = load_config()
