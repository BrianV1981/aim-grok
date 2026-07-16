# Plan: Realize the LLM Wiki on aim-grok (then mirror to fleet)

**Status:** Phase 0–1 / PR-A **SHIPPED** on fleet (Schema-Version 2) — 2026-07-15  
**Vessel:** aim-grok pilot **with fleet lockstep** (see `LOCKSTEP_WIKI_MEMORY_FLEET.md`)  
**Date:** 2026-07-15  
**Soul SHA (schema):** `0e7a77b` · Grok `ef5b5e9` · OpenCode `6414a7f`  
**Goal:** Make `memory-wiki/` a **persistent, compounding, interlinked knowledge base** maintained under a real **schema**, not extractive session dumps or flaky one-line agent pastes.

**North star:** Operator’s LLM Wiki pattern — raw sources immutable → LLM-owned wiki → schema (`AGENTS.md`) drives ingest / query / lint; knowledge compiled once and kept current.

**Lockstep:** Schema + init/scaffold seeds + `wiki_compiler` + default process mode ship **aim-agy first**, then **same-day** pin-sync to grok + opencode. No Grok-only schema overhaul.

---

## 0. Success criteria (aim-grok done when…)

| # | Criterion |
|---|-----------|
| 1 | `memory-wiki/AGENTS.md` is a full **schema** (ingest / query / lint / page types), not a thin loop |
| 2 | Agent-mode ingest **must** load schema first; paste prompt is a thin pointer to schema + one file |
| 3 | One curated **golden** Grok session produces **multi-page** graph updates (entity/concept/source + index + log), not a single `reincarnate-*.md` blob |
| 4 | Serial queue: **one source at a time**, lock while busy; no concurrent wiki agents |
| 5 | Deterministic compiler is **Stage 0 only** (clean staging), not the final product |
| 6 | `./aim wiki search` + reading `index.md` can answer a non-trivial project question from wiki alone |
| 7 | Lint pass exists (orphan pages, missing concepts, contradictions flagged) |
| 8 | Documented runbook so the same plan can be mirrored to AGY/OpenCode without copying Grok paths |

**Out of scope for v1 on Grok:** full Obsidian plugin suite, embedding re-architecture, mass AGY backfill, auto-web clipper.

---

## 1. Current baseline (aim-grok)

| Asset | State |
|-------|--------|
| `memory-wiki/` | Exists: AGENTS, index, log, pages, _ingest, _raw_logs |
| History load | **Light** (~10 archives, few Grok session UUIDs under `~/.grok/sessions/%2Fhome%2Fkingb%2Faim-grok/`) |
| Default pipeline | Deterministic extractive pages (reliable, shallow) |
| Agent pipeline | Optional, paste-weak; often assumes `agy` spawn not Grok |
| Schema | Thin maintainer loop; **not** the driver of default path |

Grok is the right **first** vessel: small history, less garbage, fast feedback.

---

## 2. Target architecture (Grok-specific)

```text
raw/                         # optional curated sources (immutable)
  sources/                   # Operator-dropped markdown/pdf notes
  sessions/                  # pointers or copies of approved session archives
                             # (never mutate ~/.grok/sessions originals)

memory-wiki/                 # LLM-owned (or Stage0+LLM hybrid)
  AGENTS.md                  # SCHEMA (source of truth for maintainer behavior)
  index.md                   # content catalog
  log.md                     # append-only timeline
  pages/                     # entity / concept / decision / source / synthesis
  _ingest/                   # single-item work queue (ideally 0–1 files)
  _raw_logs/                 # transient staging only
  _queue/                    # optional: ordered list of pending session IDs

aim-agy_os/archive/history/  # pulse archives (immutable after write)
~/.grok/sessions/...         # durable CLI truth (read-only for wiki pipeline)
```

**Three operations (must match schema):**

1. **Ingest** — one source → integrate into many pages  
2. **Query** — answer from wiki; optionally file answer as a new page  
3. **Lint** — health check; open questions; orphans  

---

## 3. Phased plan

### Phase 0 — Freeze & measure (½ day)

**Intent:** Know what “bad” looks like before changing behavior.

1. Snapshot current wiki:  
   `cp -a aim-agy_os/memory-wiki aim-agy_os/memory-wiki.bak.$(date +%Y%m%d)`  
