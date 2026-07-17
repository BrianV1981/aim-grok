# Black box vault: one sealed ground-truth store per vessel (reincarnate-only, non-fatal)

## Summary

Restore and standardize the **Immutable Black Box** session vault across **aim-grok**, **aim-agy**, and **aim-opencode** so Operators can answer:

> “How do I know the LLM didn’t edit/alter the session history?”

**Scope of this work:** one black box **per vessel install** (not per agent/tmux spawn), sealed **only when an explicit reincarnation command runs**, with **non-fatal** failure (WARNING, never block pulse/wiki/reincarnate teleport).

This is a **forensic seal**, not reincarnation memory, not Engram, not the wiki. Derived lore (wiki/archive markdown) remains mutable; the black box holds an **encrypted copy of the raw platform transcript** for that reincarnation event only.

---

## Background / why

- LLMs can hallucinate, soft-pedal failures, or rewrite narratives. Derived artifacts (wiki pages, flight-recorder markdown, post-compact `chat_history`) are **not** sufficient as sole court evidence.
- A black box was implemented earlier (`blackbox_vault.py` + `vault_session` from `session_summarizer`) and worked in some environments (including historical **aim-opencode**).
- Feature was under-documented on purpose (avoid agents “fixing” ground truth) and then **forgotten**.
- On headless hosts it currently fails loudly:

  ```text
  [FATAL] Failed to vault session …: No recommended backend was available
  (Python keyring — no Secret Service / keyrings.alt backend)
  ```

  That log level is wrong: vault failure must **not** look like reincarnation failure. Wiki/reincarnate already continue after the exception; labeling must match reality.

Related recent work (do **not** regress):

- Operator reincarnation → memory-wiki acceptance bar: `docs/GOAL_REINCARNATION_MEMORY_WIKI.md`
- Fleet gate: `scripts/fleet_full_reincarnate_gate.sh` (aim-grok)
- Memory path is independent; **black box is optional forensic bonus**, not a gate for wiki PASS.

---

## Goals

1. **One black box root per vessel tree**  
   Example: `<vessel_root>/archive/.raw_jsonl_blackbox/`  
   - Shared by all agents/sessions of that install.  
   - **Not** one box per reincarnation tmux session or per agent role.

2. **Seal only on explicit reincarnation**  
   Trigger when Operator (or protocol) runs reincarnation, e.g.:
   - `./aim reincarnate` / `aim_reincarnate.py`  
   - Not on every pulse, not on every chat turn, not a bulk scrape of all historical sessions for that vessel type.

3. **What gets sealed**  
   Exactly the **raw transcript used for that reincarnation handoff** (the exclusive session selected for handoff), as platform-native bytes:
   - Grok: prefer durable `updates.jsonl` (or the path handoff already selected), never invent content  
   - AGY: brain `transcript.jsonl` for that session UUID  
   - OpenCode: the `archive/raw` / export JSON used for that handoff  

4. **Non-fatal**  
   - Vault errors → **WARNING** (or `[VAULT] WARN`), never `[FATAL]` that implies pipeline death  
   - Never block: handoff READY, wiki SUCCESS, teleport/spawn, fleet operator E2E green  

5. **Headless-safe keys**  
   - Prefer OS keyring when a backend exists  
   - Fallback: Operator-held key file e.g. `~/.aim/blackbox.key` or `<vessel>/.aim_core/blackbox.key` mode `0600`  
   - Document how Operator creates/rotates the key  

6. **Integrity without always decrypting**  
   Manifest entry per seal: `session_id`, `source_path`, `sealed_at`, `sha256_plaintext`, `blob_path`, `vessel_id`  
   Audit can re-hash current platform file and compare before decrypt.

7. **Operator-only decrypt**  
   `./aim vault audit <session_id>` (or equivalent) prints/decrypts for Operator; agents should not treat this as a normal tool for “self-correction.”

8. **Config flag**  
   ```json
   "settings": {
     "blackbox_enabled": true,
     "blackbox_on_reincarnate_only": true
   }
   ```
   Default: enabled when key material available; always soft-fail if not.

---

## Non-goals

- Scraping every conversation ever for a vessel type  
- Sealing on every `./aim pulse` / handoff without reincarnate (unless Operator later opts in via separate flag — **out of scope**)  
- Replacing `updates.jsonl` / wiki / Engram  
- Nation-state crypto or multi-user HSM  
- Making black box part of fleet wiki PASS criteria  
- Per-agent or per-tmux black box directories  

---

## Proposed design

### Layout (per vessel)

```text
<vessel_root>/
  archive/
    .raw_jsonl_blackbox/          # gitignored
      <session_id>.enc
      manifest.jsonl              # one JSON object per line; no key material
  .aim_core/CONFIG.json           # settings.blackbox_*
```

Key material (not in git):

- Preferred: OS keyring service `aim-system` / account `blackbox-key` (existing code)  
- Fallback: `~/.aim/blackbox.key` (Fernet key, 0600) shared across vessels on the host **or** per-vessel key under vessel root if Operator prefers isolation — **decide in implementation and document one default** (recommend: host `~/.aim/blackbox.key` for simplicity, optional override path in CONFIG).

