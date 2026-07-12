# TOOL_MAP

*Ingested from `seed_tool-map.md` on 2026-07-12*

# TOOL_MAP

*Seeded from `/home/kingb/aim-grok/TOOL_MAP.md`*

# Tool surface map — A.I.M. / AGY → Grok CLI (aim-grok)

Phase 1 mapping for agents operating in this vessel.

## Built-in agent tools

| Intent | Antigravity / Gemini | Grok CLI |
|--------|----------------------|----------|
| Shell | `run_shell_command` / `run_command` | `run_terminal_command` |
| Read file | `read_file` | `read_file` |
| Edit | `replace` / `write_file` | `search_replace` / `write` |
| Search code | `grep_search` | `grep` |
| Web | browser / search tools | `web_search` / `web_fetch` |
| Subagents | AGY tasks | `spawn_subagent` |
| Images | platform-specific | `image_gen` / `image_edit` |

## A.I.M. CLI (shared)

| Command | Purpose |
|---------|---------|
| `./aim search "<q>"` | Hybrid Engram search |
| `./aim map` | Knowledge index |
| `./aim doctor` | Env health (exit 1 on hard errors) |
| `./aim bug` / `fix` / `push` | GitOps |
| `./aim pulse` / reincarnation | Handoffs (Grok transcripts first) |

## Session / memory paths

| Concept | Grok (aim-grok) | AGY (legacy fallback) |
|---------|-----------------|------------------------|
| Session root | `~/.grok/sessions/` | `~/.gemini/antigravity-cli/brain/` |
| Transcript | `<urlencode(cwd)>/<session_id>/chat_history.jsonl` | `<id>/.system_generated/logs/transcript.jsonl` |
| Config key | `paths.tmp_chats_dir` → `~/.grok/sessions` | old default was AGY brain |
| Resolver | `aim-agy_os/.aim_core/vessel_paths.py` | same module, `prefer=agy` |

## Inter-agent

Skill: `aim-communicate` — chalkboard + short tmux paste; Enter after sleep; prefer no Escape for AGY peers.

## MCP

See `.vscode/mcp.json` / `.grok/mcp.json` — `aim-engram` points at this vessel’s `mcp_server.py` + venv.

---
[← Wiki index](../index.md)
