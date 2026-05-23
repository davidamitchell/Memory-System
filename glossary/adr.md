---
title: "Architecture Decision Record"
category: practice
tags: [adr, decision, architecture, governance, documentation]
date: 2026-05-23
related:
  - term: "MADR"
    file: madr.md
  - term: "Open-Brain"
    file: open-brain.md
aliases: ["ADR", "decision record"]
---

**A short, structured document that records a significant architectural or design decision, its context, the options considered, and the consequences of the chosen option.**

## Definition

An Architecture Decision Record (ADR) is a lightweight governance document that captures why a significant technical decision was made, not just what was decided. The "why" is the part most likely to be forgotten, and the part most needed when the decision is later revisited or challenged.

ADRs are stored alongside the code or content they govern, are written at decision time (not retroactively), and are append-only: once accepted, an ADR is never edited to change its decision. If the decision changes, a new ADR is written that supersedes the old one.

The format used in this repository is MADR (Markdown Any Decision Records), which provides a minimal structure: Context, Decision, Consequences.

## Usage in This System

- ADRs live in `docs/adr/` and are named `NNNN-short-title.md` (zero-padded four-digit sequence number).
- The `docs/adr/README.md` file maintains the index of all ADRs.
- Status values are `proposed → accepted → superseded / deprecated`.
- Use the `decisions` skill from `.github/skills/decisions/SKILL.md` when writing a new ADR.

## Related Terms

- [MADR](./madr.md)
- [Open-Brain](./open-brain.md)

## References

1. [ADR GitHub Organisation](https://adr.github.io/) — canonical resource for ADR formats and tooling.
2. [Michael Nygard: Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — the original ADR proposal.
3. [`docs/adr/README.md`](../docs/adr/README.md) — the ADR index for this repository.
