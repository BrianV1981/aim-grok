# Upstream source pin

| Field | Value |
|-------|--------|
| Upstream | https://github.com/BrianV1981/aim-agy |
| Commit | `d07e41b6ac228e8e5a8b60e5a9415f3cc95f1537` |
| Note | Post-merge P0/P1 (#66–#72): memory untracked, install-core fixed, CI, doctor, VERSION, dep floors |
| Vendored path | `aim-agy_os/` (name retained for `config_utils` / installer compatibility) |
| Phase | 0 bootstrap |

To refresh engine from upstream later:

```bash
# from a clean aim-agy main checkout
rsync -a --delete \
  --exclude venv --exclude memory --exclude memory_lance \
  --exclude workspace --exclude archive --exclude '__pycache__' \
  /path/to/aim-agy/aim-agy_os/ .aim_core_staging/
# then carefully merge into aim-agy_os/ preserving aim-grok overlays
```
