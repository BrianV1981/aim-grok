# aim-grok reincarnate spawn = grok (auto-approve), never AGY

**GitHub:** https://github.com/BrianV1981/aim-grok/issues/34

## Operator rule (corrected)
Successor on aim-grok = **Grok** with documented auto-approve flags, e.g.:

```bash
grok --always-approve --cwd <workspace>
```

**Not** `agy --dangerously-skip-permissions`.  
**Not** inventing `--yolo` unless docs say so (Operator clarified: not yolo).

## Finding
`teleport_engine._resolve_vessel_cli` falls through to AGY when both binaries exist and path is not clearly `aim-grok*`. Happy path already uses `--always-approve`; the bug is **wrong CLI family**, not the approve flag name.
