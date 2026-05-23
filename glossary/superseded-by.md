---
title: "Superseded-by"
category: practice
tags: [superseded-by, lifecycle, memory, versioning]
date: 2026-05-23
related:
  - term: "Memory File"
    file: memory-file.md
  - term: "YAML Front Matter"
    file: yaml-front-matter.md
  - term: "Knowledge Graph"
    file: knowledge-graph.md
aliases: ["superseded", "supersedes", "superseded_by"]
---

**The memory lifecycle state (and corresponding front matter field) that marks a file as out of date and points to the newer file that replaced it, preserving history while directing readers to current information.**

## Definition

Superseded-by is both a lifecycle state and a YAML front matter field. When a memory file is no longer the authoritative version of the knowledge it contains — because a decision changed, information was corrected, or context shifted — it should not be deleted. Deletion destroys the ability to understand how thinking evolved over time. Instead, the file is marked superseded: its `superseded_by` front matter field is set to the path of the newer file, and a visual callout is added to the body:

```markdown
> ⚠️ Superseded by [new file](path/to/new-file.md).
```

This creates a directed edge in the knowledge graph from the old file to the new one. Anyone landing on the old file via search or a stale link is immediately directed to the current version. The old file remains fully readable and git-versioned.

The complement of superseded-by is `refactor_memory` (updating a file in place when the change is a correction or clarification, not a genuine new decision).

## Usage in This System

- Every memory file has `superseded_by: ""` in its front matter; the empty string means it is current.
- When a file is superseded, set `superseded_by: "path/to/newer-file.md"` and add the visual callout at the top of the body.
- Agents are required to check for and resolve contradictions on every write (see `.github/copilot-instructions.md` §7).

## Related Terms

- [Memory File](./memory-file.md)
- [YAML Front Matter](./yaml-front-matter.md)
- [Knowledge Graph](./knowledge-graph.md)

## References

1. [`.github/copilot-instructions.md` §7](../.github/copilot-instructions.md) — the instruction to mark superseded files rather than delete them.
