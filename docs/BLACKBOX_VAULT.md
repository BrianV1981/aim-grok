# Black box vault (Operator forensic seal)

**Issue:** [#12](https://github.com/BrianV1981/aim-grok/issues/12)  
**Status:** aim-grok first; AGY/OpenCode ports follow  

## Intent

Answer: *How do you know the model didn’t alter session history?*

At **reincarnation only**, encrypt the **raw platform transcript** for the session being reincarnated into a vessel-local black box. Derived wiki/markdown is not the court record.

## Policy

| Rule | Value |
|------|--------|
| Scope | **One box per vessel install** — not per agent/tmux |
| When | **`./aim reincarnate` only** — not every pulse, not bulk scrape |
| Failure | **WARN, never block** reincarnate/wiki |
| Key | OS keyring if available; else `~/.aim/blackbox.key` (0600) or `settings.blackbox_key_path` |

## Layout

```text
<vessel>/archive/.raw_jsonl_blackbox/
  <session_id>.enc
  manifest.jsonl          # sha256_plaintext, source_path, sealed_at, …
```

Gitignored. Key material never committed.

## Operator commands

```bash
# After reincarnate, audit a seal (decrypt to stdout)
./aim vault audit <session_id>

# Verify sealed hash vs live file
./aim vault verify <session_id> --live /path/to/updates.jsonl

# Manual seal (still reason=reincarnate; Operator-only)
./aim vault seal --session-id <uuid>
```

## CONFIG

```json
"settings": {
  "blackbox_enabled": true,
  "blackbox_on_reincarnate_only": true,
  "blackbox_key_path": "~/.aim/blackbox.key"
}
```

## Not for agents

Do not treat vault decrypt as a normal self-repair tool. Seal is for **Operator** forensics. Reincarnation memory still uses wiki/pulse per `GOAL_REINCARNATION_MEMORY_WIKI.md`.
