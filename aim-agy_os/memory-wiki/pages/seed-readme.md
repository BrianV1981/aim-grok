# README

*Ingested from `seed_readme.md` on 2026-07-12*

# README

*Seeded from `/home/kingb/aim-grok/README.md`*

# aim-grok

**A.I.M. for Grok CLI** — Phase 0 scaffold.

This workspace ports the [aim-agy](https://github.com/BrianV1981/aim-agy) engine so [Grok](https://x.ai) CLI (`grok`) can run as a sovereign vessel with hybrid LanceDB memory, GitOps tooling, and shared inter-agent protocols.

## Status

| Phase | State |
|-------|--------|
| 0 — Bootstrap engine + venv + seed memory | **Done** |
| 1 — Tool surface / Grok sessions / skills / MCP | **Done** |
| 2 — Deeper reincarnation UX + hook parity | Next |
| 3 — Optional GitHub remote + CI on aim-grok | Later |

**Upstream pin:** `aim-agy` `d07e41b` (post P0/P1 cleanup merges #66–#72).

## Layout

```text
aim-grok/                 # project root (this repo / Grok cwd)
├── AGENTS.md             # Grok-oriented operating rules
├── aim-agy_os/           # A.I.M. engine (vendored from aim-agy; dir name kept for path compat)
│   ├── .aim_core/        # Python CLI + RAG + reincarnation
│   ├── memory_lance/     # live RAM DB (gitignored)
│   ├── assets/           # default seed ROM
│   ├── venv/             # python env (gitignored)
│   └── tests/
├── .grok/skills/         # project Grok skills
└── workspace/            # git worktrees for aim fix
```

The folder is still named `aim-agy_os` so `config_utils.OS_ROOT` and installers keep working without a mass rename. Branding and entrypoint are **aim-grok**.

## Quickstart

```bash
cd /home/kingb/aim-grok

# already run in Phase 0 — recreate if needed:
# bash aim-agy_os/setup.sh
# mkdir -p aim-agy_os/memory_lance && cp -a aim-agy_os/assets/default_lance/. aim-agy_os/memory_lance/

# CLI (venv)
./aim search "GitOps"
./aim map
./aim doctor

# or:
aim-agy_os/venv/bin/python3 aim-agy_os/.aim_core/aim_cli.py doctor
```

Optional shell alias:

```bash
alias aim-grok='NODE_OPTIONS="--max-old-space-size=8192" /home/kingb/aim-grok/aim-agy_os/venv/bin/python3 /home/kingb/aim-grok/aim-agy_os/.aim_core/aim_cli.py'
```

## Grok session

Start Grok with this workspace as cwd:

```bash
cd /home/kingb/aim-grok && grok
# or attach tmux session aim-grok
```

Skills: user-level under `~/.grok/skills/aim-*`; project skills under `.grok/skills/`.

## Relation to aim-agy

| Repo | Role |
|------|------|
| **aim-agy** | Flagship engine for Antigravity CLI; upstream source of truth |
| **aim-grok** | Grok CLI adaptation / vessel; vendors engine + Grok overlays |

Sync process (later): cherry-pick or rsync `.aim_core` from aim-agy main; keep Grok-only files here.

## License

MIT (same as aim-agy).

---
[← Wiki index](../index.md)
