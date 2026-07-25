# Handoff (reincarnation) — opt-in wiki policy

**Status:** Operator-ratified product law (2026-07-24)  
**Supersedes (as default product behavior):** nightly “vacuum” wiki batch of every session by cwd (Handoff vNext system B as originally sketched in epic #32 / #116)

---

## 1. Why handoff exists (original design)

From `aim-agy_os/aim-agy_os_docs/REINCARNATE_PROTOCOL.md` and `PERSISTENT_WIKI.md`:

1. **Context dies** — long agents hit window limits / amnesia / API errors.  
2. **Continuity** — gameplan / pulse / wake so a *new* mind continues work.  
3. **Long-term memory** — on **that same deliberate fire**, archive + distill + weave into **memory-wiki** + embed.  
4. **Not ambient** — the conscious agent does not casually edit the wiki; the **reincarnate/handoff trigger** starts the subconscious scribe path.

From `docs/GOAL_REINCARNATION_MEMORY_WIKI.md`:

> After a real session with Operator directives, **reincarnation (pulse/handoff)** must leave those directives findable in memory-wiki — without false SUCCESS.

The original bar is **Operator-chosen session → handoff → wiki**, not “every chat folder scrape.”

---

## 2. The fine line (Operator memory dump)

| Session type | Intent | Wiki / lore? |
|--------------|--------|----------------|
| Scratch / “use agent in this project folder” | Temporary help; agent may read project | **No** ingest |
| Campaign / decisions you care about | Continuity + project memory | **Yes — only if handoff is run** |

**Typing handoff (historically `/reincarnate`) is the Operator’s vote:**  
“This session is part of the project’s memory.”

That is why the process is **triggered**, not a nightly vacuum of every conversation.

---

## 3. Naming

| Prefer | Avoid as primary product name |
|--------|-------------------------------|
| **Handoff** | “Reincarnation” as the only word (confuses agents and Operators) |

Legacy CLI `./aim reincarnate` may remain as alias until cutover. Docs and new work use **handoff**.

---

## 4. Rejected default: wiki vacuum

**Rejected as default product behavior:**

- Nightly cron that discovers **all** sessions under a cwd and ingests them into memory-wiki / embed DB.  
- Treating “session happened in this project folder” as “must enter wiki.”

**Why rejected:** pollutes lore, mixes scratch with campaign, fights the original opt-in design, and was only a temporary overhaul sketch.

### What may still run nightly (separate jobs)

| Job | Allowed? | Notes |
|-----|----------|--------|
| Blackbox seal of raw sessions | Optional forensic | **Not** wiki law |
| Maintenance / watermark hygiene | Optional | Must not invent wiki pages for non-handoff sessions |
| Wiki batch of **handoff-marked** sessions only | OK | Queue = sessions that already completed handoff |

---

## 5. Canonical pipeline (product law)

### On explicit handoff (Operator / CLI / optional precompact hook)

1. Resolve **exclusive** `--session-id` (no mtime steal).  
2. Extract signal / flight-record clean as needed.  
3. Write **continuity packet** (gameplan / `CURRENT.md` / result JSON) — content-gated.  
4. Archive history for that session.  
5. **Wiki + embed path only for this session** (scribe / Stage 0 / FR→wiki→DB as implemented).  
6. Spawn successor CLI matching **this vessel** (Grok→`grok --always-approve`, never AGY for Grok-family).  
7. Optional teleport UX.

### Not on handoff

- Other sessions in the same folder.  
- Nightly bulk wiki invent.

---

## 6. Implications for existing code & tests

Fleet work under Handoff vNext **ports** (agy#117, opencode#34, grok handoff package) included:

- Nightly `wiki-batch` / `cron-all` that processes sessions since watermark  
- Multi-day soak that plants sessions and expects wiki for each day  

Under **this** policy those paths must be **re-scoped or demoted**:

| Component | Required change |
|-----------|-----------------|
| Nightly wiki cron | **Off by default** or only process handoff queue |
| e2e “every staged session → wiki” | Rewrite: only handoff-marked sessions |
| Docs / epics #32 #116 | Amend title/body: reject vacuum |
| Crontabs on host | Remove or disable vessel `cron-all` wiki half until retested |

**All relevant E2E must be re-run** after the code matches this law.

---

## 7. Related fleet docs

| Doc | Role |
|-----|------|
| `aim-agy_os/aim-agy_os_docs/REINCARNATE_PROTOCOL.md` | Original 5-phase pipeline (trigger-based) |
| `aim-agy_os/aim-agy_os_docs/PERSISTENT_WIKI.md` | Wiki write on reincarnate trigger |
| `aim-agy_os/aim-agy_os_docs/GAMEPLAN_SOP.md` | Continuity before handoff |
| `docs/GOAL_REINCARNATION_MEMORY_WIKI.md` | Operator acceptance bar |
| `docs/PLAN_HANDOFF_VNEXT_REINCARNATION.md` | Overhaul history (includes rejected vacuum sketch) |
| `docs/FOUR_PILLARS_ALIGNMENT.md` | Install/update + short opt-in note |

---

## 8. One-sentence north star

**Handoff is the Operator’s intentional commit of a session into continuity and project memory; the wiki is not a vacuum cleaner for every chat that happened to share a folder.**
