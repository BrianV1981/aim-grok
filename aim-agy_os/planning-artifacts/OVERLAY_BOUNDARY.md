# Overlay Boundary (Host-Agnostic Engine)

The `aim-agy` engine is the host-agnostic source of truth for the fleet. When nested in other vessels (`aim-grok`, `aim-opencode`), respect this boundary to maintain sync lockstep:

## Shared DNA (MUST NOT be forked/changed by vessels)
- `session_naming` API
- `aim doctor` logic and checks
- `lance_backend` data schema and FTS ensure logic
- Reincarnation package shape (`REINCARNATION_GAMEPLAN.md` parsing)

## Vessel Overlay (MAY be adapted by vessels)
- Teleport CLI routing (`aim_reincarnate.py` specific hook execution)
- `extract_signal` memory parsing
- Vessel-specific filesystem paths and workspace root definitions
