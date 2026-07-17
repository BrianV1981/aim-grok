# Fleet reincarnate → memory-wiki E2E (2026-07-17)

Operator acceptance bar from `docs/GOAL_REINCARNATION_MEMORY_WIKI.md`.

| Vessel | Harness | Verdict | Notes |
|--------|---------|---------|-------|
| **aim-grok** | `operator_reincarnate_wiki_e2e.py` | **PASS** | Marker in archive + FR + wiki pages; vault sealed |
| **aim-agy** | `operator_reincarnate_wiki_e2e_agy.py` | **PASS** | Brain transcript plant; vault seal via AGY fallback |
| **aim-opencode** | `operator_reincarnate_wiki_e2e_oc.py` | **PASS** | Fixed: OpenCode `messages[]` extract + wiki path |
| **aim-codex** | `operator_reincarnate_wiki_e2e_codex.py` | **PASS** | Codex rollout plant; exclusive session-id |

## Fixes landed with this run

1. **OpenCode extract** — single-JSON `session-*.json` with `messages[]` was `unknown` / 0 turns; now `opencode_session`.
2. **OC E2E wiki root** — preferred nested `aim-agy_os/memory-wiki` over stale vessel-root wiki.
3. **Black box `seal_for_reincarnate`** — AGY/OC/Codex fallbacks when `vessel_paths` missing or empty (soul had no `vessel_paths.py`).
4. **Serial Stage 0** — re-ran golden wiki schema ingest successfully.

## Not in this gate

- Full `./aim reincarnate` **tmux teleport** (wiki bar uses exclusive pulse; teleport is separate UX step).
- Stage 1 LLM agent polish (`AIM_WIKI_MODE=agent`) — still optional quality.
- Dual SUCCESS lines in daemon (cosmetic; page graph is real).
