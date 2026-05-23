# Learnings

Distilled from PROGRESS.md mini-retros. Each entry states the class of problem and the concrete fix or standing rule.

---

## Commit frequency during long documentation passes

**Pattern:** Context compaction mid-session can lose all uncommitted changes.
**Rule:** Call `report_progress` after every 2–3 file edits, not at the end. Mid-session commits keep state recoverable.
**Source:** 2026-05-23 — Full pivot documentation coherence pass

---

## Full-file replacement via the edit tool

**Pattern:** Using the `edit` tool to replace an entire large file is error-prone — the `old_str` can match only a partial section, leaving duplicate content.
**Rule:** For full-file replacements, use a bash write/truncation rather than the `edit` tool.
**Source:** 2026-05-23 — ADR-0004: provenance model and control plane

---

## Open Questions in design documents

**Pattern:** Design documents without an explicit "Open Questions" section bury uncertainty in prose, causing re-decisions in later sessions.
**Rule:** Every new design document in `docs/design/` must include an "Open Questions" section.
**Source:** 2026-05-23 — Ontology architecture design and setup

---

## Merging main into feature branches early

**Pattern:** Long-running feature branches diverge from `main` and require manual rebases to resolve conflicts introduced by concurrent PRs.
**Rule:** Merge or rebase against `main` before branches diverge significantly. Don't wait until PR review.
**Source:** 2026-03-07 — Copilot headless-mode setup

---

## CHANGELOG.md duplicate [Unreleased] entries

**Pattern:** Merging multiple PRs that each touch `CHANGELOG.md` can produce duplicate `[Unreleased]` blocks.
**Rule:** Before adding a new changelog entry, scan for duplicate `[Unreleased]` headings and deduplicate.
**Source:** 2026-03-08 — Mobile capture discovery backlog

---

## Issue descriptions truncated mid-content

**Pattern:** Problem statements written in GitHub issue bodies can be truncated before all items are specified, forcing scope extrapolation.
**Rule:** Write issue specs to fit the body limit, or split continuation across comments. Include a list of intended item IDs at the top.
**Source:** 2026-03-13 — BACKLOG-v2.md implementation-ready roadmap

---

## Phase renumbering in BACKLOG-v2.md

**Pattern:** Inserting new phases mid-document requires touching phase headers, the Outstanding Discovery table, and the Research Cross-Reference table — easy to miss one.
**Rule:** Add a phase index or table of contents to `BACKLOG-v2.md` so renumbering touch-points are visible at a glance.
**Source:** 2026-03-15 — BACKLOG-v2.md structured relational layer

---

## Shallow clone requires unshallowing before merge/rebase

**Pattern:** A shallow clone means `git fetch --unshallow` is needed before full branch history is visible; skipping this causes silent merge failures.
**Rule:** Always run `git fetch --unshallow origin` before any merge, rebase, or conflict-resolution operation.
**Source:** 2026-03-08 — Merge-conflict audit and branch hygiene

---

## Glossary cross-linking is for memory files, not design documents

**Pattern:** The Wikipedia-style cross-linking rule (§16) was applied in `docs/design/build-loop-harness.md`, which is a protocol document, not a memory file.
**Rule:** Only apply glossary cross-links in memory files (journal, meetings, projects, ADRs). Design documents and protocol docs should use plain prose.
**Source:** 2026-05-23 — build-loop-harness glossary link removal

---

**Pattern:** Inserting a new section mid-document requires renumbering all subsequent sections — a mechanical step that is easy to get wrong.
**Rule:** Keep section numbers stable where possible. When inserting, prefer appending or using sub-sections to avoid a cascade renumber.
**Source:** 2026-03-07 — Standardise agent instructions