### Call site

**Primary:** `aim_reincarnate.py` / reincarnation `background_tasks` **after** handoff successfully selects `session_id` + raw transcript path, **before or after** wiki daemon (order flexible; must not gate wiki).

**Remove or demote** opportunistic vault from generic `session_summarizer` “every reincarnate archive process” if that path runs for non-reincarnate wiki process — **reincarnate command only**.

If summarizer is only invoked from reincarnate, vault once in reincarnate orchestrator is cleaner (single choke point).

### API sketch

```python
# blackbox_vault.py (shared contract; vessel-aware roots)
def vault_session(jsonl_or_json_path: str, *, session_id: str, vessel_root: str, reason: str = "reincarnate") -> bool
def audit_vault(session_id: str, *, vessel_root: str) -> None  # Operator decrypt to stdout
def verify_manifest(session_id: str, *, vessel_root: str, live_path: str | None) -> bool  # hash check
```

### Logging

| Event | Level |
|-------|--------|
| Sealed OK | `[VAULT] sealed session=<id> blob=... sha256=...` |
| No key backend / encrypt fail | `[VAULT] WARN skipped: ...` |
| Disabled in CONFIG | `[VAULT] skip blackbox_enabled=false` |
| Not reincarnate context | do not call |

---

## Implementation plan (all three vessels)

### Shared lessons (port carefully)

| Vessel | Raw path at reincarnate | Notes |
|--------|-------------------------|--------|
| **aim-grok** | `vessel_paths` exclusive session → `updates.jsonl` / `chat_history.jsonl` | Prefer path handoff already chose |
| **aim-agy** | brain `.../transcript.jsonl` | UUID parent dir, not basename `transcript` |
| **aim-opencode** | `archive/raw` session JSON for that handoff | Flat or nested export shape |

### Per-repo tasks

1. **Inventory** current `blackbox_vault.py` / callers; list gaps (FATAL, keyring-only, wrong session id basename, seal-on-summarizer).  
2. **Hardening** key fallback + WARN + manifest + sha256.  
3. **Wire** seal only from reincarnate path with exclusive session raw file.  
4. **Gitignore** `archive/.raw_jsonl_blackbox/` and key files.  
5. **Docs** short Operator note (intent, not a how-to for agents to “improve” the vault). Link from reincarnation goal doc as *optional forensic seal*.  
6. **Tests**  
   - Unit: seal → manifest hash → audit decrypt roundtrip (temp dir, file key)  
   - Unit: vault failure does not raise out of reincarnate  
   - Integration: `./aim reincarnate` (or NO_TELEPORT test) creates exactly one new blob for the target session; does **not** bulk-seal other sessions  

### Acceptance criteria

- [x] One box directory per vessel root; no per-agent boxes  
- [x] Reincarnate command seals **only** the session being reincarnated  
- [x] No bulk scrape of all sessions for that vessel type  
- [x] Missing keyring → file key fallback works on headless Linux  
- [x] Vault failure → WARN only; reincarnate + wiki still succeed  
- [x] Manifest includes sha256; `verify` can detect if live log diverged after seal  
- [x] `archive/.raw_jsonl_blackbox/` gitignored  
- [x] CONFIG flags documented  
- [ ] Same contract behavior on **grok / agy / opencode / codex** (paths vessel-native) — fleet port after aim-grok land

---

## Test plan (Operator)

```bash
# Enable key fallback if needed
mkdir -p ~/.aim && umask 077 && python3 -c "from cryptography.fernet import Fernet; open('$HOME/.aim/blackbox.key','wb').write(Fernet.generate_key())"

# Grok (example)
cd /path/to/aim-grok-vessel
# run a short session, note session id, then:
./aim reincarnate --session-id <uuid>   # or vessel-equivalent
ls archive/.raw_jsonl_blackbox/
# expect one new .enc + manifest line for that uuid only

# Negative: break key path → reincarnate still completes; log shows VAULT WARN
```

Repeat with AGY brain session id and OpenCode session export id.

---

## Security / threat model (honest)

- **In scope:** deter/detect casual rewrite of *derived* history; give Operator a sealed snapshot at reincarnate time.  
- **Out of scope:** agent with filesystem write + key file read; root attacker; steganographic edits before seal.  
- Raw platform logs remain the live stream; black box is **point-in-time seal at reincarnate**.

---

## References

- `aim-agy_os/.aim_core/blackbox_vault.py` (existing Fernet + keyring)  
- `hooks/session_summarizer.py` current `vault_session` call (likely relocate)  
- `docs/GOAL_REINCARNATION_MEMORY_WIKI.md` (wiki bar; keep separate)  
- Fleet gate summary 2026-07-15 (vault FATAL observed as non-blocking)  

---

## Suggested labels

`enhancement`, `security`, `reincarnation`, `forensics`, `high-priority`

## Coordination

Open **parallel issues** on aim-grok, aim-agy, aim-opencode with this body (vessel-specific path notes only). Implement shared contract first on one vessel (recommend **aim-grok**), then port adapters. Do not block wiki/fleet green on vault.  
