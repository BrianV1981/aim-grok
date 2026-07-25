# Fleet: reject wiki vacuum — handoff-only ingest

Opened: 2026-07-24

| Pillar | Issue |
|--------|--------|
| aim-grok | https://github.com/BrianV1981/aim-grok/issues/39 |
| aim-agy | https://github.com/BrianV1981/aim-agy/issues/120 |
| aim-opencode | https://github.com/BrianV1981/aim-opencode/issues/37 |
| aim-codex | https://github.com/BrianV1981/aim-codex/issues/18 |

**Policy:** [`HANDOFF_OPT_IN_WIKI_POLICY.md`](./HANDOFF_OPT_IN_WIKI_POLICY.md)

**Amends:** #32 / #116 (nightly wiki vacuum framing)

**Tests:** Full E2E must be **re-run** after pipelines match opt-in law (include control: non-handoff session must not appear in wiki).
