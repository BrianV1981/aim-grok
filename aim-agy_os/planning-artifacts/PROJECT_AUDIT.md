# Project Audit: `aim-agy` (A.I.M. / Antigravity)

**Date:** 2026-07-11  
**Path:** `/home/kingb/aim-agy`  
**Remote:** `https://github.com/BrianV1981/aim-agy`  
**Branch:** `main` @ `0723703` (v1.0.7)  
**Working tree:** clean (untracked: `patch.diff` only)

This is a full **project health audit**, not a single-diff code review.

---

## What it is

A.I.M. is an agent “exoskeleton” for Antigravity CLI: LanceDB hybrid RAG, GitOps worktrees, reincarnation/handoffs, MCP, installers, and strong process rules in `AGENTS.md`. Ambition and product vision are clear; operational hygiene and packaging are where the risk sits.

| Metric | Value |
|--------|--------|
| Version | `v1.0.7` (root) / `v1.0.2` (`aim-agy_os/VERSION`) |
| Disk | **~3.8 GB** checkout; **~355 MB** git pack |
| Python core | **~6.8k LOC**, 48 files — all **syntax-OK** |
| Tracked files | 816 (mostly `.lance` / txn / manifest) |
| Open GitHub issues | 8 (epics + bugs) |
| Active worktrees | 4 (issues 59–62) |

---

## Strengths

1. **Clear agent operating system** — GitOps isolation, TDD mandate, blast-radius rules, inquiry vs directive, reincarnation SOP. That is real product differentiation.
2. **Coherent memory design** — `EntityIntersectionReranker`, Tantivy hybrid FTS, temporal decay hooks, parquet “cartridges.” Architecture matches the README story.
3. **Recent installer hardening** — #63–#65 (tmux session names, `cp -a` vs `mv`, trust-prompt matching) show real production debugging.
4. **MCP skill sandbox** — bubblewrap + no network + timeout is a solid security posture for skill execution.
5. **No obvious secrets** in-tree; `.env` / `CONFIG.json` gitignored.
6. **Active roadmap** — aim-connect bridge, co-agents, RAG 6.0, etc.

---

## Critical findings

### 1. CI is dead on arrival

`.github/workflows/test.yml` expects:

- root `requirements.txt`
- `tests/`
- `PYTHONPATH=.../src`

None of those exist. There is **no `tests/` directory** anywhere under the repo despite a hard TDD mandate in docs and `AGENTS.md`.

**Impact:** Every push/PR “test” job fails or no-ops. Agents cannot empirically prove changes via the documented pipeline.

---

### 2. `install-core.sh` is broken

```bash
# after clone into .aim_temp_clone
./setup.sh   # DOES NOT EXIST at repo root
```

`setup.sh` lives only at `aim-agy_os/setup.sh`. Clean/agent installers call the nested path; core still does not. Comment still points at `main/install-core.sh` (pre-move URL).

**Impact:** “Core contributor” install path fails immediately. README curl URL was partly fixed (see untracked `patch.diff`); script body was not.

---

### 3. Repo bloat: live LanceDB committed to git

- ~**570** tracked files under `aim-agy_os/memory/lance/`
- Individual data blobs ~**98 MB** each
- Pack size **~355 MB**

Runtime memory is versioned as source. Clone time, PR diffs, and history will stay heavy forever unless rewritten.

Default seed under `assets/default_lance/` (150 files) is a better model; **`memory/` should not be tracked.**

---

### 4. `.gitignore` fights the repo layout

Root `.gitignore` ignores:

```
.aim_core/
aim-agy_os/
AGENTS.md
memory-wiki/
workspace/
```

Those paths **are already tracked**, so ignore only applies to **new** untracked files. Contributors who `git add .` will **silently skip** new Python under `aim-agy_os/.aim_core/`.

**Impact:** Easy to “fix” something and never commit it. Opposite of GitOps hygiene the project preaches.

---

### 5. Stale worktrees: ~2.8 GB wasted

| Worktree | Branch | Tip (old) |
|----------|--------|-----------|
| `workspace/issue-59` | `fix/issue-59` | reincarnation modularize |
| `workspace/issue-60` | `fix/issue-60` | tmux polling |
| `workspace/issue-61` | `fix/issue-61` | session-id arg |
| `workspace/issue-62` | `fix/issue-62` | scaffolding |

All of those issues are already merged to `main` (commits `99bab32` … `9568385`). `AGENTS.md` requires cleanup via promote / `git worktree remove`; it was not done.

---

### 6. Broken CLI entry: `aim doctor`

```python
def cmd_doctor(args):
    run_script(os.path.join(AIM_CORE_DIR, "aim_doctor.py"), [])
```

**`aim_doctor.py` does not exist.** Registered in argparse; will always fail at runtime.

---

## High / medium findings

### Dual memory paths (confusion + installer split-brain)

| Path | Role today |
|------|------------|
| `memory_lance/` | What `lance_backend.py` actually uses |
| `memory/lance/` | Large, tracked, **695 MB** on disk; install-core copies assets **here** |
| `assets/default_lance/` | Intended seed ROM |

Clean/agent installers copy → `memory_lance/`. Core installer copies → `memory/lance/`. Runtime only reads `memory_lance/`. Core path seeds the **wrong** tree.

### Version schema chaos

