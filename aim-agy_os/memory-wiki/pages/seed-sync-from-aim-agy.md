# SYNC_FROM_AIM_AGY

*Ingested from `seed_sync-from-aim-agy.md` on 2026-07-12*

# SYNC_FROM_AIM_AGY

*Seeded from `/home/kingb/aim-grok/SYNC_FROM_AIM_AGY.md`*

# Syncing engine code from aim-agy → aim-grok

aim-agy remains the **upstream** for Antigravity + shared engine. aim-grok **vendors** `aim-agy_os/` and applies Grok overlays.

## What is overlay (do not clobber blindly)

| Path | Owner |
|------|--------|
| `AGENTS.md`, `README.md`, `TOOL_MAP.md`, `SOURCE.md` | aim-grok |
| `./aim` wrapper | aim-grok |
| `.grok/` skills | aim-grok |
| `.vscode/mcp.json`, `.grok/mcp.json` | aim-grok |
| `vessel_paths.py` | aim-grok (port back to aim-agy later if desired) |
| Grok patches in `extract_signal.py`, `handoff_pulse_generator.py`, `session_porter.py`, `recover_json_logs.py`, `config_utils.py` tmp path | aim-grok |

## Safe rsync (engine only)

```bash
AGY=/home/kingb/aim-agy
GROK=/home/kingb/aim-grok

# Dry-run first
rsync -anc --delete \
  --exclude venv --exclude memory --exclude memory_lance \
  --exclude workspace --exclude archive --exclude continuity \
  --exclude '__pycache__' --exclude '*.pyc' \
  --exclude '.aim_core/vessel_paths.py' \
  "$AGY/aim-agy_os/" "$GROK/aim-agy_os/"

# Real sync (after reviewing dry-run)
rsync -a --delete \
  --exclude venv --exclude memory --exclude memory_lance \
  --exclude workspace --exclude archive --exclude continuity \
  --exclude '__pycache__' --exclude '*.pyc' \
  --exclude '.aim_core/vessel_paths.py' \
  "$AGY/aim-agy_os/" "$GROK/aim-agy_os/"

# Re-apply / re-check Grok patches, then:
cd "$GROK" && ./aim doctor && ./aim map
```

After sync, re-apply any lost patches (git diff against last aim-grok commit).

## Pin record

Update `SOURCE.md` with new aim-agy commit SHA after each intentional sync.

---
[← Wiki index](../index.md)
