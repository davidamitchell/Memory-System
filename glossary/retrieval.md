---
title: "Retrieval"
category: concept
tags: [retrieval, search, memory, recall]
date: 2026-05-23
related:
  - term: "Semantic Search"
    file: semantic-search.md
  - term: "LanceDB"
    file: lancedb.md
  - term: "MCP Tool"
    file: mcp-tool.md
  - term: "Knowledge Graph"
    file: knowledge-graph.md
aliases: ["recall", "memory retrieval", "search"]
---

**The process of finding and returning relevant memory files in response to a query, using vector similarity, keyword matching, or graph traversal.**

## Definition

Retrieval is the read side of the memory system: given a natural-language query (or a structured filter), return the most relevant memory files. It is the counterpart to capture (writing memories in) and the operation that delivers value to the user or agent.

In Open-Brain, the primary retrieval mechanism is semantic search via LanceDB: the query is embedded by the same model used to embed documents, and the nearest-neighbour vectors are returned. This retrieves documents by meaning, not by keyword.

Retrieval quality is a first-class engineering concern in this system. Poor retrieval — returning irrelevant results, or failing to surface a document that should clearly match — undermines the entire value proposition of a personal memory system. W-0106 addresses hybrid search (combining vector similarity with BM25 keyword scoring) as a quality improvement, and W-0107 addresses related-memories linking to surface graph-connected memories that pure vector search might miss.

## Usage in This System

- `search_brain(query)` is the retrieval tool. Agents call it before every write to avoid duplicating existing memories.
- Retrieval quality signals (poor or missing results) should be noted in the mini-retro and raised as backlog items.

## Related Terms

- [Semantic Search](./semantic-search.md)
- [LanceDB](./lancedb.md)
- [MCP Tool](./mcp-tool.md)
- [Knowledge Graph](./knowledge-graph.md)

## References

1. [LanceDB: Full-Text and Vector Search](https://lancedb.github.io/lancedb/search/) — retrieval mechanisms available in LanceDB.
2. [`BACKLOG-v2.md` W-0106](../BACKLOG-v2.md) — hybrid search improvement item.
