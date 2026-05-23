---
title: "Retrieval"
category: concept
tags: [retrieval, search, knowledge, recall]
date: 2026-05-23
related:
  - term: "Knowledge Graph"
    file: knowledge-graph.md
  - term: "MCP Tool"
    file: mcp-tool.md
  - term: "Open-Brain"
    file: open-brain.md
aliases: ["recall", "knowledge retrieval", "search"]
---

**The process of finding and returning relevant knowledge in response to a query, using ontology traversal, graph pattern matching, or structured query across the knowledge store.**

## Definition

Retrieval is the read side of the knowledge store: given a natural-language query (or a structured filter), return the most relevant knowledge. It is the counterpart to capture (writing knowledge in) and the operation that delivers value to the user or agent.

In Open-Brain, retrieval is performed by querying the ontology store. A query can traverse concept graphs within a domain, match assertion patterns, or navigate provenance links from assertions back to source segments. This is richer than vector similarity: the ontology encodes explicit relationships that similarity alone cannot capture.

Retrieval quality is a first-class engineering concern. Poor retrieval — returning irrelevant results, or failing to surface a concept that should clearly match — undermines the entire value proposition of a personal knowledge system. Retrieval quality signals should be noted in the mini-retro and raised as backlog items.

## Usage in This System

- The ontology-based MCP query interface (not yet implemented) will be the primary retrieval tool.
- Until the MCP server is implemented, agents retrieve context by searching files directly (grep, glob) and reading ADRs and design documents.
- Retrieval quality signals should be raised in the mini-retro and as backlog items.

## Related Terms

- [Knowledge Graph](./knowledge-graph.md)
- [MCP Tool](./mcp-tool.md)
- [Open-Brain](./open-brain.md)

## References

1. [W3C SPARQL Query Language](https://www.w3.org/TR/sparql11-query/) — structured query language for RDF graph retrieval.
2. [`docs/design/ontology-system-design.md`](../docs/design/ontology-system-design.md) — the retrieval architecture for the ontology store.
