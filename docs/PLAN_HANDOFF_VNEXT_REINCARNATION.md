> **Operator status (2026-07-23):** Agrees with ~95% of this plan. Archived from plan-mode draft for local docs/artifacts.  
> **Architecture amendment (same day):** Split **handoff** vs **wiki batch** vs **blackbox cron**; Flight Recorder cleans sessions before embed → DB. See §0.

# Plan: Reincarnation vNext — from scratch, agent-proof

**Mode:** Design only (no implementation in this turn)  
**Operator mandate:** Full overhaul. Current stack is too fragile and depends on agents not being stupid.  
**Constraint:** Codex on hold indefinitely — design must work for **agy / grok / opencode** first; codex adapter later.

---

## 0. Architecture amendment — three independent systems (Operator direction)

**Do not glue handoff, wiki, and vault into one process.** They share adapters/schemas where useful; they do **not** share critical-path success.

| System | Trigger | Job | Explicit non-jobs |
|--------|---------|-----|-------------------|
| **A. Handoff / reincarnation** | On demand (Operator CLI, optional precompact/Stop hook) | Continuity packet for the *next* mind — content-gated, agent-proof | Wiki enrich, vault seal, spawn agents |
| **B. Wiki batch + memory** | **Nightly cron** (methodical) | By **conversation root (cwd / project folder)**: Flight Recorder clean-up → wiki pages for that root → **embed → save into the database** | Mid-session handoff, teleport, agent ceremonies |
| **C. Blackbox backup** | **Nightly cron** (every session) | Encrypt/seal raw transcripts into the vessel black box | Handoff exit code, wiki SUCCESS |

```text
  LIVE SESSION                    NIGHTLY CRON (no agents required)
  ─────────────                   ────────────────────────────────
  context full / Operator
       │
       ▼
  ./aim handoff  ──► continuity/CURRENT.md
                     handoff_result.json
                     (optional --spawn later)

                              ┌── raw hosts (grok/agy/oc …)
                              ▼
                         HostAdapter.resolve_all
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         Blackbox seal   Flight Recorder   Wiki writer
         (every session)  (clean markdown)  (by cwd root)
                              │               │
                              └───────┬───────┘
                                      ▼
                              Embed chunks → LanceDB / memory DB
                              (only after clean FR exists)
```

### 0.1 Flight Recorder in the nightly pipeline (required)

Documented contract:

1. **Input:** native session log for a session-id (via HostAdapter).  
2. **Flight Recorder** produces a **cleaned** human-readable markdown record (modes: cleaned default; chat_only/hybrid/full available offline).  
3. That cleaned record is the **canonical text** for wiki page bodies and for **embedding**.  
4. **Only after** FR output exists and passes basic non-empty checks:  
   - write/update wiki under the project root that owned the conversation  
   - chunk + **embed**  
   - **persist vectors/rows into the memory database** (e.g. Lance / vessel memory store)  
5. Raw jsonl is **not** what we embed by default (noise, tools, noise tokens). Raw stays for blackbox + optional full FR.

### 0.2 Grouping rule for wiki cron

- Session → `cwd` / workspace root from host metadata (or path encoding).  
- Map root → vessel/project wiki root (e.g. `/home/kingb/aim-grok` → that repo’s `memory-wiki`).  
- One session never “infects” another project’s wiki because an agent was confused.

### 0.3 Why this split is non-negotiable

- Handoff stays **fast** when context dies.  
- Wiki/embed can be **slow, retryable, re-runnable** without blocking reincarnate.  
- Blackbox is **forensic insurance**, not a side effect of a flaky handoff.  
- Agents **consume** packets + wiki; they do **not** operate infrastructure.

---

## 1. What reincarnation (handoff) actually is

Reincarnation is **not**:
- A fancy wiki compile
- A fleet orchestration protocol
- A multi-agent conversation ritual
- A “daemon SUCCESS” line in a log
- Nightly embed/cron (that is system B/C)

Reincarnation **is** one Operator outcome:

> **When a session dies (context full, crash, intentional handoff), a new session can start and continue the same work without the Operator re-explaining the campaign — and without trusting the dead chat window.**

Handoff **must** produce:

| # | Artifact | Question it answers |
|---|----------|---------------------|
| 1 | **Continuity packet** | What was I doing, what’s next, what must not be forgotten? |
| 2 | **handoff_result.json** | Machine proof of ok / empty / error (no fake SUCCESS) |

Wiki memory index + blackbox seal are **durable facts of the fleet**, but they are produced by **cron systems B and C**, not by the handoff critical path.

