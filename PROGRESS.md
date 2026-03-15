# Progress

---

## 2026-03-07 — Copilot headless-mode setup

Added `.github/copilot-setup-steps.yml` and `.vscode/mcp.json` so GitHub Copilot's coding agent can operate on this memory system from the GitHub web UI or mobile app with no local IDE. Added Section 15 (headless mode) to `.github/copilot-instructions.md`. Rebased PR onto main after main introduced `.github/copilot-instructions.md` (superseding `AGENTS.md`); moved the headless-mode section from the old AGENTS.md addition into copilot-instructions.md accordingly.

**Mini-Retro**
1. Did the process work? Yes — the files are straightforward; the main complexity was the rebase against a diverged main that had replaced AGENTS.md.
2. What slowed down or went wrong? The PR branch diverged from a main that had already removed AGENTS.md. Manual rebase was needed because the branch's base pre-dated PR #3 and #4.
3. What single change would prevent this next time? Merging main into feature branches earlier (before they diverge significantly) would prevent this class of conflict.
4. Is this a pattern? Potentially — if multiple Copilot branches run against the same repo simultaneously they will each diverge from main. Worth raising in the backlog.

---

## 2026-03-07 — Standardise agent instructions
## 2026-03-07

Standardisation pass: replaced `## 7. Mandatory System Self-Improvement` in `.github/copilot-instructions.md` with the unified **Continuous Improvement & Learning** framework (section 7). Added new `## 13. Chain-of-Thought Reasoning` section tailored to this repo's memory workflows; renumbered Privacy to section 14. Updated CHANGELOG.md under [Unreleased].

**Mini-Retro**
1. Did the process work? Yes — the instruction file was well-structured and the targeted replacement was straightforward.
2. What slowed down or went wrong? Nothing significant; the only ambiguity was whether the new Chain-of-Thought section should be numbered 13 or 14 (resolved by inserting before Privacy and bumping Privacy to 14).
3. What single change would prevent this next time? Keeping section numbers stable in the instructions document would remove renumbering ambiguity on future insertions.
4. Is this a pattern? No — first occurrence. Worth watching if further sections are added in future standardisation passes.

---

## 2026-03-07 — Align copilot-instructions with owner's personal Copilot instructions

Applied six targeted updates to `.github/copilot-instructions.md` to remove contradictions with the owner's personal Copilot instructions, without touching any repo-specific content (memory system constitution, LanceDB, MCP, folder structure, file naming, front matter, privacy, headless mode, chain-of-thought):

1. **§2 Skills** — Added `git submodule update --init --recursive` setup note and a "no synthesising substitutes" fallback rule.
2. **§7 Identity as Architect** — Replaced hollow "You are a collaborator that learns" blockquote with direct "Complete the work. Improve the system." wording.
3. **§7 Mini-Retro** — Added mandate-action note after the four questions: "Do not just answer — make the change."
4. **§7 Signal table** — Added missing `Missing skill` row.
5. **§7 "Done" checklist** — Added `CHANGELOG.md updated if behaviour changed` and `remove-ai-slop run on committed prose`.

**Mini-Retro**
1. Did the process work? Yes — all changes were surgical text replacements with no structural side effects.
2. What slowed down or went wrong? Nothing significant; the changes were clearly specified in the issue.
3. What single change would prevent this next time? Nothing to improve — the issue was well-specified and straightforward.
4. Is this a pattern? This is a recurring "sync personal instructions → repo instructions" task. Could add a periodic review backlog item.

---

## 2026-03-08 — Merge-conflict audit and branch hygiene (W-0002)