Changelog goes `v1.71.x` → then `v1.0.3` … `v1.0.7`. Root `VERSION` is `v1.0.7`; `aim-agy_os/VERSION` is `v1.0.2`. Semver consumers and release automation cannot trust this.

### Install surface area / host safety

- `curl | bash` install is convenient but trust-heavy.
- Clean/agent use `cp -a aim-agy_os ../` into the **current** project (reasonable).
- Core uses `shopt -s dotglob; cp -a * ../` — can overwrite host files and copy unexpected tree layout.
- Installers mutate `~/.bashrc` / `~/.zshrc` and set `NODE_OPTIONS=--max-old-space-size=16384` (16 GB) by default.

### Docs / code drift

- `.aim_core/README.md` still describes `forensic_utils.py` as top-level and “tier summarizers” that are not present that way (`forensic_utils` lives under `plugins/datajack/`).
- `TOOLS.md` is effectively a stub.
- Philosophy docs are strong; mechanical maps lag.

### Dependencies

`requirements.txt`: ranges only, no lockfile, bare `datasets` / `lancedb` / `pandas`. Reproducible installs and CI will drift.

### Error handling

~**83** broad `except Exception`, ~**20** bare `except:` in core. Fine for CLI resilience; bad for diagnosing production failures.

### Branch sprawl

~17 local branches, ~59 remote (`archive-fix/*`, `fix/issue-*`). Worktree isolation is good; lifecycle automation is incomplete.

### Dead local artifact

Untracked `patch.diff` only fixes README installer URLs — still not applied/committed as a proper PR.

---

## Architecture snapshot (healthy core)

```
aim-agy/                    # host / product root
├── AGENTS.md               # agent constitution
├── aim-agy_os/             # OS payload
│   ├── .aim_core/          # Python engine (CLI, RAG, reincarnation, MCP)
│   ├── hooks/              # Antigravity hooks
│   ├── install-*.sh        # bootstrap
│   ├── assets/default_*    # seed memory
│   ├── memory_lance/       # LIVE DB (runtime)
│   ├── memory/lance/       # LEGACY/tracked DB (bloat)
│   └── workspace/issue-*   # stale worktrees
└── .github/workflows/      # CI (misaligned)
```

Core modules of note: `aim_cli.py` (~44k), `aim_config.py`, `retriever.py` + `lance_backend.py`, `reincarnation/*`, `reasoning_utils.py`, `mcp_server.py`.

---

## Priority remediation backlog

| Priority | Action | Why |
|----------|--------|-----|
| P0 | Fix `install-core.sh` → `./aim-agy_os/setup.sh` + copy to `memory_lance/` | Broken install path |
| P0 | Remove `aim-agy_os/memory/` from git (keep `assets/default_lance` only); fix `.gitignore` so `aim-agy_os/.aim_core/**` *is* tracked deliberately | Size + contributor footgun |
| P0 | Rewrite CI: install from `aim-agy_os/requirements.txt`, `pytest` real tests under a real tree | TDD credibility |
| P0 | Prune worktrees 59–62 + merged `fix/issue-*` branches | Recover ~2.8 GB |
| P1 | Implement or remove `aim doctor` | Dead command |
| P1 | Align VERSION files; pick one semver line (1.71 or 1.0) | Releases |
| P1 | Pin deps or add lockfile | Reproducibility |
| P2 | Refresh core README / SCRIPT_MAP / TOOLS.md | Onboarding |
| P2 | Branch retention policy (auto-archive after promote) | Hygiene |
| P2 | Soften default Node heap or document why 16 GB | Host impact |

---

## Overall assessment

| Dimension | Grade | Notes |
|-----------|-------|--------|
| Vision / product | **A−** | Strong differentiation, clear agent mandates |
| Core engine design | **B+** | Hybrid RAG + GitOps + reincarnation is coherent |
| Packaging / install | **D+** | Core installer broken; path dualism |
| Testing / CI | **F** | No suite; CI targets missing paths |
| Repo hygiene | **D** | 3.8 GB disk, 355 MB pack, stale worktrees, ignore mismatch |
| Docs quality | **B** | Philosophy excellent; mechanical docs stale |
| Security posture | **B−** | Sandbox good; curl\|bash + shell alias mutation need care |
| Active maintenance | **A−** | Rapid issue-driven fixes on main |

**Bottom line:** The *ideas and core Python engine* are mature and intentional. The *shipping surface* (installers, CI, gitignore, memory in git, worktree lifecycle) is the weak layer and will block external adopters and slow agents that depend on `aim doctor` / green CI.

---

## Suggested follow-ups

1. **Remediate P0** (installer, gitignore, worktree cleanup, CI skeleton)
2. **Deep-dive** one subsystem (RAG, reincarnation, or install path)
3. **Write formal design fixes** as tickets (`aim bug`-style) for the open issues

---

## Audit metadata

- **Auditor:** Grok (xAI) project audit session
- **Scope:** Full repository health (structure, packaging, CI, hygiene, security, docs drift)
- **Method:** Tree inventory, git history/worktrees, install-script path analysis, tracked-blob sizing, Python syntax compile of `.aim_core`, secret-pattern scan, open GitHub issue listing
- **Not covered:** Full runtime integration tests against live Ollama/Antigravity; production API key handling beyond static scan