2. Inventory:  
   - count pages, orphans (no inbound links), average size  
   - list Grok session dirs + archive/*.md ordered by mtime  
3. Write `memory-wiki/BASELINE.md` with 3 sample queries and whether wiki alone answers them (probably no).  
4. Do **not** mass-ingest yet.

**Exit:** Baseline numbers + session/archive ordered list for Grok only.

---

### Phase 1 — Schema as the product (1 day)

**Intent:** Make `AGENTS.md` the real “schema” document from the LLM Wiki essay, specialized for A.I.M. @ Grok.

#### 1.1 Rewrite `memory-wiki/AGENTS.md`

Sections (required):

1. **Purpose** — compounding project lore for aim-grok / fleet work; not chat log  
2. **Layers** — raw vs wiki vs schema (paths above)  
3. **Page types** (A.I.M.-specific):  
   - `entity-*` (vessels, tools, people)  
   - `concept-*` (GitOps, reincarnation, Engram, lockstep)  
   - `decision-*` (ADR-style: context, choice, consequences)  
   - `source-*` (one page per ingested session/archive with link to archive path)  
   - `synthesis-*` (comparisons, open questions, “current mental model”)  
4. **Ingest workflow** (crystal clear steps; multi-page):  
   - Read schema + `index.md`  
   - Process **exactly one** file from `_ingest/`  
   - Extract: decisions, architecture changes, failures, APIs, open questions, Operator intent  
   - **Ignore:** skill dumps, system-reminders, tool noise, YOLO thrash  
   - Update/create **all** affected pages (target 5–15 touches for a rich source)  
   - Update `index.md` (catalog blurb)  
   - Append **one** `log.md` line with prefix:  
     `## [YYYY-MM-DD HH:MM] ingest | <title> | <source-id>`  
   - Delete only that one ingest file  
   - Stop (do not pull next file unless Operator says batch)  
5. **Query workflow** — search index → pages → answer with citations; offer to file answer as `synthesis-*`  
6. **Lint workflow** — contradictions, orphans, missing entity pages, stale claims  
7. **Sandbox** — only `memory-wiki/` writes; never mutate `~/.grok/sessions` or engine code  
8. **Quality bar** — “Would this help a reincarnated agent tomorrow?”  

#### 1.2 HARD REQUIREMENT: single source of truth for schema creation

**If we alter `memory-wiki/AGENTS.md`, every install/init path that creates it MUST be updated in the same PR.**  
Otherwise greenfield installs (and headless co-agents) keep shipping the thin `T_WIKI_AGENT` swarm blurb and the vision dies on first `aim init`.

##### Canonical source (do not duplicate prose)

| Path | Role |
|------|------|
| `aim-agy_os/memory-wiki/AGENTS.md` | **Runtime schema** used by wiki agent cwd |
| `aim-agy_os/.aim_core/wiki_schema/` or `.../templates/memory_wiki_AGENTS.md` | **Optional** template file copied by init/scaffold (preferred over giant string in `aim_init.py`) |

Prefer: **one markdown file on disk** that init/scaffold **copies** when missing (or when `Schema-Version` is older than packaged). Avoid maintaining the full schema only as `T_WIKI_AGENT = """..."""` in Python.

##### Creation / seed sites that MUST be wired (aim-grok now; soul + OC when mirroring)

| Site | Today | Required change |
|------|--------|-----------------|
| `aim_init.py` → `files["…/memory-wiki/AGENTS.md"] = T_WIKI_AGENT` | Thin swarm node template | Write **new schema** (from template file or updated constant) |
| `wiki_compiler.ensure_wiki_scaffold()` | Creates dirs + empty index/log only — **does not write AGENTS.md** | If `AGENTS.md` missing (or schema version stale), **install canonical schema** |
| `session_summarizer` / reincarnate path | Calls `ensure_wiki_scaffold` | Inherits scaffold fix automatically |
| `./aim wiki bootstrap` | Via wiki_compiler | Must leave a real schema on disk |
| Install scripts (`install-clean` / `install-agent` / `install-core`) | Copy engine tree; init creates wiki AGENTS | No separate AGENTS body — but **must not strip** template path; headless init must run schema seed |
| OpenCode / other vessel inits (later) | May omit wiki AGENTS entirely | Same template copy rule |

##### Upgrade policy for existing vessels

| Case | Behavior |
|------|----------|
| No `memory-wiki/AGENTS.md` | Create full schema |
| Present but no `Schema-Version:` / version &lt; packaged | **Offer** `aim wiki schema-upgrade` or init flag `--upgrade-wiki-schema` (do not silent overwrite Operator-edited schema without flag) |
| Present with equal/newer version | Leave alone |

##### Verification (PR-A acceptance)

- [ ] Fresh tmp headless/init → `memory-wiki/AGENTS.md` contains new schema (multi-page ingest language, Schema-Version)  
- [ ] Delete AGENTS.md → `ensure_wiki_scaffold` / wiki process restores it  
- [ ] `T_WIKI_AGENT` (if still present) **identical** to packaged schema or removed in favor of file copy  
- [ ] Grep for other `T_WIKI` / wiki AGENTS seed strings — zero stale thin templates left  

#### 1.3 Paste prompt becomes a pointer (not the whole job)

Replace long/short weak pastes with something like:

```text
Read memory-wiki/AGENTS.md (schema) and memory-wiki/index.md first.
Then process exactly ONE file in _ingest/ per the Ingest workflow.
Do not process a second file. When that file is absorbed and deleted, stop.
```

**Exit:** Schema committed; init/scaffold guarantee; paste is ≤5 lines and references schema.

---

### Phase 2 — Two-stage pipeline (code) (1–2 days)

**Intent:** Reliability + quality without forcing LLM for bulk junk.

```text
Stage 0 (deterministic, always):
  session/archive → cleaned markdown into _ingest/source-<id>.md
  (filters noise, preserves USER/MODEL signal, caps size)

Stage 1 (LLM maintainer, quality):
  AIM_WIKI_MODE=agent → spawn Grok-aware agent in memory-wiki/
  loads AGENTS.md → multi-page integrate → stop after one file
```

#### 2.1 Stage 0 improvements (`wiki_compiler` / summarizer)

- Stronger **exclude** filters: system-reminder blocks, skill lists, huge tool dumps  
- Preserve Operator markers and decision language  
- Output to `_ingest/` with YAML frontmatter:  
  `source_id`, `source_path`, `session_id`, `ingested_at`, `stage: 0`  
- Never claim SUCCESS if Stage 0 produces empty/noise-only content (already partially gated)

#### 2.2 Stage 1 agent spawn (Grok-native)

Today wiki agent often spawns **`agy`**. For aim-grok:

- Prefer `grok` (or documented vessel CLI) with cwd = `memory-wiki/`  
- Ensure project context discovers `AGENTS.md` in that directory  
- Single-flight lock: if wiki tmux session exists → refuse new spawn  
- Optional: `scripts/wiki_ingest_one.sh` Operator entrypoint  

#### 2.3 CLI surface

```text
./aim wiki process              # Stage 0 only if _raw present; else Stage 1 if agent mode
./aim wiki process --stage0     # force deterministic only
./aim wiki process --agent      # force LLM maintainer (one file)
./aim wiki lint                 # new: schema-driven lint prompt or deterministic checks + agent
./aim wiki query "..."          # optional thin wrapper: search + suggest file-back
```

**Exit:** One golden source through Stage 0 → Stage 1 → multi-page wiki; daemon/log proves it.

---

### Phase 3 — Golden path proof on Grok (½–1 day)

**Intent:** Prove quality before scale.

1. Pick **1–2** real Grok sessions from `~/.grok/sessions/%2Fhome%2Fkingb%2Faim-grok/` (this orchestration session + #10 work is ideal).  
2. Prefer `updates.jsonl` when present (already in vessel_paths).  
3. Run Stage 0 → review `_ingest/` with Operator.  
4. Run Stage 1 agent; Operator watches Obsidian/wiki tree.  
5. Score against checklist:  
   - [ ] source-* page exists  
   - [ ] ≥1 decision-* or concept-* updated  
   - [ ] index blurb accurate  
   - [ ] log line parseable  
   - [ ] reincarnated agent could find “what is issue #10?” from wiki alone  

**Exit:** Written `memory-wiki/GOLDEN_RUN.md` with before/after notes. **Do not scale until this passes.**

---

### Phase 4 — Serial backfill driver (Grok only) (1 day + runtime)

**Intent:** Methodical, one-at-a-time, no concurrent firehose.

#### 4.1 Queue file

`memory-wiki/_queue/pending.tsv` (or yaml):

```text
# priority  session_id  note
1  019f5a76-...  issue-10 orchestration
2  019fbb12-...  seal/reincarnate
```

Built from session dirs + archive list (Grok only — not AGY audit dump yet).

#### 4.2 Driver script `scripts/wiki_serial_ingest.sh`

```text
while queue non-empty:
  if wiki agent session alive: wait
  if _ingest has >0 files: wait for Stage 1 complete (or Operator)
  pop next session_id
  pulse/archive OR Stage0 from updates.jsonl
  if --agent: Stage 1 once
  append queue completed log
  sleep / Operator confirm gate
```

Flags: `--dry-run`, `--stage0-only`, `--stop-after N`, `--require-operator-enter`.

#### 4.3 Human gates

Default for first 5 sessions: **Operator Enter between items**.  
Later: unattended Stage 0 for all, Stage 1 only for VIP rows.

**Exit:** Grok queue empty or paused; wiki measurably richer; no agent pile-up.

---

### Phase 5 — Query + lint loops (½–1 day)

1. **Query:** Document and optionally script:  
   - `./aim wiki search` → agent/schema-aware answer  
   - “File this answer” → new synthesis page  
2. **Lint:** Agent or hybrid:  
   - orphans, missing pages for hub concepts, contradictions  
   - write `memory-wiki/pages/lint-latest.md` + log entry  
3. Run lint after backfill; fix top 5 findings with agent.

**Exit:** One successful lint + one query filed back into wiki.

---

### Phase 6 — Package for fleet mirror (½ day)

Produce a **vessel-agnostic playbook** + **vessel overlay checklist**:

| Shared (soul later) | Grok overlay | AGY overlay | OpenCode overlay |
|---------------------|--------------|-------------|------------------|
| Schema structure | `~/.grok/sessions` discovery | AGY brain transcripts | OC storage paths |
| Stage 0 compiler | already strong | port if missing | port if missing |
| Serial driver | CLI=grok | CLI=agy | CLI=opencode |
| Spawn command | grok | agy + trust | opencode |

**Do not** copy Grok path strings into AGY/OC. Copy **phases, schema shape, serial discipline, Stage0/Stage1 split**.

---

## 4. Implementation order (PRs on aim-grok)

| PR | Scope | Depends |
|----|--------|---------|
| **PR-A** | Schema rewrite + **all** init/scaffold seed paths + paste pointer + upgrade flag | — |
| **PR-B** | Stage 0 filters + frontmatter; Stage 1 Grok spawn + single-flight lock | PR-A |
| **PR-C** | `wiki_serial_ingest.sh` + queue format + dry-run | PR-B |
| **PR-D** | `wiki lint` + query-file-back convention | PR-A |
| **PR-E** | Docs: runbook + fleet mirror checklist | PR-C |

Keep PRs surgical; no `git add .` of skill noise / wiki bak dumps unless intentional.

---

## 5. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Agent ignores schema | Paste forces read AGENTS.md; keep AGENTS short enough to load |
| Stage 1 flaky (trust/boot) | Single-flight lock; wait loops; Operator-visible tmux; Stage 0 always durable |
| Garbage sources pollute wiki | VIP queue; noise filters; “delete if noise” still in schema |
| Deterministic path “feels done” | Golden run requires multi-page Stage 1; measure page graph not just log lines |
| Scope creep to AGY mess | **Grok first**; no AGY mass ingest until mirror playbook exists |

---

## 6. What we deliberately will not do yet

- Ingest all AGY sessions from `session_history_audit.md`  
- Parallel scribes “to go faster”  
- Rely on LanceDB alone without good markdown graph  
- Claim wiki works because bootstrap seeds exist  

---

## 7. Immediate next action (after Operator approval)

1. Approve this plan (or mark edits).  
2. Implement **PR-A only**: full schema + **update every install/init/scaffold writer** of that file (not just the live wiki copy) + paste pointer.  
3. Prove on **fresh tmp install** that new schema appears without hand-copying.  
4. Golden dry-run on **one** Grok session with Operator watching.  
5. Then PR-B/C.

---

## 8. One-sentence mission

**On aim-grok: make the schema real, make ingest multi-page and serial, prove it on one golden session, then scale—and only then copy the *method* (not Grok paths) to AGY and OpenCode.**