Audited all open pull requests against `main`. Only one open PR existed at the time of this session (PR #7 — this branch). All earlier PRs (#1–#6) had already been merged or closed. The current branch (`copilot/clean-up-merge-conflicts`) is a single clean commit ahead of `main` with no conflicts. No rebases or fixup commits were needed. Marked W-0002 as done in `BACKLOG.md`.

**Mini-Retro**
1. Did the process work? Yes — systematic enumeration of open PRs via GitHub MCP confirmed there was nothing to resolve.
2. What slowed down or went wrong? The shallow clone meant `git fetch --unshallow` was needed before seeing full branch history; this is minor but worth noting.
3. What single change would prevent this next time? Nothing actionable — the task is complete. The scheduled-workflow idea (W-0002 notes) is still worth exploring for future prevention.
4. Is this a pattern? Yes — same pattern observed in the headless-mode PR (see 2026-03-07 retro). W-0002 now closed.

---

## 2026-03-08 — Mobile capture discovery backlog (W-0003–W-0015) and doc validation

Added 13 discovery backlog items (W-0003 through W-0015) covering all viable mobile capture and retrieval paths: Slack bot, Claude iOS MCP, ChatGPT Actions, Gemini/Google ecosystem, Grok/X DM bot, iOS Shortcuts + GitHub API, Raycast/Alfred, `remember` CLI, Telegram bot, `inbox/` folder, Apple Watch dictation, self-hosted MCP server options, and LanceDB index rebuild evaluation. Fixed W-0002 duplicate `### Notes` / `---` formatting artifact. Fixed CHANGELOG.md duplicate [Unreleased] entries and added mobile capture changelog entry. Fixed stale `AGENTS.md` link in `projects/2026-03-07-copilot-headless-mode.md`. Added ADR index table to `docs/adr/README.md`. Strengthened archived header in `getting-started-prompt.md`.

**Mini-Retro**
1. Did the process work? Yes — the issue was fully specified with exact content for each backlog item, making this a clean writing task.
2. What slowed down or went wrong? CHANGELOG.md had duplicate [Unreleased] entries from a prior session; required careful deduplication to avoid losing content.
3. What single change would prevent this next time? A lint check or note in the CHANGELOG template reminding to deduplicate before adding new entries would prevent accumulation of duplicate blocks.
4. Is this a pattern? The duplicate CHANGELOG entries appear to be a one-off from a previous PR merge. Watch for it on future PRs that touch CHANGELOG.md.

---

## 2026-03-13 — BACKLOG-v2.md — implementation-ready roadmap

Created `BACKLOG-v2.md` as a complete, shaped build plan for the future of the memory system. The file contains a Vision section, an Architecture section (with plain-text layered diagram), a Research Cross-Reference table, an Outstanding Discovery section, and 11 atomic work items (W-0100–W-0110) across 5 phases:

- Phase 1 — Fix the foundation: W-0100 (pre-computed embeddings, cold-start fix) and W-0101 (Model2Vec evaluation)
- Phase 2 — Frictionless capture: W-0102 (inbox/ folder), W-0103 (triage automation), W-0104 (iOS Shortcut), W-0105 (CLI remember/recall)
- Phase 3 — Retrieval quality: W-0106 (hybrid search), W-0107 (related-memories linking)
- Phase 4 — Async capture channels: W-0108 (Telegram bot), W-0109 (Slack bot)
- Phase 5 — Infrastructure: W-0110 (self-hosted MCP server)

`BACKLOG.md` was left untouched as the historical record of the discovery agenda. Updated CHANGELOG.md under [Unreleased].

**Mini-Retro**
1. Did the process work? Yes — the issue was well-specified with phases, format requirements, and partial content for the first two items. The structure from `BACKLOG.md` provided a clear format template.
2. What slowed down or went wrong? The problem statement was truncated mid-W-0102, requiring extrapolation of the acceptance criteria and all subsequent items. The extrapolation was grounded in the existing BACKLOG.md discovery items (W-0008 through W-0015) and the stated system goals.
3. What single change would prevent this next time? Providing the full content of W-0102 and a list of intended subsequent item IDs in the issue would have removed all ambiguity about scope.
4. Is this a pattern? Truncated issue descriptions have appeared before. Worth noting in the backlog that issue specifications should be written to fit within the issue body limit or split across comments.

---

## 2026-03-15 — BACKLOG-v2.md — structured relational layer, human door, proactive agent

Extended `BACKLOG-v2.md` with 5 new work items and 2 new phases, per issue "New items in backlog":

- Phase 3 (NEW) — Structured relational layer: W-0111 (discovery: Supabase MCP architecture — two-server vs unified), W-0112 (implementation: Supabase Postgres tables for contacts, meetings, TBD)
- Phase 4 (NEW) — Human door: W-0113 (auth model + Vercel skeleton), W-0114 (contacts view, inline editing, quick-capture form)
- Phase 7 (was Phase 5) — Infrastructure: W-0115 added (proactive/scheduled agent, blocked by W-0114 in daily use)
- Previous Phase 3–5 renumbered to Phase 5–7
- W-0102 context updated: capture friction note requiring the human-door quick-capture form to use the GitHub Contents API write path (same as iOS Shortcut and CLI), not a Supabase write path
- Research Cross-Reference and Outstanding Discovery tables updated

**Mini-Retro**
1. Did the process work? Yes — the issue was precisely specified with item content, format, and dependency rules. The existing item format in BACKLOG-v2.md provided a reliable template.
2. What slowed down or went wrong? Phase renumbering required careful edits in multiple places (phase headers, Outstanding Discovery, Research Cross-Reference). No errors, but this is mechanical work that is easy to miss.
3. What single change would prevent this next time? A script or table of contents in BACKLOG-v2.md that maps phase numbers to phase names would make renumbering visible at a glance — worth raising as a backlog item.
4. Is this a pattern? Phase renumbering has now happened once. If it happens again, a structured phase index or YAML front-matter list of phases would eliminate the manual touch points.
