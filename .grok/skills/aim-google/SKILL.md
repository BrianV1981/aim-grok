---
name: aim-google
description: >
  Use the aim-google CLI for Gmail, Calendar, Drive, Docs, Sheets, Tasks, and Chat.
  Activate when reading email, scheduling, Drive/Docs, or Google Workspace tasks.
  Slash: /aim-google. Migrated from aim/.gemini/skills/aim-google.
---

# aim-google: Workspace Gateway

Do **not** invent Google API scripts. Use the installed CLI (OAuth, backoff, JSON).

Binary: `aim-google` (typically `~/.local/bin/aim-google`).

## Context efficiency

Always pass **`--agent`** when results go back into the model context — strips whitespace and verbose envelopes.

```bash
aim-google gmail search "is:unread" --agent
aim-google gmail get <message_id> --agent
aim-google calendar events list --agent
aim-google drive ls --agent
aim-google docs get <doc_id> --agent
```

## Pattern

```bash
aim-google <service> <command> [flags] --agent
```

## Errors

- On HTTP 429/503, brief wait and retry (CLI already retries with backoff).
- On exit code > 0, read telemetry: `~/.config/aim-google/execution.log` before guessing.