**Teleport** (spawn a new tmux pane) is **UX sugar** on top of (1). It is not reincarnation itself. Default direction: **no agent spin-up as part of handoff.**

---

## 2. Why the current system fails (diagnosis)

We did not fail because reincarnation is hard. We failed because the design **outsources correctness to agents** and **spreads one job across too many moving parts**.

### 2.1 Failure modes we lived through

| Failure | Root cause |
|---------|------------|
| False SUCCESS / empty handoff | Pass gates on process cosmetics (CONFIG load, daemon line) not **content** |
| 0 turns / wrong session | Smart extract + multi-format detection + “newest file” heuristics |
| Dual SUCCESS, dual spawns | Two writers to one log; two owners of “when to wiki” |
| Agents open false tickets | Pipeline is opaque; agents invent theories instead of reading a single machine-readable result |
| Fleet “lockstep” drama | Shared engine + vessel overlays + peer agents expected to sync themselves |
| aim-agy-claude noise | Orchestration relies on agents knowing the **social graph** of the fleet |
| Codex adapter fragility | Host-specific paths buried inside shared “soul” logic |

### 2.2 Architectural smell

Today’s path is roughly:

```text
agent guesses reincarnate
  → aim_reincarnate.py
    → gameplan_manager
    → handoff_pulse_generator
      → extract_signal (format zoo)
      → archive md
      → spawn session_summarizer
        → stage0 multi-page
        → maybe lance
        → maybe dual write
    → blackbox seal
    → teleport_engine
    → wake prompt file
```

~1400+ LOC across core modules alone, plus harnesses, plus per-vessel overlays.  
**Every branch is a place an agent can “help” and break production.**

### 2.3 The real principle we violated

> **Anything an agent must remember to do will eventually be forgotten, half-done, or done wrong.**

So reincarnation cannot depend on:
- Agents remembering REPLY_TO / FROM
- Agents pulling main / syncing soul
- Agents choosing the right session-id
- Agents not filing tickets about phantom pipeline bugs
- Agents interpreting “HANDOFF READY” as success

---

## 3. Design thesis (the best idea)

### One sentence

**Reincarnation becomes a single deterministic program with a hard content gate, a single JSON result, and a fixed Continuity Packet schema — hosts only supply a transcript adapter; agents never “run” the pipeline, they only consume the packet.**

### Design laws

1. **One command, one owner**  
   `./aim handoff` (or `./aim reincarnate`) does everything that must be true. No parallel “also run the summarizer.”

2. **Content-gated success**  
   Exit code **0** only if Continuity Packet contains required fields **and** Operator marker / directives are present in outputs.  
   Exit code **2** = empty/no session.  
   Exit code **1** = hard failure.  
   **Never** print SUCCESS and exit 0 on empty.

3. **Machine-readable result first**  
   Always write `handoff_result.json` (schema-versioned). Humans read markdown; agents and CI read JSON. False tickets die when the JSON says `status: ok|empty|error` with codes.

4. **Host adapters are dumb and tiny**  
   Shared core never greps `~/.codex` vs `~/.grok`.  
   Adapter interface: `resolve(session_id|latest) → TranscriptHandle` and `iter_turns(handle) → Turn[]`.  
   One adapter file per host. No smart multi-format zoo in shared code.

5. **Continuity Packet is the only thing the next agent sees**  
   Wake prompt is generated **only** from the packet. Not from half-parsed wiki pages, not from fleet dispatches.

6. **Memory is append-only, boring, deterministic**  
   Stage 0 style: write one `source-{id}.md` + update log/index.  
   No agent-LLM “polish” on the critical path. Stage 1 polish is offline optional.

7. **Agents are consumers, not operators of reincarnation**  
   Operator (or precompact hook) runs handoff.  
   New agent reads packet.  
   Agents are **forbidden** from “fixing” the handoff pipeline unless `handoff_result.json` proves a real defect.

8. **Teleport is optional and last**  
   `--spawn` flag only after packet is sealed. Default is no kill / no pane swap.

---

## 4. Target architecture

```text
┌─────────────────────────────────────────────────────────┐
│  ./aim handoff [--session-id UUID] [--spawn]            │
└───────────────────────────┬─────────────────────────────┘
                            │
              ┌─────────────▼─────────────┐
              │  HANDOFF CORE (shared)    │
              │  pure, deterministic      │
              └─────────────┬─────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
   HostAdapter        PacketBuilder      MemoryWriter
   (vessel-local)     (schema v1)        (wiki Stage0)
         │                  │                  │
         ▼                  ▼                  ▼
   turns.jsonl         CONTINUITY.md      pages/source-*.md
   raw seal            CURRENT_PULSE      log.md / index.md
                       handoff_result.json
                            │
                     optional --spawn
                            ▼
                     SpawnAdapter (tmux)
```

