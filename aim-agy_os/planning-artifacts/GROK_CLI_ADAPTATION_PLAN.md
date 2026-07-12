# aim-agy → aim-grok (Grok CLI) adaptation plan

**Status:** aim-agy main is cleaned and merge-complete after P0/P1 (2026-07-11).  
**Goal:** Port / adapt the A.I.M. exoskeleton so **Grok CLI** in `/home/kingb/aim-grok` can run as a first-class vessel (parallel to Antigravity/`agy`).

## Baseline (aim-agy main @ post-merge)

Verified on operator host after squash-merge of PRs #73–#79:

| Check | Result |
|--------|--------|
| Memory untracked | `git ls-files aim-agy_os/memory/**` → 0 |
| Engine code trackable | ~49 `.aim_core` py files tracked |
| `aim doctor` | Present; exits 1 on missing deps |
| CI paths | `aim-agy_os/requirements.txt` + `aim-agy_os/tests/` |
| VERSION | root + `aim-agy_os/VERSION` = `v1.0.7` |
| Dep floors | datasets/lancedb/tantivy/pandas pinned with `>=` |
| Worktrees | Issue worktrees removed |
| Disk | ~395MB checkout (was ~3.8GB) |

## Architecture split

| Layer | Keep in aim-agy | Port / reimplement for aim-grok |
|-------|-----------------|--------------------------------|
| LanceDB RAG, retriever, lance_backend | Source of truth | Copy or submodule / package |
| GitOps CLI (`aim bug/fix/push`) | Source of truth | Wrap via Grok skill + shell |
| Reincarnation pipeline | Source of truth | Path/tool renames for Grok sessions |
| AGENTS.md mandates | Shared philosophy | `.grok` project rules + AGENTS.md |
| Antigravity hooks (`hooks/*.py`) | AGY-specific | Replace with Grok hooks/skills |
| `reasoning_utils` → agy CLI | AGY | Map to `grok` / API |
| tmux inter-agent | Protocol shared | Already in `~/.grok/skills/aim-communicate` |
| MCP server | Portable | Point Grok MCP config at it |
| Install scripts (`install-*.sh`) | AGY install | New `install-grok.sh` path |

## Recommended approach (phased)

### Phase 0 — Workspace bootstrap (aim-grok)
1. Initialize git repo in `/home/kingb/aim-grok` if empty.
2. Either:
   - **A (recommended):** Vendor a thin copy of `aim-agy_os` as `aim-grok_os` with Grok-specific overrides, or  
   - **B:** Git submodule / sparse checkout of `BrianV1981/aim-agy` + overlay.
3. Install Python venv from `aim-agy_os/requirements.txt`.
4. Seed `memory_lance` from `assets/default_lance`.

### Phase 1 — Tool surface mapping
| A.I.M. / AGY | Grok equivalent |
|--------------|-----------------|
| `run_shell_command` / `run_command` | `run_terminal_command` |
| `read_file` / `replace` / `write_file` | `read_file` / `search_replace` / `write` |
| `agy` TUI agent | `grok` interactive session |
| Project skills under `.gemini` | `~/.grok/skills` + `aim-grok/.grok/skills` |
| Hooks in `hooks/` | Grok hooks (`~/.grok` hooks guide) if needed |

### Phase 2 — Skills (already partial)
Migrated user skills live in `~/.grok/skills/`:
- `aim-communicate`, `aim-calc`, `aim-google`, `aim-memory-search`, …
Promote project-scoped copies into `aim-grok/.grok/skills/` for the team.

### Phase 3 — CLI entrypoint
- Shell alias: `aim-grok` → `venv/bin/python aim-agy_os/.aim_core/aim_cli.py` (or forked tree).
- Fix `config_utils` / `find_project_root` for Grok cwd (`/home/kingb/aim-grok`).
- `tmp_chats_dir` currently points at Antigravity brain; add Grok session path (`~/.grok/sessions/...`).

### Phase 4 — Reincarnation & handoffs
- Point session salvage at Grok transcripts, not only AGY brain JSON.
- Keep gameplan SOP; change teleport to spawn `grok` in tmux `aim-grok`.

### Phase 5 — Validation
- `aim doctor` green in aim-grok venv.
- `pytest aim-agy_os/tests/` green.
- Smoke: `aim search`, `aim map`, one `aim bug` dry-run.
- Inter-agent: aim-agy ↔ aim-grok via `aim-communicate`.

## Out of scope for first port
- Full AGY hook parity (cognitive mantra, etc.) — later.
- P2 audit items (remote branch GC, true lockfile, double worktree path bug).
- History rewrite of old memory blobs (already untracked; GC optional).

## Immediate next action
Operator authorizes Phase 0: scaffold aim-grok from cleaned aim-agy main and wire alias + doctor.

— Grok orchestrator
EOF
