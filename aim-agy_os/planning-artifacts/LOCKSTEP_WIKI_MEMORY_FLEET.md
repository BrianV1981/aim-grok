# Fleet lockstep: memory-wiki (aim-agy · aim-grok · aim-opencode)

**Status:** Action B **DONE** on GitHub (2026-07-15) — pre-schema lockstep  
**Soul tip:** `5b18bcf` · **Grok:** `1a947d5` · **OpenCode:** `fa2a7cd`  
**Why this exists:** Operator concern — wiki/memory work is in flight; vessels already drift; we must not make Grok-only changes that orphan AGY/OpenCode.

**Related:** `PLAN_LLM_WIKI_AIM_GROK.md` (vision + phases)

---

## 0. Calm the scope

| Claim | Reality |
|-------|---------|
| “We overhauled the wiki agent schema” | **Not yet.** Full LLM Wiki schema is still a **plan**. |
| “We changed the pipeline” | **Yes** — #10 work: no silent CONFIG fail, session ids, deterministic default, daemon logging. |
| “Vessels are identical” | **No** — critical drift already (see §1). |
| “We can fix Grok in isolation” | **No** for shared engine files. Schema + init seeds + `wiki_compiler` / `session_summarizer` / default `wiki_tools` behavior = **soul-first**. |

**Lock rule:** Any change that touches **how wiki AGENTS is seeded or how ingest runs** lands on **aim-agy main first**, then surgical pin-sync to grok + opencode in the **same calendar day**.

---

## 1. Empirical drift (2026-07-15)

| Module | aim-agy | aim-grok | aim-opencode | Notes |
|--------|---------|----------|--------------|--------|
| `hooks/session_summarizer.py` | **same hash** | **same hash** | **different** | AGY↔Grok lockstep on #10 path; OC behind/forked |
| `memory-wiki/AGENTS.md` | thin maintainer (same) | thin maintainer (same) | **MISSING** | Init seeds differ (AGENTS vs AGENT.md) |
| `.aim_core/wiki_compiler.py` | present | present (identical) | **MISSING** | OC cannot run Stage 0 deterministic without port |
| `.aim_core/wiki_tools.py` | deterministic default + agent mode | **older agent-only style** (different) | opencode spawn, agent-only | **High risk** |
| `.aim_core/handoff_pulse_generator.py` | AGY-native | Grok vessel_paths | OC paths | **Expected overlay** — keep vessel-specific |
| `.aim_core/aim_init.py` | `T_WIKI_AGENT` swarm string | similar | larger fork; `AGENT.md` | **Must unify schema seed** |

**Takeaway:** We are already mid-drift. Freezing *process* matters more than freezing *fear*.

---

## 2. What is SHARED vs OVERLAY

### SHARED (soul-owned — implement on aim-agy first)

These must not diverge without intentional pin-sync:

1. **Wiki schema content** — eventual `memory-wiki/AGENTS.md` / packaged template  
2. **Schema seed path** — `aim_init` + `ensure_wiki_scaffold` (copy template, Schema-Version)  
3. **`wiki_compiler.py`** — Stage 0 deterministic ingest  
4. **`session_summarizer.py`** core flow — CONFIG loud fail, deterministic reincarnate, daemon log (vessel jsonl discovery may call vessel helpers)  
5. **Default wiki process mode** — `AIM_WIKI_MODE` default deterministic; agent optional  
6. **Paste pointer text** — “read AGENTS.md first; one file” (spawn binary is overlay)

### OVERLAY (vessel-owned — never rsync-clobber)

| Vessel | Overlay |
|--------|---------|
| aim-grok | `vessel_paths.py` (updates.jsonl), Grok spawn binary, `~/.grok/sessions` |
| aim-agy | `agy_workspace_trust.py`, AGY brain transcript discovery, agy spawn |
| aim-opencode | `session_bridge.py`, opencode spawn, OC storage paths, legacy flat paths |

---

## 3. Lockstep process (how we stay aligned)

### 3a. Single ticket, three remotes

When schema/pipeline ships:

| Remote | Ticket purpose |
|--------|----------------|
| **aim-agy** | Soul implementation + merge to main |
| **aim-grok** | Port/pin + Grok overlay verification + SOURCE pin |
| **aim-opencode** | Port/pin + OC overlay verification + SOURCE pin |