### 4.1 Continuity Packet (schema v1) — the product

Path (fixed):

```text
<vessel>/continuity/CURRENT.md          # always the latest
<vessel>/continuity/history/{id}.md     # immutable archive of each handoff
<vessel>/continuity/handoff_result.json # last run machine result
```

Required sections in `CURRENT.md` (fail if any missing or empty after a non-empty session):

```markdown
# Continuity Packet
Schema-Version: 1
Session-Id: ...
Vessel: aim-grok
Generated: ISO-8601
Turn-Count: N

## Commander Summary
(≤ 12 lines: what this campaign is)

## Now
- Active goal
- Active branch / worktree
- Blockers

## Do Next
1. ...
2. ...
3. ...

## Do Not Forget
- Operator directives / decisions / constraints (verbatim bullets)

## Evidence
- source_path: ...
- archive_path: ...
- wiki_page: ...
- raw_seal: optional

## Self-check
- marker: <uuid or directive hash>
- turn_count: N
- status: ok
```

**Wake prompt for new session = only this file** (plus AGENTS.md).  
No reincarnation gameplan novel. No fleet dissertation.

### 4.2 HostAdapter interface (the only host-specific code)

```python
class HostAdapter(Protocol):
    name: str  # grok | agy | opencode | codex

    def resolve(self, session_id: str | None, cwd: Path) -> TranscriptRef:
        """Return exact path + session_id. Fail loud if not found.
        Never silently pick a different session when session_id is set.
        """

    def iter_turns(self, ref: TranscriptRef) -> Iterable[Turn]:
        """Yield Turn(role, ts, text). No tools required for gate."""

    def default_session_id(self) -> str | None:
        """Optional: latest for this cwd only. Prefer explicit id."""
```

Adapters live in:

```text
aim-agy_os/handoff/adapters/{grok,agy,opencode}.py
```

Shared core **imports one adapter** from vessel config (`AIM_HOST=grok`), not via auto-detect soup.

### 4.3 Hard gates for **handoff only** (kill false greens)

| Gate | Rule |
|------|------|
| G0 | Adapter resolve succeeded |
| G1 | `turn_count >= 1` (or Operator-set min) |
| G2 | At least one `role=user` turn with non-trivial text |
| G3 | Packet sections non-empty (schema validator) |
| G4 | Marker / directive check: either injected test marker **or** hash of last N user turns written into packet **and** grepped in `CURRENT.md` |
| G5 | `handoff_result.json` written with matching status |

**G6 (wiki) is a nightly-job gate, not a handoff gate.**  
If any handoff gate fails → exit non-zero, **no** SUCCESS banner.

### 4.3b Nightly job gates (wiki + FR + embed + DB)

| Gate | Rule |
|------|------|
| N0 | Session resolved; cwd/root mapped |
| N1 | Flight Recorder produced non-empty cleaned markdown |
| N2 | Wiki page written under correct project root; marker/session-id present |
| N3 | Embed step ran on **cleaned FR** (not raw jsonl by default) |
| N4 | Rows persisted to memory DB; ids recorded in job result |
| N5 | Job result JSON written (`status: ok|partial|error`) |

Blackbox cron has its own result file (sealed count / failures); separate from N-gates.

### 4.4 `handoff_result.json` (agent-proof API)

```json
{
  "schema_version": 1,
  "status": "ok",
  "code": "OK",
  "session_id": "...",
  "vessel": "aim-grok",
  "turn_count": 88,
  "paths": {
    "continuity": ".../continuity/CURRENT.md",
    "archive": ".../continuity/history/....md",
    "wiki_page": ".../memory-wiki/pages/source-....md",
    "raw": "..."
  },
  "gates": {"G0": true, "G1": true, "G2": true, "G3": true, "G4": true, "G5": true, "G6": true},
  "errors": []
}
```

**Policy for agents:**  
You may open a ticket about handoff **only if** you attach this JSON and `status != ok` with a real `code`.  
“I think the pipeline is broken” without JSON = invalid ticket.

### 4.5 Memory (wiki) — **not** on handoff critical path

Wiki + embed live in **system B (nightly cron)**. See §0.

Handoff may optionally *hint* paths in the packet (`Evidence` section) but **must not** require wiki SUCCESS to exit 0.

Nightly wiki pipeline (authoritative):

