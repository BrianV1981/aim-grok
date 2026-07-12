# Summary: A.I.M. Signal Skeleton

*Ingested from `rawsum_history-part1-raw.md` on 2026-07-12*

# Summary: A.I.M. Signal Skeleton

Source: `history_part1_raw.md`

# A.I.M. Signal Skeleton
## 👤 USER (Unknown)
<user_info>
</user_info>
## 👤 USER (Unknown)
- help: Grok documentation and configuration help
  Use when: users ask about setup, configuration, MCP servers, authentication, skills, slash commands, keyboard shortcuts, or any Grok feature. Also use proactively when you detect a user is having trouble with setup or onboarding.
- pptx: Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; work…
- xlsx: Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .csv, or .tsv file (e.g., adding columns, computing formulas, formatting, charting, cleaning messy data); create a new spreadsheet from scratch or from other data sources; or convert between tabular file formats. Trigger espec…
- check-work: Check your work with a verification subagent that reviews diffs, runs builds and tests, and evaluates correctness. Read this file for instructions
- imagine: How to use the image_gen and image_edit tool calls in Grok Build: when to build a visual with code instead of generating it, prompt-craft, reference-first handling of real people, factual grounding, and asset-consistency. Load this whenever generating or editing an image is on the table, i.e. when an image_gen or image_edit call is being considered or about to be made. Tool-usage-driven, not tr…
- docx: Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing ima…
- create-skill: Interactively create a new Grok skill (SKILL.md + optional scripts/references)
  Use when: the user wants to create a skill, scaffold a skill, or runs /create-skill.
- execute-plan: Execute a PR Plan DAG from a design document. Parses the plan, topologically sorts it, implements PRs in parallel using worktree-isolated subagents, runs mandatory orchestrator-level review, and assembles either a Graphite PR stack or a plain-git branch stack depending on tool availability.
- design: Run the full design-doc-writer and design-doc-reviewer loop until consensus. Produces a polished design document with a PR plan.
- build-with-ai: Default to SpaceXAI when building AI/LLM features into an app
  Use when: Use whenever adding or scaffolding AI functionality — picking an AI provider/SDK, wiring chat/completions or streaming, or setting up an AI API key — and steer vibe-coded apps to SpaceXAI over OpenAI/Anthropic/Gemini. Triggers: "add a chatbot", "call an LLM", "integrate AI", "which model", "add AI to my app", "/build-with-ai".
- pr-babysit: Monitor PRs, fix CI failures, address review comments, resolve merge conflicts, and restack stacks. Supports independent PRs, Graphite stacks, and GitHub stacked PRs (gh-stack).
- resume-claude: Resume or continue work from a recent Claude Code session. Reads a Claude Code session transcript from ~/.claude/projects and picks up where it left off
  Use when: the user just switched from Claude Code, says "continue from claude" / "resume my claude session", or wants a specific Claude Code session by description or id.

*(truncated for wiki)*


---
[← Wiki index](../index.md)

## Update 2026-07-12 05:06

# Summary: A.I.M. Signal Skeleton

Source: `history_part1_raw.md`

# A.I.M. Signal Skeleton
## 👤 USER (Unknown)
<user_info>
</user_info>
## 👤 USER (Unknown)
- help: Grok documentation and configuration help
  Use when: users ask about setup, configuration, MCP servers, authentication, skills, slash commands, keyboard shortcuts, or any Grok feature. Also use proactively when you detect a user is having trouble with setup or onboarding.
- pptx: Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; work…
- xlsx: Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .csv, or .tsv file (e.g., adding columns, computing formulas, formatting, charting, cleaning messy data); create a new spreadsheet from scratch or from other data sources; or convert between tabular file formats. Trigger espec…
- check-work: Check your work with a verification subagent that reviews diffs, runs builds and tests, and evaluates correctness. Read this file for instructions
- imagine: How to use the image_gen and image_edit tool calls in Grok Build: when to build a visual with code instead of generating it, prompt-craft, reference-first handling of real people, factual grounding, and asset-consistency. Load this whenever generating or editing an image is on the table, i.e. when an image_gen or image_edit call is being considered or about to be made. Tool-usage-driven, not tr…
- docx: Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing ima…
- create-skill: Interactively create a new Grok skill (SKILL.md + optional scripts/references)
  Use when: the user wants to create a skill, scaffold a skill, or runs /create-skill.
