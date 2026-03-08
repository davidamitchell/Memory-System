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

## 2026-03-08 — Mobile capture discovery backlog (W-0003–W-0015) and doc validation

Added 13 discovery backlog items (W-0003 through W-0015) covering all viable mobile capture and retrieval paths: Slack bot, Claude iOS MCP, ChatGPT Actions, Gemini/Google ecosystem, Grok/X DM bot, iOS Shortcuts + GitHub API, Raycast/Alfred, `remember` CLI, Telegram bot, `inbox/` folder, Apple Watch dictation, self-hosted MCP server options, and LanceDB index rebuild evaluation. Fixed W-0002 duplicate `### Notes` / `---` formatting artifact. Fixed CHANGELOG.md duplicate [Unreleased] entries and added mobile capture changelog entry. Fixed stale `AGENTS.md` link in `projects/2026-03-07-copilot-headless-mode.md`. Added ADR index table to `docs/adr/README.md`. Strengthened archived header in `getting-started-prompt.md`.

**Mini-Retro**
1. Did the process work? Yes — the issue was fully specified with exact content for each backlog item, making this a clean writing task.
2. What slowed down or went wrong? CHANGELOG.md had duplicate [Unreleased] entries from a prior session; required careful deduplication to avoid losing content.
3. What single change would prevent this next time? A lint check or note in the CHANGELOG template reminding to deduplicate before adding new entries would prevent accumulation of duplicate blocks.
4. Is this a pattern? The duplicate CHANGELOG entries appear to be a one-off from a previous PR merge. Watch for it on future PRs that touch CHANGELOG.md.