1. Discover sessions since last watermark (per host adapter)  
2. Group by conversation root (cwd)  
3. **Flight Recorder** → cleaned session markdown  
4. Write/update wiki pages for that root (one clean page family per session; no dual rawsum/reincarnate spam)  
5. **Embed** cleaned FR chunks  
6. **Save into the memory database** (Lance / vessel store)  
7. Record job result JSON (same anti-false-green discipline as handoff)

Stage 1 LLM polish remains **optional offline**, never blocks the nightly job’s structural SUCCESS.

### 4.6 Blackbox seal — **nightly cron only** (system C)

Every session gets sealed via **cron**, not via handoff/reincarnate process side effects.

- Input: raw native transcript  
- Output: encrypted object + manifest (`sha256_plaintext`, session_id, sealed_at)  
- Failure: job-level warn/retry; **does not** affect handoff exit codes  
- Handoff does **not** own vault

### 4.7 Spawn / teleport

```bash
./aim handoff --session-id X           # default: packet only
./aim handoff --session-id X --spawn   # after OK, start host CLI with CURRENT.md injected
```

Spawn adapter rules:
- Never kill a session whose name is in `PILLAR_SESSIONS` allowlist (`aim-grok`, `aim-agy`, `aim-opencode`) unless `--force-kill-source`
- Default spawn creates **new** session; source left alone unless `--replace`

This alone would have prevented half the board-room disasters.

### 4.8 When handoff runs (triggers)

| Trigger | Who runs it | Agent involved? |
|---------|-------------|-----------------|
| Operator CLI | Operator | No |
| Precompact / Stop hook | Host hook → `./aim handoff` | No (hook is dumb shell) |
| Context budget critical | Hook or Operator | No |
| Agent “I should reincarnate” | Agent may **propose**; Operator or hook executes | Agent must not invent a new pipeline |

Agents do not own the critical path.

---

## 5. Packet construction strategy (quality without LLM on critical path)

Critical path stays **deterministic**:

1. Take last K user turns + last K assistant turns (K default 30 / 15)  
2. Extract “Do Not Forget” from user turns via simple rules:
   - lines starting with MUST / DO NOT / Operator: / MANDATE
   - fenced “directives” blocks if present
   - explicit `[[KEEP]]` markers Operator can type  
3. “Do Next” from last user question + open `TODO` lines in assistant text (regex)  
4. Commander Summary = first user wake + last user goal sentence (truncate)

Optional **offline** enricher later:

```bash
./aim handoff-enrich --from history/{id}.md
```

Uses LLM to rewrite Summary / Do Next — never on the gate path.

This is the opposite of “hope the agent writes a good gameplan mid-death.”

---

## 6. What we throw away vs keep

### Throw away (from critical path)

| Current piece | Fate |
|---------------|------|
| Multi-format `extract_signal` zoo as shared brain | Replace with per-host adapters |
| session_summarizer dual path | Delete from handoff path |
| Dual wiki page types per reincarnate | One page |
| Gameplan_manager as required gate | Optional read-only input if file exists |
| Fleet peer agents to “keep lockstep” for handoff | Irrelevant to handoff |
| Teleport-by-default | Opt-in |
| SUCCESS without content gates | Banned |

### Keep (ideas, not code)

| Idea | Keep as |
|------|---------|
| Exclusive `--session-id` | Law |
| Operator E2E marker bar | Law (stronger) |
| Nested vessel OS | Layout |
| Blackbox seal concept | Optional sidecar |
| Stage 0 multi-page schema | Simplify to one page + index |
| Flight recorder | Offline viewer of raw, not critical path |

### Do not rewrite the world in one PR

Greenfield **module** under `aim-agy_os/handoff/` with feature flag:

```bash
AIM_HANDOFF_V2=1 ./aim handoff ...
```

Old reincarnate stays until v2 E2E is green on grok+agy+opencode, then flip default and delete old path.

---

## 7. Agent behavior contract (stop the retardation loop)

Ship as short **immutable** section in vessel `AGENTS.md`:

```text
## Handoff (reincarnation) — hard rules
1. Continuity lives in continuity/CURRENT.md only.
2. To hand off: tell Operator to run `./aim handoff --session-id <id>` OR rely on Stop/precompact hook.
3. Never invent a new handoff pipeline. Never open tickets about handoff without attaching continuity/handoff_result.json.
4. On wake: read continuity/CURRENT.md before any other project lore.
5. If CURRENT.md is missing/stale, say so; do not hallucinate a gameplan from memory-wiki fragments.
```

