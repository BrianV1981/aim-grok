# Summary: Source material: aim-agy_os/planning-artifacts/PLAN_LLM_WIKI_AIM_GROK.md

*Stage 0 multi-page integrate · source_id=`golden-wiki-schema-v2` · file=`aim-agy_os/archive/history/2026-07-15_golden_wiki-schema-v2.md` · 2026-07-16*

# Summary: Source material: aim-agy_os/planning-artifacts/PLAN_LLM_WIKI_AIM_GROK.md

Source: `2026-07-15_golden_wiki-schema-v2.md`

## USER
Ingest curated source: aim-agy_os/planning-artifacts/PLAN_LLM_WIKI_AIM_GROK.md
## MODEL
Acknowledged. Filing structural wiki knowledge.
# Source material: aim-agy_os/planning-artifacts/PLAN_LLM_WIKI_AIM_GROK.md
# Plan: Realize the LLM Wiki on aim-grok (then mirror to fleet)
**Status:** Phase 0–1 / PR-A **SHIPPED** on fleet (Schema-Version 2) — 2026-07-15  
**Vessel:** aim-grok pilot **with fleet lockstep** (see `LOCKSTEP_WIKI_MEMORY_FLEET.md`)  
**Goal:** Make `memory-wiki/` a **persistent, compounding, interlinked knowledge base** maintained under a real **schema**, not extractive session dumps or flaky one-line agent pastes.
**North star:** Operator’s LLM Wiki pattern — raw sources immutable → LLM-owned wiki → schema (`AGENTS.md`) drives ingest / query / lint; knowledge compiled once and kept current.
**Lockstep:** Schema + init/scaffold seeds + `wiki_compiler` + default process mode ship **aim-agy first**, then **same-day** pin-sync to grok + opencode. No Grok-only schema overhaul.
## 0. Success criteria (aim-grok done when…)
| 1 | `memory-wiki/AGENTS.md` is a full **schema** (ingest / query / lint / page types), not a thin loop |
| 4 | Serial queue: **one source at a time**, lock while busy; no concurrent wiki agents |
| 6 | `./aim wiki search` + reading `index.md` can answer a non-trivial project question from wiki alone |
## 1. Current baseline (aim-grok)
| `memory-wiki/` | Exists: AGENTS, index, log, pages, _ingest, _raw_logs |
## 2. Target architecture (Grok-specific)
  sources/                   # Operator-dropped markdown/pdf notes
memory-wiki/                 # LLM-owned (or Stage0+LLM hybrid)
~/.grok/sessions/...         # durable CLI truth (read-only for wiki pipeline)
2. **Query** — answer from wiki; optionally file answer as a new page  
## 3. Phased plan
### Phase 0 — Freeze & measure (½ day)
1. Snapshot current wiki:  
   `cp -a aim-agy_os/memory-wiki aim-agy_os/memory-wiki.bak.$(date +%Y%m%d)`  
3. Write `memory-wiki/BASELINE.md` with 3 sample queries and whether wiki alone answers them (probably no).  
### Phase 1 — Schema as the product (1 day)
**Intent:** Make `AGENTS.md` the real “schema” document from the LLM Wiki essay, specialized for A.I.M. @ Grok.
#### 1.1 Rewrite `memory-wiki/AGENTS.md`
2. **Layers** — raw vs wiki vs schema (paths above)  
   - `synthesis-*` (comparisons, open questions, “current mental model”)  
   - Extract: decisions, architecture changes, failures, APIs, open questions, Operator intent  
   - Stop (do not pull next file unless Operator says batch)  
