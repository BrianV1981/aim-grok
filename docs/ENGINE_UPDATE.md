# Surgical A.I.M. OS engine update

## Model

- **Project repo** (your app / client work) may have any `origin`, or none.
- **A.I.M. OS** lives under nested `aim-agy_os/` and updates **independently**.
- `./aim update engine` does **not** `git pull` your project remote.

## Command

```bash
# from vessel or any project that vendors aim-agy_os/
./aim update engine              # surgical OS file update
./aim update engine --dry-run    # rsync plan only
./aim update engine --rebuild-deps   # also run setup.sh
```

### Upstream (engine payload)

| Env | Default |
|-----|---------|
| `AIM_ENGINE_URL` | `https://github.com/BrianV1981/aim-agy.git` (soul) |
| `AIM_ENGINE_REF` | `main` |

Override for mirrors/offline:

```bash
AIM_ENGINE_URL=https://github.com/you/aim-agy-fork.git ./aim update engine
```

## What is updated

Files under **`aim-agy_os/`** from the engine payload (rsync, no project-tree writes).

## What is preserved (never clobbered)

- User data: `memory/`, `memory_lance/`, `memory-wiki/`, `archive/`, `continuity/`, `planning-artifacts/`, `workspace/`, `venv/`
- Vessel overlays: `vessel_paths.py`, `wiki_compiler.py`, `teleport_engine.py`, `VESSEL_HOST`, `CONFIG.json`, local `handoff/`
- Project root: `AGENTS.md`, `SOURCE.md`, `./aim`, `.grok/`, app source, `.git`

## Receipt

`aim-agy_os/ENGINE_UPDATE_RECEIPT.json` after a successful update.

## Reincarnate spawn (related)

On aim-grok, successor spawn is **Grok** with documented auto-approve:

```bash
grok --always-approve --cwd <workspace>
```

Never `agy --dangerously-skip-permissions` for Grok-family workspaces (see issue #34).