Social/fleet rules (REPLY_TO, four pillars) stay **outside** handoff.  
Handoff works with **zero** other agents online.

---

## 8. Test strategy (prove it can’t false-green)

### Unit
- Adapter: given fixture, exact turn count  
- Packet schema validator  
- Gate matrix (empty → exit 2; good → 0; missing section → 1)

### Operator E2E (one harness, all hosts)

```bash
./aim handoff-e2e --host grok
```

Plant unique marker → handoff → assert:
- exit 0  
- `handoff_result.json.status == ok`  
- marker in `CURRENT.md`  
- marker in wiki page  
- **no** SUCCESS if marker deleted from input (negative test)

Negative tests are what the old system lacked.

### Chaos tests
- Wrong session-id → fail, no mtime steal  
- Truncated jsonl → fail loud  
- Double-run handoff → history grows, CURRENT replaced atomically  

---

## 9. Implementation phases

### Phase 0 — Spec freeze (1 short doc)
- Continuity Packet schema v1  
- `handoff_result.json` codes  
- Gate table  
- Agent hard rules  

### Phase 1 — Core + Grok adapter (flagship)
- `handoff/` package  
- Grok adapter from known `updates.jsonl`  
- `./aim handoff`  
- E2E + negative tests on aim-grok  
- Feature flag  

### Phase 2 — AGY + OpenCode adapters
- Same core, new adapters only  
- Same E2E harness parameterized by host  

### Phase 3 — Hooks
- Grok Stop / precompact → `./aim handoff` (no agent)  
- AGY AfterAgent / OC session.idle optional auto-handoff (debounced, Operator opt-in)

### Phase 4 — Spawn
- `--spawn` with pillar protect  
- Delete old teleport-as-default behavior  

### Phase 5 — Cutover
- Default v2  
- Delete old pulse/summarizer dual path from critical path  
- Archive old modules  

### Phase 6 — Codex (when available)
- One adapter file only  

**Soul-first:** implement core on aim-agy; adapters can start on grok if grok remains orchestrator — but **one package name, one schema**, port same week.

---

## 10. Success criteria (Operator-facing)

### Handoff
1. Kill a long session → `./aim handoff` → new session continues from **`continuity/CURRENT.md` alone**.  
2. Empty or wrong-session handoff **cannot** print SUCCESS.  
3. Agents stop filing “pipeline broken” tickets without `handoff_result.json`.  
4. **No agent spin-up** required for a correct handoff.

### Nightly wiki + FR + DB
5. Cron runs without any agent online.  
6. Sessions are cleaned via **Flight Recorder** before any embed.  
7. Embeddings / DB rows come from **cleaned FR**, not raw tool soup.  
8. Wiki pages land under the **correct conversation root** only.  
9. Job result JSON proves N-gates (no fake SUCCESS).

### Blackbox cron
10. Every session sealed on a schedule; vault failures do not block handoff or wiki jobs.

### Host growth
11. Adding a host = one adapter + fixtures, not a fleet project.

---

## 11. Explicit non-goals (this redesign)

- Multi-agent reincarnation ceremonies / spin-up-as-default  
- Wiki or vault on the handoff critical path  
- Perfect LLM-written gameplans on the critical path  
- Embedding raw jsonl by default  
- Byte-identical engines across vessels  
- Fixing codex quota / live codex  
- Preserving every historical wiki page type  

---

## 12. Recommendation

**Three systems:**

1. **Handoff Core** — Continuity Packet + dumb adapters + content gates (live).  
2. **Nightly wiki pipeline** — Flight Recorder clean → wiki by cwd root → embed → **database**.  
3. **Nightly blackbox** — seal every session raw.

Kill agent-operated pipelines and multi-writer daemons.

> **Durable continuity for the next mind — plus durable memory and forensics on a schedule — not a fragile Rube Goldberg that only works when every agent is clever.**

---

## 13. Open decisions for Operator (before code)

1. **Command name:** keep `./aim reincarnate` as alias, or rename to `./aim handoff` as primary?  
2. **Auto-handoff on Stop/precompact:** default on or opt-in? (Recommend **opt-in** until E2E green.)  
3. **Wiki / vault on handoff path:** **No** — confirmed Operator direction (cron only).  
4. **Cutover style:** feature flag side-by-side (recommended) vs big-bang delete.  
5. **Cron schedule / watermark store:** e.g. daily 02:00 local; state in `~/.aim/cron/` or vessel `continuity/cron_state.json`.  
6. **FR mode for embed default:** `cleaned` (recommended) vs `hybrid`.

Default recommendations are in parentheses if you want zero debate and just build.