7. **Sandbox** — only `memory-wiki/` writes; never mutate `~/.grok/sessions` or engine code  
#### 1.2 HARD REQUIREMENT: single source of truth for schema creation
**If we alter `memory-wiki/AGENTS.md`, every install/init path that creates it MUST be updated in the same PR.**  
Otherwise greenfield installs (and headless co-agents) keep shipping the thin `T_WIKI_AGENT` swarm blurb and the vision dies on first `aim init`.
##### Canonical source (do not duplicate prose)
| `aim-agy_os/memory-wiki/AGENTS.md` | **Runtime schema** used by wiki agent cwd |
| `aim-agy_os/.aim_core/wiki_schema/` or `.../templates/memory_wiki_AGENTS.md` | **Optional** template file copied by init/scaffold (preferred over giant string in `aim_init.py`) |
Prefer: **one markdown file on disk** that init/scaffold **copies** when missing (or when `Schema-Version` is older than packaged). Avoid maintaining the full schema only as `T_WIKI_AGENT = """..."""` in Python.
##### Creation / seed sites that MUST be wired (aim-grok now; soul + OC when mirroring)
| `aim_init.py` → `files["…/memory-wiki/AGENTS.md"] = T_WIKI_AGENT` | Thin swarm node template | Write **new schema** (from template file or updated constant) |
| `wiki_compiler.ensure_wiki_scaffold()` | Creates dirs + empty index/log only — **does not write AGENTS.md** | If `AGENTS.md` missing (or schema version stale), **install canonical schema** |
| `session_summarizer` / reincarnate path | Calls `ensure_wiki_scaffold` | Inherits scaffold fix automatically |
| `./aim wiki bootstrap` | Via wiki_compiler | Must leave a real schema on disk |
| Install scripts (`install-clean` / `install-agent` / `install-core`) | Copy engine tree; init creates wiki AGENTS | No separate AGENTS body — but **must not strip** template path; headless init must run schema seed |
| OpenCode / other vessel inits (later) | May omit wiki AGENTS entirely | Same template copy rule |
##### Upgrade policy for existing vessels
| No `memory-wiki/AGENTS.md` | Create full schema |
| Present but no `Schema-Version:` / version &lt; packaged | **Offer** `aim wiki schema-upgrade` or init flag `--upgrade-wiki-schema` (do not silent overwrite Operator-edited schema without flag) |
##### Verification (PR-A acceptance)
- [ ] Fresh tmp headless/init → `memory-wiki/AGENTS.md` contains new schema (multi-page ingest language, Schema-Version)  
- [ ] Delete AGENTS.md → `ensure_wiki_scaffold` / wiki process restores it  
- [ ] `T_WIKI_AGENT` (if still present) **identical** to packaged schema or removed in favor of file copy  
- [ ] Grep for other `T_WIKI` / wiki AGENTS seed strings — zero stale thin templates left  
#### 1.3 Paste prompt becomes a pointer (not the whole job)
Read memory-wiki/AGENTS.md (schema) and memory-wiki/index.md first.
### Phase 2 — Two-stage pipeline (code) (1–2 days)
  (filters noise, preserves USER/MODEL signal, caps size)
  AIM_WIKI_MODE=agent → spawn Grok-aware agent in memory-wiki/
#### 2.1 Stage 0 improvements (`wiki_compiler` / summarizer)
- Stronger **exclude** filters: system-reminder blocks, skill lists, huge tool dumps  
- Preserve Operator markers and decision language  
- Output to `_ingest/` with YAML frontmatter:  
- Never claim SUCCESS if Stage 0 produces empty/noise-only content (already partially gated)
#### 2.2 Stage 1 agent spawn (Grok-native)
Today wiki agent often spawns **`agy`**. For aim-grok:
- Prefer `grok` (or documented vessel CLI) with cwd = `memory-wiki/`  
- Ensure project context discovers `AGENTS.md` in that directory  
- Single-flight lock: if wiki tmux session exists → refuse new spawn  
- Optional: `scripts/wiki_ingest_one.sh` Operator entrypoint  
#### 2.3 CLI surface
./aim wiki process              # Stage 0 only if _raw present; else Stage 1 if agent mode
./aim wiki process --stage0     # force deterministic only
./aim wiki process --agent      # force LLM maintainer (one file)
./aim wiki lint                 # new: schema-driven lint prompt or deterministic checks + agent
./aim wiki query "..."          # optional thin wrapper: search + suggest file-back
**Exit:** One golden source through Stage 0 → Stage 1 → multi-page wiki; daemon/log proves it.
### Phase 3 — Golden path proof on Grok (½–1 day)
1. Pick **1–2** real Grok sessions from `~/.grok/sessions/%2Fhome%2Fkingb%2Faim-grok/` (this orchestration session + #10 work is ideal).  
3. Run Stage 0 → review `_ingest/` with Operator.  
4. Run Stage 1 agent; Operator watches Obsidian/wiki tree.  
   - [ ] reincarnated agent could find “what is issue #10?” from wiki alone  
**Exit:** Written `memory-wiki/GOLDEN_RUN.md` with before/after notes. **Do not scale until this passes.**
### Phase 4 — Serial backfill driver (Grok only) (1 day + runtime)
#### 4.1 Queue file
## USER
Ingest curated source: aim-agy_os/planning-artifacts/LOCKSTEP_WIKI_MEMORY_FLEET.md
## MODEL
Acknowledged. Filing structural wiki knowledge.
# Source material: aim-agy_os/planning-artifacts/LOCKSTEP_WIKI_MEMORY_FLEET.md
# Fleet lockstep: memory-wiki (aim-agy · aim-grok · aim-opencode)
**Status:** Action B **DONE** on GitHub (2026-07-15) — pre-schema lockstep  
**Why this exists:** Operator concern — wiki/memory work is in flight; vessels already drift; we must not make Grok-only changes that orphan AGY/OpenCode.
**Related:** `PLAN_LLM_WIKI_AIM_GROK.md` (vision + phases)

*(truncated for wiki)*


---
[← Wiki index](../index.md)