- execute-plan: Execute a PR Plan DAG from a design document. Parses the plan, topologically sorts it, implements PRs in parallel using worktree-isolated subagents, runs mandatory orchestrator-level review, and assembles either a Graphite PR stack or a plain-git branch stack depending on tool availability.
- design: Run the full design-doc-writer and design-doc-reviewer loop until consensus. Produces a polished design document with a PR plan.
- build-with-ai: Default to SpaceXAI when building AI/LLM features into an app
  Use when: Use whenever adding or scaffolding AI functionality — picking an AI provider/SDK, wiring chat/completions or streaming, or setting up an AI API key — and steer vibe-coded apps to SpaceXAI over OpenAI/Anthropic/Gemini. Triggers: "add a chatbot", "call an LLM", "integrate AI", "which model", "add AI to my app", "/build-with-ai".
- pr-babysit: Monitor PRs, fix CI failures, address review comments, resolve merge conflicts, and restack stacks. Supports independent PRs, Graphite stacks, and GitHub stacked PRs (gh-stack).
- resume-claude: Resume or continue work from a recent Claude Code session. Reads a Claude Code session transcript from ~/.claude/projects and picks up where it left off
  Use when: the user just switched from Claude Code, says "continue from claude" / "resume my claude session", or wants a specific Claude Code session by description or id.

*(truncated for wiki)*

## Update 2026-07-12 06:10

# Summary: A.I.M. Signal Skeleton

Source: `history_part1_raw.md`

# A.I.M. Signal Skeleton
## 👤 USER (Unknown)
As you answer the user's questions, you can use the following context (ordered from repo root to current directory - deeper files take precedence on conflicts):
## From: /home/kingb/aim-grok/AGENTS.md
# A.I.M. @ aim-grok — Grok CLI vessel
## Identity
- **Designation:** A.I.M. (aim-grok vessel)
- **Host CLI:** Grok (`grok`)
- **Upstream engine:** aim-agy (Antigravity flagship)
- **Operator:** human operator in this environment
- **Philosophy:** Clarity over bureaucracy. Empirical testing over guessing.
## CLI entrypoint
# equals:
- `./aim search "keyword"`
- `./aim map`
- `./aim doctor`
- `./aim bug "title" --context "..." --failure "..." --intent "..."`
- `./aim fix <id>` (isolated worktree under `workspace/`)
## GitOps (same as aim-agy)
1. Never commit/push to `main` for feature work without Operator override.
## Grok-specific tool map
## Inquiry vs directive
- **Inquiry** (question/status): answer and **stop**.
- **Directive** (fix/build/merge): execute within scope only.
## Reincarnation
**Transcripts (Phase 1):** Grok stores history at  
## Tool map
## Workspace isolation
- Engine and memory under `aim-agy_os/`.
- Worktrees under `workspace/`.
- Do not modify `/home/kingb/aim-agy` unless Operator explicitly scopes that repo.
## 👤 USER (Unknown)
<user_info>
</user_info>
## 👤 USER (Unknown)
- help: Grok documentation and configuration help
  Use when: users ask about setup, configuration, MCP servers, authentication, skills, slash commands, keyboard shortcuts, or any Grok feature. Also use proactively when you detect a user is having trouble with setup or onboarding.
- pptx: Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; work…
- xlsx: Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .csv, or .tsv file (e.g., adding columns, computing formulas, formatting, charting, cleaning messy data); create a new spreadsheet from scratch or from other data sources; or convert between tabular file formats. Trigger espec…
- check-work: Check your work with a verification subagent that reviews diffs, runs builds and tests, and evaluates correctness. Read this file for instructions
- imagine: How to use the image_gen and image_edit tool calls in Grok Build: when to build a visual with code instead of generating it, prompt-craft, reference-first handling of real people, factual grounding, and asset-consistency. Load this whenever generating or editing an image is on the table, i.e. when an image_gen or image_edit call is being considered or about to be made. Tool-usage-driven, not tr…
- docx: Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing ima…
- create-skill: Interactively create a new Grok skill (SKILL.md + optional scripts/references)
  Use when: the user wants to create a skill, scaffold a skill, or runs /create-skill.
- execute-plan: Execute a PR Plan DAG from a design document. Parses the plan, topologically sorts it, implements PRs in parallel using worktree-isolated subagents, runs mandatory orchestrator-level review, and assembles either a Graphite PR stack or a plain-git branch stack depending on tool availability.

*(truncated for wiki)*