Same title prefix: `wiki-schema-v2` or `LLM Wiki Stage 0/1 lockstep`.

### 3b. Order of operations (non-negotiable)

```text
1. Write schema once on aim-agy (template file under aim-agy_os/)
2. Wire aim_init + ensure_wiki_scaffold on aim-agy
3. Align wiki_tools default (deterministic) on aim-agy if not already
4. Merge aim-agy main → record SHA
5. SAME DAY: pin-sync to aim-grok + aim-opencode:
     - copy shared modules + template
     - preserve vessel overlays
     - bump SOURCE.md
     - ./aim doctor + wiki smoke per vessel
6. vessel_core_diff.py --report-only → document remaining intentional drift
7. Close sibling tickets with SHAs
```

### 3c. Forbidden

- Schema only on aim-grok live wiki without init/scaffold update  
- `rsync --delete` of entire `aim-agy_os` (clobbers overlays)  
- Different `T_WIKI_AGENT` strings on three vessels  
- OpenCode left without `wiki_compiler` / wiki AGENTS after soul ships schema  

### 3d. Day-of checklist (print and tick)

```text
[ ] Soul PR merged; SHA = ________
[ ] Template path exists: aim-agy_os/.../memory_wiki_AGENTS.md (or agreed path)
[ ] aim_init seeds that template
[ ] ensure_wiki_scaffold seeds that template if missing
[ ] Grok: shared files synced; vessel_paths untouched unless intentional
[ ] OpenCode: wiki_compiler present; memory-wiki/AGENTS.md present; spawn stays opencode
[ ] Fresh tmp init on each vessel shows Schema-Version line
[ ] vessel_core_diff report attached to PR/issue
[ ] SOURCE.md pins updated on grok + opencode
```

---

## 4. Immediate “get locked in” actions (this week)

### Action A — Freeze policy (now)

- No further one-off wiki hacks on a single vessel without soul PR.  
- Plan file + this lockstep file are the contract.

### Action B — Pre-schema alignment PR (small, calming)

**Goal:** Make vessels *safe to evolve together* before big schema rewrite.

1. **Soul (aim-agy):** ensure `wiki_tools` default deterministic is canonical (already is).  
2. **Grok:** port AGY `wiki_tools.py` structure (deterministic default + `AIM_WIKI_MODE=agent`) while spawn uses Grok/agy overlay flag — *or* document intentional older agent path until PR-A.  
3. **OpenCode:** port `wiki_compiler.py` from soul; ensure session_summarizer loud CONFIG matches soul; create missing `memory-wiki/AGENTS.md` from current thin template as interim (same hash as agy/grok).  
4. Pin SOURCE on grok/opencode to soul tip.

This is **lockstep hygiene**, not yet full LLM Wiki schema.

### Action C — Schema PR-A (after B)

- One template, all init/scaffold paths, three vessels same day (per PLAN §1.2).

---

## 5. Pin tracking

| Vessel | SOURCE pin should track | Wiki lockstep note |
|--------|-------------------------|-------------------|
| aim-agy | (is soul) | Authoritative |
| aim-grok | aim-agy main SHA | Update after every wiki shared merge |
| aim-opencode | aim-agy main SHA | Update after every wiki shared merge |

Current Grok pin may lag soul tip — **refresh as part of Action B**.

---

## 6. Decision for Operator

| Option | Meaning |
|--------|---------|
| **B then A** (recommended) | First equalize compiler/tools/AGENTS presence across 3 vessels; then schema rewrite with install lockstep |
| **A only** | Schema + init on Grok first — **rejected by Operator concern**; do not do |
| **Soul-only A then same-day ports** | Skip B if we accept current drift until schema day — riskier |

**Recommendation:** Execute **Action B (pre-schema lockstep)** next, then **PR-A schema** on soul with same-day triple pin.

---

## 7. One sentence

**We stay locked by treating wiki schema + seeds + Stage-0 compiler as soul property, pin-syncing all three vessels the same day, and never changing only Grok’s living AGENTS.md without the install/init factory that creates it.**
