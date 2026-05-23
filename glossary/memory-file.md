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
aliases: ["memory", "note", "brain file"]
---

**A single Markdown file stored in this repository that represents one unit of knowledge in the memory system.**

## Definition

A memory file is the atomic storage unit of Open-Brain. Each memory file is a Markdown file (`.md`) in one of the content folders (`/meetings`, `/journal`, `/projects`) or the inbox. It contains YAML front matter (title, date, tags, superseded_by) followed by the memory content in free-form Markdown.

Memory files are plain text, human-readable, and git-versioned. They are the source of truth for all content in the system; the LanceDB vector index is a derived artefact that can be discarded and rebuilt from the files at any time.

Every memory file is expected to end with a `## Related` section linking to three or more related memories, supporting manual navigation in addition to semantic search. Files that are no longer current should not be deleted; instead their `superseded_by` field should be set to the path of the newer file.

## Usage in This System

- Memory files live in `/meetings`, `/journal`, and `/projects` (and optionally `/inbox` once W-0102 lands).
- Filename convention: `YYYY-MM-DD-<kebab-case-title>.md`.
- Every write via `add_memory` creates a memory file and a paired `.embedding.json` file.
- `refactor_memory` overwrites an existing memory file in place without creating a new one.

## Related Terms

- [YAML Front Matter](./yaml-front-matter.md)
- [Tag](./tag.md)
- [Superseded-by](./superseded-by.md)
- [Open-Brain](./open-brain.md)

## References

1. [`.github/copilot-instructions.md` §9–10](../.github/copilot-instructions.md) — naming convention and required front matter for memory files.
2. [`projects/README.md`](../projects/README.md) — example front matter for project memory files.
