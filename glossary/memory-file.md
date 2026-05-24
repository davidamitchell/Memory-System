---
title: "Memory File"
category: entity
tags: [memory, markdown, file, note]
date: 2026-05-23
related:
  - term: "YAML Front Matter"
    file: yaml-front-matter.md
  - term: "Tag"
    file: tag.md
  - term: "Superseded-by"
    file: superseded-by.md
  - term: "Open-Brain"
    file: open-brain.md
aliases: ["memory", "note", "brain file", "source document"]
---

**A single Markdown file stored in this repository that represents one unit of source knowledge, from which the ontology store derives structured assertions.**

## Definition

A memory file (or source document) is a plain Markdown file (`.md`) in one of the content folders (`/meetings`, `/journal`, `/projects`). It contains YAML front matter (title, date, tags, superseded_by) followed by free-form Markdown content.

Memory files are the human-authored input to the system. The 12-processor pipeline reads them, extracts Prepared Segments (SHA-256 content-addressed fragments), and derives typed assertions that are stored in the ontology graph. The memory file itself remains the source of truth; the ontology store is a derived, query-optimised representation.

Memory files are plain text, human-readable, and git-versioned. Files that are no longer current should not be deleted; instead their `superseded_by` field should be set to the path of the newer file.

## Usage in This System

- Memory files live in `/meetings`, `/journal`, and `/projects`.
- Filename convention: `YYYY-MM-DD-<kebab-case-title>.md`.
- Every memory file should end with a `## Related` section linking to related files for human navigation.

## Related Terms

- [YAML Front Matter](./yaml-front-matter.md)
- [Tag](./tag.md)
- [Superseded-by](./superseded-by.md)
- [Open-Brain](./open-brain.md)

## References

1. [`.github/copilot-instructions.md` §9–10](../.github/copilot-instructions.md) — naming convention and required front matter for memory files.
2. [`_docs/adr/0004-provenance-model-and-control-plane.md`](../_docs/adr/0004-provenance-model-and-control-plane.md) — how source documents are processed into ontology assertions.
