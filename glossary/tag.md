---
title: "Tag"
category: entity
tags: [tag, metadata, categorisation, retrieval]
date: 2026-05-23
related:
  - term: "YAML Front Matter"
    file: yaml-front-matter.md
    rel: partOf
  - term: "Memory File"
    file: memory-file.md
    rel: partOf
  - term: "Semantic Search"
    file: semantic-search.md
    rel: relatedTerm
aliases: ["label", "category tag"]
---

**A short keyword stored in a memory file's YAML front matter that categorises the file and makes it retrievable by topic even when semantic search returns noisy results.**

## Definition

A tag is a string element in the `tags` list of a memory file's YAML front matter. Tags provide an explicit, human-curated categorisation layer on top of the semantic vector index. Where semantic search finds files by conceptual similarity, tag-based filtering finds files by declared membership in a category.

Tags should be chosen from a controlled vocabulary rather than invented freely for each file. Proliferating near-synonym tags (e.g. `lancedb`, `lance-db`, `LanceDB`) degrade retrieval because queries must match the tag exactly. The agent constitution (§13, tag coherence) requires agents to check for existing near-synonym tags before saving a new one.

Tags are lowercase, kebab-case strings (e.g. `meeting`, `lancedb`, `mcp`, `open-brain`).

## Usage in This System

Every memory file includes `tags` in its front matter:
```yaml
tags: [journal, lancedb, architecture]
```

Tags are the primary filter used when retrieving files by topic in addition to semantic search. They also appear in the `glossary/` front matter as part of the extended schema defined in `definition_scheme.md`.

## Related Terms

- [YAML Front Matter](./yaml-front-matter.md)
- [Memory File](./memory-file.md)
- [Semantic Search](./semantic-search.md)

## References

1. [`.github/copilot-instructions.md` §13](../.github/copilot-instructions.md) — tag coherence guidance in the chain-of-thought reasoning section.
