# Contributing to aim-grok

Thanks for helping improve the Grok vessel of A.I.M.

## Before you start

1. **Decide where the change belongs**
   - **Engine / shared A.I.M. behavior** → prefer [aim-agy](https://github.com/BrianV1981/aim-agy), then sync here via `SYNC_FROM_AIM_AGY.md`
   - **Grok-only overlays** (session paths, wiki compiler defaults, vessel docs) → this repo

2. Open a **GitHub Issue** describing the bug or feature.

## Development setup

```bash
git clone https://github.com/BrianV1981/aim-grok.git
cd aim-grok
bash aim-agy_os/setup.sh
mkdir -p aim-agy_os/memory_lance
cp -a aim-agy_os/assets/default_lance/. aim-agy_os/memory_lance/
./aim doctor
```

Optional: Ollama with `nomic-embed-text` for embeddings.

## Workflow (GitOps-friendly)

```bash
# From a clean main
git checkout -b fix/short-description

# Make surgical changes — never commit:
#   aim-agy_os/venv/
#   aim-agy_os/memory_lance/
#   .aim_core/CONFIG.json
#   secrets / .env

./aim doctor
./aim wiki search "smoke"   # if you touched wiki
# pytest if applicable:
#   PYTHONPATH=aim-agy_os:aim-agy_os/.aim_core \
#     aim-agy_os/venv/bin/python -m pytest aim-agy_os/tests/ -v

git add path/to/files   # surgical staging only
git commit -m "Fix: clear description"
git push -u origin HEAD
gh pr create --fill
```

### Commit messages

Prefer conventional, scannable prefixes:

- `Fix:` · `Feat:` · `Docs:` · `Refactor:` · `Test:` · `Sync:`

Reference issues: `(Closes #N)` when applicable.

## Code boundaries

| Do | Don't |
|----|--------|
| Keep Grok overlays in this repo | Blind `git add .` |
| Preserve `vessel_paths.py` and session handoff logic | Commit live memory DBs |
| Match existing style in `.aim_core` | Rewrite large modules without discussion |
| Add a short validation note in the PR | Force-push `main` |

## Grok-specific files (overlays)

Treat these as vessel-owned when syncing from aim-agy:

- `aim-agy_os/.aim_core/vessel_paths.py`
- Grok-aware handoff / extract / wiki compiler paths
- `AGENTS.md`, `./aim`, `.grok/`, vessel docs

See `SYNC_FROM_AIM_AGY.md`.

## Reporting bugs

Include:

- OS / Python version  
- `./aim doctor` output  
- Command run + full error  
- Whether Ollama / Grok auth is configured  

## Code of conduct

Be respectful. Assume good intent. No harassment or spam. Maintainers may close hostile or off-topic interactions.

## License

By contributing, you agree your contributions are licensed under the MIT License (see [LICENSE](LICENSE)).
