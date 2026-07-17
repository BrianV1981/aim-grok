# Remaining work scoreboard (post four-pillar + blackbox)

**Updated:** 2026-07-17  
**Context:** Four vessels active (agy / grok / opencode / codex). Black box vault fleet-landed.

## Done this cycle

| Item | Evidence |
|------|----------|
| Ecosystem README: aim-codex active (not horizon) | Fleet docs PRs |
| Black box #12 full land (was dangling `881584e`) | aim-grok [PR #21](https://github.com/BrianV1981/aim-grok/pull/21) |
| Fleet blackbox port | agy #107 · opencode #27 · codex #8 |
| Reincarnate hygiene Lane 1 (single wiki spawn, status pulse, vault WARN) | earlier lockstep |
| Codex vessel parity (paths/extract/pulse/teleport) | earlier |
| AGY transcript detect fix | earlier |

## Black box operator usage

```bash
# once per host
mkdir -p ~/.aim && umask 077 && \
  python3 -c "from cryptography.fernet import Fernet; p='$HOME/.aim/blackbox.key'; \
  __import__('pathlib').Path(p).write_bytes(Fernet.generate_key()) if not __import__('pathlib').Path(p).exists() else None"

# automatic: ./aim reincarnate [--session-id UUID]
# manual:
./aim vault seal --session-id <uuid>
./aim vault audit <uuid>
./aim vault verify <uuid> --live /path/to/updates.jsonl
```

Docs: `docs/BLACKBOX_VAULT.md`

## Still open (prioritized)

### P0 — trust / reincarnate completeness
1. **Live reincarnate teleport E2E** on each vessel with exclusive `--session-id` → wiki pages contain marker (bar: `docs/GOAL_REINCARNATION_MEMORY_WIKI.md`). Not blocked by blackbox.
2. **OpenCode ForensicDB / session_bridge** gaps for full summarizer path (Stage 0 multi-page via compiler still works).

### P1 — wiki quality
3. **Stage 1 agent polish** (`AIM_WIKI_MODE=agent`) on one golden source after Stage 0 — optional quality, not structural.
4. **Serial Stage 0 backfill** more archives via `wiki_serial_ingest.sh` (Operator-gated; AGY garbage-heavy).

### P2 — hygiene / polish
5. Grok local skill-tree / worktree noise (D/??) — never blind `git add .`
6. Optional: dual EXCLUSIVE log / root CONFIG path clarity if still confusing on wake
7. Keep SOURCE.md soul pin current after each lockstep merge

## Explicit non-goals right now
- Per-agent black boxes  
- Bulk scrape all historical sessions into vault  
- Making vault part of fleet wiki PASS gate  
- Schema v2 redesign (already shipped)
