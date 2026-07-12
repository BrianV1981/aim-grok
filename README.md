# aim-grok

**A.I.M. for [Grok CLI](https://x.ai)** — the Grok vessel of [Actual Intelligent Memory](https://github.com/BrianV1981/aim-agy).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v0.2.1-blue.svg)](VERSION)
[![Status](https://img.shields.io/badge/status-v0%20vessel-green.svg)](#status)

aim-grok wraps the A.I.M. engine around **Grok CLI** so long-running coding agents get:

- **Hybrid RAG memory** (LanceDB + Tantivy FTS + local embeddings)
- **Persistent memory wiki** (searchable markdown lore under `memory-wiki/`)
- **GitOps discipline** (`aim bug` → `aim fix` → `aim push`)
- **Session handoffs** (`aim pulse`) using Grok `chat_history.jsonl`
- **Project skills** under `.grok/skills/`

Upstream engine source of truth: **[aim-agy](https://github.com/BrianV1981/aim-agy)** (Antigravity flagship).  
This repo is the **Grok-adapted vessel**: vendored engine + Grok-only overlays.

---

## Requirements

| Dependency | Notes |
|------------|--------|
| **Linux** or **WSL (Ubuntu)** | Primary target |
| **Python 3.10+** | 3.12 tested |
| **Grok CLI** (`grok`) | Authenticated (e.g. SuperGrok) |
| **Ollama** (recommended) | `nomic-embed-text` for embeddings |
| **git**, **tmux** | GitOps + optional multi-agent |
| **gh** (optional) | Issue sync / PR workflows |

---

## Quickstart

```bash
git clone https://github.com/BrianV1981/aim-grok.git
cd aim-grok

# Build Python backend
bash aim-agy_os/setup.sh

# Seed live memory from default ROM (once)
mkdir -p aim-agy_os/memory_lance
cp -a aim-agy_os/assets/default_lance/. aim-agy_os/memory_lance/

# Health check
./aim doctor
./aim map

# Memory wiki (first time)
./aim wiki bootstrap
./aim wiki search "vessel"

# Start Grok in this workspace
grok
# or: tmux attach -t aim-grok
```

CLI entrypoint:

```bash
./aim <command>
# equivalent to:
# aim-agy_os/venv/bin/python3 aim-agy_os/.aim_core/aim_cli.py <command>
```

Optional shell alias:

```bash
alias aim-grok='NODE_OPTIONS="--max-old-space-size=8192" /path/to/aim-grok/aim-agy_os/venv/bin/python3 /path/to/aim-grok/aim-agy_os/.aim_core/aim_cli.py'
```

---

## Core commands

| Command | Purpose |
|---------|---------|
| `./aim doctor` | Environment health (exit `1` on hard errors) |
| `./aim map` | Knowledge map (Engram index) |
| `./aim search "<query>"` | Hybrid RAG search |
| `./aim wiki search "<q>"` | Lexical search over `memory-wiki/` |
| `./aim wiki process` | Compile `_ingest/` → wiki pages (deterministic) |
| `./aim wiki bootstrap` | Seed docs + recent history into the wiki |
| `./aim pulse` | Session handoff / flight recorder from Grok transcripts |
| `./aim bug` / `fix` / `push` | GitOps issue → worktree → PR |

More: [`TOOLS.md`](TOOLS.md) · [`TOOL_MAP.md`](TOOL_MAP.md) (Grok vs AGY tool surface)

---

## Memory wiki

The persistent wiki lives at `aim-agy_os/memory-wiki/`.

```bash
# Drop notes for processing
echo "# My note\n\nFacts here..." > aim-agy_os/memory-wiki/_ingest/my-note.md
./aim wiki process

# Browse
less aim-agy_os/memory-wiki/index.md
ls aim-agy_os/memory-wiki/pages/
```

Default processing is **deterministic** (no second agent required).  
Optional agent mode: `AIM_WIKI_MODE=agent AIM_WIKI_AGENT=grok ./aim wiki process`

After `./aim pulse`, the summarizer can feed session history into the wiki automatically.

---

## Layout

```text
aim-grok/
├── aim                 # CLI wrapper
├── AGENTS.md           # Agent operating rules (Grok vessel)
├── README.md
├── CONTRIBUTING.md
├── CONTRIBUTORS.md
├── LICENSE
├── VERSION
├── SOURCE.md           # Upstream pin (aim-agy commit)
├── SYNC_FROM_AIM_AGY.md
├── TOOL_MAP.md
├── TOOLS.md
├── .grok/skills/       # Project Grok skills
├── .github/workflows/  # CI
├── workspace/          # aim fix worktrees (gitignored content)
└── aim-agy_os/         # Vendored A.I.M. engine (+ Grok overlays)
    ├── .aim_core/      # Python engine (CLI, RAG, wiki, reincarnation)
    ├── assets/         # Default seed ROM
    ├── memory_lance/   # Live DB (gitignored)
    ├── memory-wiki/    # Persistent markdown wiki
    ├── hooks/          # Background summarizer, etc.
    └── tests/
```

The directory name `aim-agy_os` is kept for path compatibility with the upstream engine. Product name and entrypoint are **aim-grok**.

---

## Status (v0.2.1)

| Area | State |
|------|--------|
| Engine bootstrap + venv | Done |
| Grok session paths (`vessel_paths`) | Done |
| Hybrid search + doctor | Done |
| Memory wiki (deterministic) | Done |
| Upstream sync from aim-agy P2 | Done (`947c538`) |
| Full reincarnate teleport UX | Partial |
| Multi-host install polish | Evolving (v0) |

This is a **v0 vessel**: usable for daily Grok + A.I.M. workflows; APIs and layout may still shift.

---

## Relation to aim-agy

| Repo | Role |
|------|------|
| [**aim-agy**](https://github.com/BrianV1981/aim-agy) | Flagship A.I.M. engine (Antigravity CLI) |
| **aim-grok** (this repo) | Grok CLI vessel + overlays |

Sync procedure: [`SYNC_FROM_AIM_AGY.md`](SYNC_FROM_AIM_AGY.md)  
Upstream pin: [`SOURCE.md`](SOURCE.md)

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CONTRIBUTORS.md`](CONTRIBUTORS.md).

Surgical commits, GitOps branches, and tests preferred. Do not commit `venv/`, live `memory_lance/`, or secrets.

---

## Security

See [`SECURITY.md`](SECURITY.md). Never commit API keys or `.aim_core/CONFIG.json`.

---

## License

[MIT](LICENSE) — Copyright (c) 2026 Brian Vasquez

---

## Support

- Issues: use GitHub Issues on this repo  
- Upstream engine issues: [aim-agy](https://github.com/BrianV1981/aim-agy/issues)  
- Coffee: [buymeacoffee.com/brianv1981](https://buymeacoffee.com/brianv1981)
