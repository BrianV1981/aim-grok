# Handoff vNext — E2E & cron ops

**Issue:** [aim-grok#32](https://github.com/BrianV1981/aim-grok/issues/32) · [aim-agy#116](https://github.com/BrianV1981/aim-agy/issues/116)  
**Plan:** `docs/PLAN_HANDOFF_VNEXT_REINCARNATION.md`

## Three pipelines

| Command | System |
|---------|--------|
| `python -m handoff.cli handoff` | A — Continuity packet |
| `python -m handoff.cli wiki-batch` | B — FR → wiki → embed → DB |
| `python -m handoff.cli blackbox-cron` | C — seal every session |
| `python -m handoff.cli cron-all` | B+C together |
| `python -m handoff.cli e2e-staged` | All three on fixtures |

## Quick E2E (staged history)

```bash
cd /home/kingb/aim-grok
export PYTHONPATH=aim-agy_os:aim-agy_os/.aim_core
aim-agy_os/venv/bin/python3 -m handoff.cli e2e-staged \
  --fixture-root aim-agy_os/tests/fixtures/handoff_vnext \
  --vessel-root "$PWD" \
  --marker E2E_HANDOFF_VNEXT_MARKER_7f3a
```

Expect `{"ok": true}`. Report: `continuity/cron_state/e2e_staged_report.json`.

## Unit tests

```bash
aim-agy_os/venv/bin/python3 -m pytest aim-agy_os/tests/test_handoff_vnext.py -q
```

## Multi-day soak (simulate N nights)

```bash
bash aim-agy_os/scripts/multi_day_handoff_test.sh 3
```

Each “day” plants a new staged session, runs handoff + cron-all, asserts FR, wiki, DB, blackbox.

## Install real crontabs (host)

```bash
bash aim-agy_os/scripts/install_handoff_crontabs.sh
# logs: ~/.aim/cron/logs/
```

Default schedule:
- **02:00** `blackbox-cron` (grok adapter, live sessions)
- **02:15** `cron-all` (blackbox + wiki-batch)

## Outputs

| Path | What |
|------|------|
| `continuity/CURRENT.md` | Latest handoff packet |
| `continuity/handoff_result.json` | Machine result (handoff) |
| `continuity/flight_records/*.md` | Cleaned FR |
| `continuity/cron_state/*_result.json` | Nightly job results |
| `aim-agy_os/memory-wiki/pages/source-*.md` | Wiki pages |
| `aim-agy_os/memory_lance/handoff_vnext/` | Embed store (jsonl + lance) |
| `archive/.raw_jsonl_blackbox/` | Sealed sessions |

## Agent rule

Tickets about these pipelines **require** attaching the relevant `*_result.json`. No JSON → invalid ticket.
