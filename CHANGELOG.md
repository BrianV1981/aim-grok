# Changelog — aim-grok

## [v0.2.1-sync] - 2026-07-12
- Sync engine from aim-agy `947c538` (P2: path, heap, docs, traceback, CI, prune-remote)
- Preserved Grok overlays (`vessel_paths`, session handoff, vessel `config_utils`)
- CI workflow + TOOLS.md updated from upstream

## [v0.2.0-phase1] - 2026-07-11
- `vessel_paths.py`: resolve Grok `chat_history.jsonl` (+ AGY fallback)
- Handoff / porter / recover_json_logs use vessel paths
- `extract_signal` understands Grok `assistant` + `reasoning` roles
- Project skills promoted under `.grok/skills/aim-*`
- MCP configs: `.vscode/mcp.json`, `.grok/mcp.json`
- Docs: `TOOL_MAP.md`, `SYNC_FROM_AIM_AGY.md`

## [v0.1.0-phase0] - 2026-07-11
- Phase 0: scaffold from aim-agy `d07e41b`
- Vendored engine under `aim-agy_os/`, venv + seeded `memory_lance`
- Added `./aim` wrapper, Grok-oriented `AGENTS.md` / `README.md`
- Project skill stubs under `.grok/skills/`
