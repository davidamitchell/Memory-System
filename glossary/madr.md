---
title: "MADR"
category: format
tags: [madr, adr, markdown, format, decision]
date: 2026-05-23
related:
  - term: "Architecture Decision Record"
    file: adr.md
    rel: instanceOf
aliases: ["Markdown Any Decision Records", "Markdown Architectural Decision Records"]
---

**A lightweight Markdown template for writing Architecture Decision Records that enforces the minimum structure needed to capture context, decision, and consequences.**

## Definition

MADR (Markdown Any Decision Records) is a specific format for writing ADRs, created by the ADR GitHub organisation. It provides a minimal, opinionated Markdown template that ensures every decision record captures: the context that led to the decision, the decision itself, and the consequences (positive, negative, and neutral) of choosing that option.

MADR is intentionally minimal — it avoids the verbose "options considered" tables found in other ADR formats when they are not needed, but accommodates them when they are. Files are plain Markdown, which means they are readable without tooling, diff-friendly, and can be stored in any git repository.

The minimal MADR structure is:
```
# Title
Date: YYYY-MM-DD
Status: proposed | accepted | superseded | deprecated

## Context
## Decision
## Consequences
```

## Usage in This System

- All ADRs in `_docs/adr/` use the MADR format.
- The `decisions` skill in `.github/skills/decisions/SKILL.md` provides the canonical template and guidance for this repository.

## Related Terms

- [Architecture Decision Record](./adr.md)

## References

1. [MADR — Official Documentation](https://adr.github.io/madr/) — format specification, templates, and examples.
2. [MADR GitHub Repository](https://github.com/adr/madr) — template files and changelog.
