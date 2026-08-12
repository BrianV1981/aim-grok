# aim-grok — **deprecated**

> **This repository is not maintained.**  
> The Grok CLI vessel is **deprecated in favor of [J.O.S.H.U.A.](https://github.com/BrianV1981/aim-joshua)** — the CLI-agnostic operating system.

Do not clone this repo for new work. Install Joshua, then inject skills from [aim-skill-library](https://github.com/BrianV1981/aim-skill-library) into your Grok host.

```bash
curl -fsSL https://raw.githubusercontent.com/BrianV1981/aim-joshua/main/joshua_os/install.sh | bash

git clone https://github.com/BrianV1981/aim-skill-library.git
cd aim-skill-library
./scripts/install.sh --vessel grok --dest ~/.grok/skills --mode symlink
```

Wiki / onboarding: [aim-joshua/wiki](https://github.com/BrianV1981/aim-joshua/wiki)

---

<!-- AIM_ECOSYSTEM_START -->
### 🧬 The A.I.M. Ecosystem

Modular A.I.M. (Actual Intelligent Memory) repositories. While the original architecture relied on separate CLI harnesses, **J.O.S.H.U.A.** is the convergence point that unifies hosts under a single, agnostic operating system.

**Active (CLI host / OS):**
- **[aim-joshua](https://github.com/BrianV1981/aim-joshua)** — The Universal Operating System. *Use this.*

**Tools & workspaces:**
- **[aim-tmux-dashboard](https://github.com/BrianV1981/aim-tmux-dashboard)** — Terminal multi-session monitor and daily cockpit (CLI alias: `aim-dash`).
- **[aim-connect](https://github.com/BrianV1981/aim-connect)** — Self-hosted remote workspace web UI.
- **[aim-skill-library](https://github.com/BrianV1981/aim-skill-library)** — Skills index / multi-CLI install registry. Home of **`aim-communicate`** and **`aim-audit`**.
- **[aim-browser](https://github.com/BrianV1981/aim-browser)** — Headed Chromium CDP engine + browser skill suite.
- **[aim-google](https://github.com/BrianV1981/aim-google)** — Google Workspace CLI (Gmail, Drive, Calendar, …).
- **[aim-flight-recorder](https://github.com/BrianV1981/aim-flight-recorder)** — Forensic Markdown session extractor.
- **[aim-boardroom](https://github.com/BrianV1981/aim-boardroom)** — Multi-agent orchestration room (OS multiplexing + artifacts).

**DNA, comms & lore:**
- **[aim-coagents](https://github.com/BrianV1981/aim-coagents)** — DNA bank for sovereign co-agent blueprints (including **`aim-auditor`**).
- **[aim-knowledge](https://github.com/BrianV1981/aim-knowledge)** — Public Obsidian vault / deep-lore archive.
- **[aim-chalkboard](https://github.com/BrianV1981/aim-chalkboard)** — Optional cross-host async git mailbox (PoC; default same-host comms = aim-communicate skill).

**Deprecated / not maintained:**
- **aim-agy** — Legacy core engine (Antigravity CLI). Deprecated in favor of aim-joshua.
- **aim-grok** (this repo) — Legacy Grok CLI vessel. Deprecated in favor of aim-joshua.
- **aim-opencode** — Legacy OpenCode CLI vessel. Deprecated in favor of aim-joshua.
- **aim-codex** — Legacy OpenAI Codex CLI vessel. Deprecated in favor of aim-joshua.
- **aim-claude / Anthropic-line vessels** — Done. Operator does not develop against Anthropic.
- **aim-skills** — Replaced by `aim-skill-library`.
- **aim** — Original Gemini CLI framework. Deprecated after loss of practical subscription access.
- **aim-swarm** — Legacy Python swarm factory.
<!-- AIM_ECOSYSTEM_END -->

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[MIT](LICENSE) — Copyright (c) 2026 Brian Vasquez  
☕ **Support:** [Buy Me a Coffee](https://buymeacoffee.com/brianv1981)
