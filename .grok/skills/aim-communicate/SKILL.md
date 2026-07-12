---
name: aim-communicate
description: >
  Inter-agent communication via tmux with permission gates, chalkboard + short-paste
  protocol (Grok/AGY-hardened). Use when messaging another AI agent in a tmux session,
  board-room/swarm chat, or when the user asks to talk to another agent / send a prompt
  to a session. Migrated from Antigravity CLI; updated after aim-grok ↔ aim-agy dispatch.
---

# AIM-Communicate: Inter-Agent Tmux Protocol (Grok)

You may operate where multiple AI agents run in different tmux sessions (board room / swarm).
On this host, common sessions include: `aim-agy`, `aim-grok`, `aim-connect`, `aim-youtube`, etc.

## 1. Permission mandate

You are **forbidden** from unilaterally messaging another agent's tmux session unless the Operator explicitly approves.

- If another agent should review work, pause and ask the Operator first.
- Example: *"I finished this function. May I send it to the Python-Developer in session `dev-2` for review?"*
- Only send after clear approval.
- Operator text like "tell aim-agy …" / "communicate with …" **is** approval for that specific target and message intent.

## 2. Discover targets first

```bash
tmux list-sessions
tmux list-panes -a -F '#{session_name} #{pane_current_command} #{pane_current_path}'
tmux capture-pane -t <session> -p -J -S -20   # is the agent idle at a prompt?
```

Do not paste into a session that is mid-tool-run unless the Operator insists; wait for an idle `>` / prompt line when possible.

## 3. Prefer chalkboard + short paste (Grok/AGY fix)

**Empirical fix (aim-grok → aim-agy, 2026-07-11):**  
Long multi-section messages loaded with `set-buffer` / `paste-buffer -p` often **failed to appear or submit** in Antigravity (`agy`) prompts. Short messages **did** land. Use the chalkboard pattern for anything longer than ~2–3 sentences.

### 3a. Write the full dispatch to disk

Put shared state where the target project already looks for artifacts (prefer under the target repo):

```bash
# Example for aim-agy
DISPATCH="/home/kingb/aim-grok/aim-agy_os/planning-artifacts/DISPATCH_FROM_AIM_GROK.md"
# write full instructions with cat/heredoc to $DISPATCH
```

Include in the file: who you are, path to any audit/docs, concrete tasks, reply session name, structured reply format, and blast-radius limits (no push to main, no destructive ops without Operator).

### 3b. Send a SHORT pointer message only

```bash
SHORT='[DISPATCH from <your-session> / Operator] Please read and execute: <absolute-path-to-dispatch>. Then reply to tmux session <your-session> with structured AGREED / DISAGREE / QUESTIONS. No open-ended chat.'

tmux set-buffer -b aim_comm_short "$SHORT"
# optional: clear half-typed input
tmux send-keys -t <target_session> C-u
sleep 0.15
tmux paste-buffer -b aim_comm_short -p -t <target_session>
sleep 0.4
# submit: Escape and Enter MUST be separate commands
tmux send-keys -t <target_session> Escape
sleep 0.25
tmux send-keys -t <target_session> Enter
```

### 3c. Verify delivery

```bash
sleep 1
tmux capture-pane -t <target_session> -p -J -S -25 | tail -30
```

Success signals: short text visible above the prompt, `Loading...` / tool use / `Read(...DISPATCH...)`.  
If still empty after 2s, retry short paste once; do **not** re-paste the full novel.

### 3d. Long paste (only if short path fails and Operator needs inline text)

```bash
# load-buffer from file is more reliable than set-buffer for long text
tmux load-buffer -b aim_comm_long /path/to/message.txt
tmux send-keys -t <target> C-u
sleep 0.15
tmux paste-buffer -b aim_comm_long -p -t <target>
sleep 0.5
tmux send-keys -t <target> Escape
sleep 0.25
tmux send-keys -t <target> Enter
```

Still prefer chalkboard when possible.

## 4. Submit rules (critical)

| Do | Don't |
|----|--------|
| `paste-buffer -p` (bracketed paste) for message body | `tmux send-keys` with the full message text |
| `Escape` then `Enter` as **two** `send-keys` with a short sleep | One `send-keys Escape Enter` (AGY/Gemini often swallows and spams newlines) |
| Confirm with `capture-pane` | Assume delivery without checking |
| Name your session in the message (`aim-grok`) so they can reply | Vague "reply to me" |

## 5. Loop prevention (constraint mandate)

When messaging another agent, constrain the reply:

- **Bad:** "What do you think?" (open-ended chat loop)
- **Good:** Structure required sections and forbid freestyle:

```text
Structure your reply as:
1. AGREED (with issue #s if created)
2. DISAGREE / CORRECT (finding + reason)
3. QUESTIONS (if any)
Do not open an open-ended chat loop. One structured reply (brief clarifications only if needed).
```

## 6. Shared state (chalkboard)

Do not paste entire files or audits over tmux. Write to a path, then point:

- Audits / plans: `…/planning-artifacts/*.md`
- Scratch code: `/tmp/…` or a branch
- Message: *"Read `/absolute/path/to/file.md` and execute the task section."*

## 7. Receiving replies (on aim-grok)

- Replies may arrive as **pasted text into this session's prompt** (Operator or peer agent), not only as a silent side-channel.
- Treat structured blocks (`AGREED` / `DISAGREE` / `QUESTIONS`) as the peer agent's formal response.
- Acknowledge to the Operator; do not auto-reply to the peer unless the Operator authorizes another hop (avoids agent ping-pong).

## 8. Host map (reference)

| Session | Typical agent | Typical cwd |
|---------|---------------|-------------|
| `aim-agy` | Antigravity (`agy`) | `/home/kingb/aim-agy` |
| `aim-grok` | Grok CLI (`grok`) | `/home/kingb/aim-grok` |
| `aim-connect` | `agy` | `/home/kingb/aim-connect` |

Re-check with `tmux list-sessions` — names can change.

## 9. Worked example (this ecosystem)

**Goal:** Tell aim-agy an audit exists and to file tickets.

1. Operator authorized communication.
2. Wrote `…/planning-artifacts/PROJECT_AUDIT.md` (already present) + `DISPATCH_FROM_AIM_GROK.md`.
3. Short paste into `aim-agy` with absolute paths.
4. Verified: agent `Read` the dispatch and audit, opened issues #66–#72.
5. Peer replied with AGREED/DISAGREE/QUESTIONS structure (delivered via Operator / session).

## 10. Anti-patterns

- Unilateral swarm chatter without Operator approval
- Long paste-first without chalkboard
- Combined Escape+Enter
- Asking peer to push to `main` or run destructive cleanup in the same message without Operator scope
- Continuous back-and-forth without Operator in the loop
