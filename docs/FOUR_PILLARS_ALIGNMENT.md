# Four pillars alignment — install, headless install, update

**Status:** Fleet policy (Operator 2026-07-24)  
**Issues:** [aim-grok#37](https://github.com/BrianV1981/aim-grok/issues/37) · [aim-agy#119](https://github.com/BrianV1981/aim-agy/issues/119) · [aim-opencode#36](https://github.com/BrianV1981/aim-opencode/issues/36) · [aim-codex#17](https://github.com/BrianV1981/aim-codex/issues/17)

This document is the **contract** so all vessel repos stay aligned. Copy or keep in sync across pillars. Vessel-specific URLs/scripts may differ; **laws do not**.

---

## 1. The four pillars

| Pillar repo | Host CLI | Exoskeleton role |
|-------------|----------|------------------|
| **aim-agy** | `agy` (Antigravity) | Soul + **reference** install/update product (most complete today) |
| **aim-grok** | `grok` | Grok vessel OS + Grok install/update/docs |
| **aim-opencode** | `opencode` | OpenCode vessel OS + OC install/update/docs |
| **aim-codex** | `codex` | Codex vessel (live agent may be on hold; **alignment still required**) |

Shared shape: nested **`aim-agy_os/`** engine.  
**Vessel identity** = CLI host + overlays + product surface (README, install, update defaults).

---

## 2. Two channels (do not confuse them)

| Channel | What it is | How it updates |
|---------|------------|----------------|
| **Project / app** | The user’s code (or a client repo). May have its own `origin`, or none after headless install. | Normal `git` for *that* project. **Not** OS update. |
| **A.I.M. OS (vessel)** | Nested OS under `aim-agy_os/` (+ vessel wrapper `./aim`, host hooks/skills layout). | **`./aim update engine`** (or vessel install scripts) from **that vessel’s** published GitHub (or documented dual-channel). |

**Law:** After headless install into someone else’s project, the **project remote can be severed or point elsewhere**. OS update must still work via the **OS/engine URL**, not `git pull` on the project.

---

## 3. Install modes (each vessel must document + ship)

Parity with **aim-agy** product shape (names may match or be prefixed):

| Mode | Intent | aim-agy reference |
|------|--------|-------------------|
| **Clean / OS shell** | Use A.I.M. as the OS for this CLI | `install-clean.sh` |
| **Headless / core into project** | Wrap an existing project; lightweight OS copy | `install-core.sh` |
| **Agent / persona** (optional) | Headless co-agent persona | `install-agent.sh` |

**Each vessel’s scripts must default to cloning/installing from that vessel’s repo**, e.g.:

- AGY → `BrianV1981/aim-agy`
- Grok → `BrianV1981/aim-grok`
- OpenCode → `BrianV1981/aim-opencode`
- Codex → `BrianV1981/aim-codex`

**Not** “everyone curl|bash from aim-agy only.”

---

## 4. Update laws (surgical + vessel-aware)

1. **Default update source = this vessel’s public repo** (or dual-channel: soul shared modules + vessel overlay package — must be explicit).  
2. **Surgical:** only OS tree (`aim-agy_os/` and documented OS files). Never eat app source, `.git` of the project, user docs you didn’t put in the OS package.  
3. **Preserve user data:** `archive/`, `memory/`, `memory_lance/`, `memory-wiki/`, `continuity/`, `planning-artifacts/`, `workspace/`, `venv/`.  
4. **Preserve vessel overlays:** e.g. `VESSEL_HOST`, `teleport_engine.py`, `vessel_paths.py`, host hooks/skills roots, handoff adapters owned by the vessel.  
5. **No silent soul overwrite of vessel identity** — cloning aim-agy into a Grok tree without overlay restore is a **defect**.  
6. **Dry-run** supported (`--dry-run` / `AIM_UPDATE_DRY_RUN`).  
7. **Receipt** written under OS (`ENGINE_UPDATE_RECEIPT.json` or equivalent).

### Known incomplete state (historical)

Early `./aim update engine` on aim-grok defaulted engine URL to **aim-agy** soul while being surgical. That is **not** full four-pillar alignment. Endpoint of this epic: **per-vessel defaults + install parity**.

---

## 5. Runtime identity (spawn / handoff)

Successor agent CLI must match the vessel:

| Vessel | Successor spawn (documented) |
|--------|------------------------------|
| aim-grok / Grok-family | `grok --always-approve --cwd <ws>` — **never** `agy --dangerously-skip-permissions` |
| aim-agy | `agy` with AGY permission flags as documented |
| aim-opencode | `opencode` (vessel spawn contract) |
| aim-codex | `codex` (when enabled) |

Handoff / “reincarnate” naming: prefer **handoff** for clarity.  
**Wiki ingest** is **not** “every session nightly” by default — Operator intent: **opt-in** (handoff / explicit promote). Blackbox backup may differ; wiki is selective.

---

## 6. Alignment maintenance

| Artifact | Purpose |
|----------|---------|
| This file (`docs/FOUR_PILLARS_ALIGNMENT.md`) | Canonical policy |
| `aim-agy_os/planning-artifacts/FOUR_PILLARS_ALIGNMENT.md` | Planning mirror (where used) |
| Sibling GitHub issues | Per-repo implementation tracking |
| README link from each vessel | Onboarding sees the fleet contract |

When changing install/update laws: **update this doc first**, then implement on each vessel, then comment on sibling issues.

---

## 7. Per-vessel checklist

- [ ] README: clean + headless for **this** CLI  
- [ ] Install scripts from **this** vessel GitHub  
- [ ] `./aim update engine` default = **this** vessel (or dual-channel documented)  
- [ ] Update test: no clobber of project/wiki/archive/overlays  
- [ ] This alignment doc present + README link  
- [ ] Spawn/handoff CLI matches vessel (tests)  
- [ ] Sibling issues linked  

---

## 8. Default public URLs (fill as scripts land)

| Vessel | Repo | Install raw base (pattern) | Update default |
|--------|------|----------------------------|----------------|
| aim-agy | https://github.com/BrianV1981/aim-agy | `…/aim-agy/main/aim-agy_os/install-*.sh` | aim-agy |
| aim-grok | https://github.com/BrianV1981/aim-grok | *(to ship)* `…/aim-grok/main/…` | aim-grok |
| aim-opencode | https://github.com/BrianV1981/aim-opencode | *(to ship)* | aim-opencode |
| aim-codex | https://github.com/BrianV1981/aim-codex | *(to ship)* | aim-codex |

---

## 9. Related issues

| Topic | Example |
|-------|---------|
| Grok spawn not AGY | aim-grok#34 |
| Surgical update (first pass) | aim-grok#35 / PR#36 |
| This alignment epic | #37 / agy#119 / oc#36 / codex#17 |
| Handoff vNext | aim-grok#32 family |

---

**North star:** four CLI exoskeletons, one fleet contract, **no cross-wired updates**, project files sacred, OS independently updatable after headless install.
