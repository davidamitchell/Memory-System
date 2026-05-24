---
title: "Mini-Retro"
category: practice
tags: [mini-retro, retrospective, improvement, process]
date: 2026-05-23
related:
  - term: "Open-Brain"
    file: open-brain.md
    rel: partOf
  - term: "Architecture Decision Record"
    file: adr.md
    rel: relatedTerm
aliases: ["mini retrospective", "session retrospective", "retro"]
---

**A mandatory four-question retrospective appended to `PROGRESS.md` at the end of every agent session, designed to surface process improvements and convert friction into system changes.**

## Definition

A mini-retro is a short, structured self-assessment that every agent (and human contributor) must complete before closing a session or merging a PR. It is not optional. It answers four questions:

1. **Did the process work?** Was the approach sound? Did the plan hold?
2. **What slowed down or went wrong?** No blame — just facts.
3. **What single change would prevent this next time?** If nothing: say so.
4. **Is this a pattern?** Have you seen this friction before? If yes, it deserves a fix, not just a note.

The mini-retro is the primary mechanism by which the memory system learns about itself. Agents are expected not just to answer the questions but to act on the answers: if the retro reveals a missing document, write it; if it reveals a backlog item, add it. The goal is a system that is measurably better after every ten sessions than it was before.

The mini-retro is appended to `PROGRESS.md` (never edited in place) and appears as a `**Mini-Retro**` block at the end of the session's progress entry.

## Usage in This System

- `PROGRESS.md` contains the complete history of mini-retros for this repository.
- `.github/copilot-instructions.md` §7 mandates the mini-retro and defines its four questions.
- The "What is Done" checklist in §7 requires `PROGRESS.md` to be updated with a mini-retro before a session is considered complete.

## Related Terms

- [Open-Brain](./open-brain.md)
- [Architecture Decision Record](./adr.md)

## References

1. [`.github/copilot-instructions.md` §7](../.github/copilot-instructions.md) — the mini-retro mandate and format.
2. [`PROGRESS.md`](../PROGRESS.md) — the append-only history of all mini-retros in this repository.
