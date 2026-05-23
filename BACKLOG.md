# Backlog

---

## W-0001

status: done
created: 2026-03-07
updated: 2026-03-07

### Outcome

Repository structure is standardised: single `.github/copilot-instructions.md` source of truth, `.github/skills` submodule, `sync-skills.yml` workflow, `BACKLOG.md`, `PROGRESS.md`, `CHANGELOG.md`, and `docs/adr/` all present and consistent.

### Context

Standardisation pass to remove AGENTS.md and align with all other repos in the davidamitchell organisation.

## W-0002

status: done
created: 2026-03-07
updated: 2026-03-08

### Outcome

All open PR branches were verified against `main`. No conflicts found — only one open PR existed (PR #7) and it was cleanly rebased on `main`.

### Context

When multiple Copilot feature branches are open simultaneously they may diverge from a main that has received merged PRs. Detected during the headless-mode setup PR which required a manual rebase after main replaced AGENTS.md. On 2026-03-08 a full audit confirmed no concurrent conflicts.

### Notes

Consider adding a scheduled workflow or PR check that detects when a Copilot branch is more than N commits behind main and posts a comment prompting a rebase.

---

## W-0003

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research whether a Slack bot (personal workspace or shared) can receive messages and write them directly to the Memory-System repo as `.md` files via the GitHub API. Determine: (a) whether a free Slack workspace + incoming webhook or Slash command is sufficient, (b) whether a hosted bot (e.g. on Railway, Render, or a GitHub Actions webhook receiver) is needed, (c) latency from message → committed file, (d) [retrieval](./glossary/retrieval.md): can the bot respond to a query by calling `search_brain` results back into the Slack thread? Key unknown: does the hosted component requirement kill the "zero infrastructure" design goal?

### Context

Slack is already open on most people's phones all day. Sending a message to a dedicated `#brain` channel is 2 taps. This is potentially the lowest-friction mobile [capture](./glossary/capture.md) path that doesn't require a new app.

---

## W-0004

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research whether Claude for iOS supports [MCP](./glossary/mcp.md) connections to a locally-running `mcp_server.py`, or whether there is a cloud-hosted MCP option. Determine: (a) current state of MCP support in the Claude mobile app (as of 2026), (b) whether Anthropic's planned "personal context" or memory features could serve as a bridge, (c) whether a self-hosted [MCP server](./glossary/mcp-server.md) (e.g. on a home server, VPS, or cloud run) accessible over HTTPS would be recognised by the Claude iOS app, (d) the security model — is it safe to expose `mcp_server.py` to the internet? Key question: is Claude iOS the closest thing to a ready-made solution if you're willing to host the server?

### Context

Claude Desktop already works with the local MCP server. If the iOS app supports the same MCP config, this is a zero-new-code path. The blocker is that `mcp_server.py` must be reachable from the internet, not just localhost.

---

## W-0005

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research whether ChatGPT for iOS supports any mechanism to connect to an external memory system: (a) OpenAI Actions / plugin architecture — can a custom GPT be configured with an Action that POSTs to a self-hosted endpoint wrapping `add_memory`? (b) ChatGPT's native Memory feature — is there any API or export hook to sync ChatGPT memories into this repo? (c) Can a custom GPT be configured to call `search_brain` via an HTTP Action before responding? Determine the hosting requirement and auth model.

### Context

ChatGPT is the most widely used AI app on iOS. If a custom GPT can be pointed at a simple HTTP wrapper around the [MCP tools](./glossary/mcp-tool.md), the retrieval and capture path becomes: open ChatGPT → speak/type → memory is stored or searched. The hosted endpoint requirement is the key unknown.

---

## W-0006

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research Google's equivalent of MCP/Actions for mobile: (a) Gemini Extensions and whether they support custom external tools, (b) Google AppSheet or Workspace Apps as a lightweight form-based capture interface that writes to Google Drive → syncs to GitHub, (c) Google Assistant routines — can "Hey Google, remember X" be hooked into a GitHub API write? (d) Gemini for Workspace — if owner uses Google Workspace, does Gemini have any memory or note-taking integration?

### Context

Lower priority than Claude/ChatGPT given the owner's tool stack, but worth scanning — Google has deep iOS integration and Assistant is always-on on Android.

---

## W-0007

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research whether Grok on iOS has any plugin, MCP, or external tool integration that would allow it to write to or read from an external memory system. Also: could the X/Twitter API be used as a capture channel — e.g. a private tweet or DM to a bot account that triggers a GitHub API write? Determine viability and effort.

### Context

Speculative but low-effort to evaluate. If owner is already in the X app, a DM-based capture bot is a 2-tap flow.

---

## W-0008

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Build and document an iOS Shortcut that: (a) accepts text from the Share Sheet, dictation, or a manual text field, (b) calls the GitHub Contents API (`PUT /repos/{owner}/{repo}/contents/{path}`) to write a new `.md` file directly to the `journal/` or `inbox/` folder, (c) requires zero running infrastructure — just a GitHub PAT stored in the Shortcut. Determine: file naming convention, front-matter templating within Shortcuts, and whether the Shortcut can also call a read endpoint (e.g. search via GitHub code search API or a static pre-built index) for retrieval.

### Context

This is the highest-confidence, lowest-infrastructure option for mobile capture. No server, no bot, no subscription. The GitHub API supports file creation directly. Retrieval is harder — GitHub code search is keyword-only, not semantic — but capture alone solves 80% of the friction.

---

## W-0009

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Build a Raycast extension or Alfred workflow that: (a) opens a floating text input on a global keyboard shortcut, (b) sends the text to `mcp_server.py` via stdin/stdout or directly calls the underlying Python function, (c) dismisses immediately. Also evaluate whether Raycast AI (if owner has it) can answer questions against the memory system. Determine: does Raycast support MCP tools natively or does it require a custom extension?

### Context

On the desktop side, this is the equivalent of the iOS Shortcut — one keystroke from anywhere to capture. Raycast already has MCP support in its AI features as of 2025.

---

## W-0010

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Add a `remember` CLI script to the repo that: (a) accepts a string argument, (b) writes a timestamped `.md` file to `journal/` using the same logic as `add_memory` in `mcp_server.py`, (c) commits and pushes via `git_commit_and_push`, (d) optionally accepts `--folder` to target `meetings/` or `projects/`. Script must be installable as `remember` on PATH (e.g. via a symlink or `pip install -e .` entry point). Also add a `recall` command that calls `search_brain` and prints results to stdout — so retrieval works from any terminal session without the MCP server needing to be running.

### Context

Engineers live in the terminal. `remember "decided X because Y"` is lower-friction than any GUI for capture during a coding session. `recall "what did I decide about [LanceDB](./glossary/lancedb.md)"` replaces opening an AI chat for quick lookups.

---

## W-0011

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research and prototype a Telegram bot that: (a) accepts any message sent to it and calls `add_memory` (writing to `journal/`), (b) responds to messages starting with `?` by calling `search_brain` and replying with the top results, (c) runs as a long-polling or webhook Python process, (d) can be hosted on a Raspberry Pi, home server, or cheap VPS. Determine: effort to set up, security model, whether the Telegram bot token + GitHub PAT model is acceptably secure, and whether this is better or worse than the Slack option (W-0003).

### Context

Telegram bots are trivial to create and the bot API is free and well-documented. The capture UX is identical to messaging a contact. Retrieval via `?what do I know about X` is natural. The hosted component is unavoidable here — unlike iOS Shortcuts (W-0008).

---

## W-0012

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Add an `inbox/` folder to the repo as a frictionless drop zone: (a) any capture tool (Shortcut, bot, CLI) can write unstructured notes here without requiring a title, tags, or folder decision, (b) a periodic agent task (weekly or on-demand) reads the inbox, classifies each item, and moves it to `meetings/`, `journal/`, or `projects/` with proper front-matter. Determine: does removing the "what folder?" decision at capture time meaningfully reduce friction? What is the minimum viable agent prompt for inbox triage?

### Context

The current `add_memory` tool requires `folder` as a parameter. Forcing a folder decision at capture time is friction. An [inbox](./glossary/inbox.md) pattern removes that decision from the capture path and defers it to a low-urgency [triage](./glossary/triage.md) step.

---

## W-0013

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research whether an Apple Watch complication or Shortcut can: (a) accept voice dictation, (b) send the transcribed text to the iOS Shortcut from W-0008 or directly to the GitHub API. Determine latency and reliability of Watch dictation → GitHub write path.

### Context

"Hey Siri, remember X" or a Watch tap → dictate → done is potentially the fastest possible capture path. No phone unlock required. Worth evaluating even if it turns out to be unreliable for longer captures.

---

## W-0014

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research the minimum viable self-hosted deployment of `mcp_server.py` that would make it reachable from Claude iOS or ChatGPT Actions: (a) home server / Raspberry Pi with Tailscale (no open ports), (b) fly.io / Railway free tier, (c) Cloudflare Worker wrapping the GitHub API (stateless, no LanceDB — write only), (d) GitHub Actions as a compute backend (trigger via `repository_dispatch`). For each option: cost, latency, security model, and whether it preserves the "zero ongoing infrastructure management" goal. Key question: is a Cloudflare Worker wrapping just the GitHub write API sufficient for capture, with retrieval deferred to desktop?

### Context

Most of the AI app integrations (Claude iOS, ChatGPT Actions) require the MCP server or an HTTP endpoint to be reachable over the internet. This item determines whether self-hosting is feasible within the design constraints of this repo.

---

## W-0015

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Determine whether `mcp_server.py` can rebuild the full LanceDB index from the `.md` files in the repo on startup, making the index fully recoverable from git. Measure: (a) rebuild time for current corpus size, (b) rebuild time at 100 files, 500 files, (c) whether the startup rebuild is fast enough to be triggered per-request in a serverless context (enabling stateless deployment). If fast enough, the LanceDB index becomes ephemeral — no persistence needed, which simplifies all self-hosted options.

### Context

Currently `.lancedb` is excluded from git and must persist locally. If the index can be rebuilt in <5 seconds for a typical corpus, the self-hosted deployment model simplifies significantly — any stateless compute (Cloudflare Worker, Lambda, GitHub Actions) becomes viable.

---

## References

1. [`BACKLOG-v2.md`](./BACKLOG-v2.md) — the implementation-ready roadmap that supersedes this discovery backlog.
2. [`.github/copilot-instructions.md` §3](../.github/copilot-instructions.md) — the agent instruction to read the backlog at the start of every session.
3. [`glossary/README.md`](./glossary/README.md) — controlled vocabulary for terms used in these work items.
