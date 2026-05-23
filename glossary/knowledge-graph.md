---
title: "Knowledge Graph"
category: concept
tags: [knowledge-graph, graph, links, ontology, structure]
date: 2026-05-23
related:
  - term: "Memory File"
    file: memory-file.md
  - term: "Semantic Search"
    file: semantic-search.md
  - term: "Tag"
    file: tag.md
  - term: "Open-Brain"
    file: open-brain.md
aliases: ["knowledge base graph", "memory graph", "vectorized knowledge graph"]
---

**A network of interlinked memory files where relationships between pieces of knowledge are made explicit through bidirectional cross-references.**

## Definition

A knowledge graph is a data model that represents information as nodes (entities or concepts) connected by typed edges (relationships). Rather than storing facts in isolated rows of a table, a knowledge graph makes the connections between facts first-class: "File A is related to File B" is itself a stored piece of information.

In Open-Brain, the knowledge graph is implemented through `## Related` sections and `superseded_by` links in memory files. Every time a memory file is created or significantly updated, the agent is required to link it to at least three related existing files. Over time this builds a navigable graph where any memory can be reached from any other by following links.

The knowledge graph complements semantic search: search finds the most statistically similar documents, while the graph reveals explicit relationships that may not be captured by embedding similarity alone (e.g. "this note supersedes that decision").

The phrase "vectorized knowledge graph" used in the original PRD refers to a knowledge graph backed by a vector index — every node is both linked explicitly and semantically searchable.

## Usage in This System

- The `## Related` section in every memory file is the graph edge list.
- `.github/copilot-instructions.md` §7 (Knowledge Graphing) mandates that agents maintain the graph on every write.
- The `superseded_by` front matter field is a directed edge indicating which file replaced this one.

## Related Terms

- [Memory File](./memory-file.md)
- [Semantic Search](./semantic-search.md)
- [Tag](./tag.md)
- [Open-Brain](./open-brain.md)

## References

1. [Wikipedia: Knowledge Graph](https://en.wikipedia.org/wiki/Knowledge_graph) — definition and academic background.
2. [`.github/copilot-instructions.md` §7](../.github/copilot-instructions.md) — the agent mandate for knowledge graphing in this repository.
