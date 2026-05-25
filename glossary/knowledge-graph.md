---
title: "Knowledge Graph"
category: concept
tags: [knowledge-graph, graph, links, ontology, structure]
date: 2026-05-23
related:
  - term: "Open-Brain"
    file: open-brain.md
    rel: partOf
  - term: "Tag"
    file: tag.md
    rel: uses
aliases: ["knowledge base graph", "ontology graph"]
---

**A structured network in which entities (concepts, assertions, sources) are connected by typed relationships, enabling reasoning, traversal, and structured query.**

## Definition

A knowledge graph is a data model that represents information as nodes (entities or concepts) connected by typed edges (relationships). Rather than storing facts in isolated rows of a table, a knowledge graph makes the connections between facts first-class: "Concept A is a subclass of Concept B" or "Assertion X was derived from Source Y" are themselves stored pieces of information.

In Open-Brain, the knowledge graph is implemented via the ontology layer. An **upper ontology** defines universal concepts (time, causality, provenance), and **lower domain ontologies** define domain-specific concepts (engineering decisions, projects, meetings). Assertions are typed instances of ontology concepts. Provenance links trace each assertion back to the Prepared Segment (a SHA-256 content-addressed fragment of source text) from which it was derived.

This is richer than a simple `## Related` link list: the ontology encodes explicit, machine-readable relationship types (subClassOf, derivedFrom, contradicts, supersedes) that support formal reasoning and structured query (e.g. SPARQL).

## Usage in This System

- The ontology store is the knowledge graph of this system. See `_docs/design/ontology-system-design.md` for the component and sequence diagrams.
- The 12-processor pipeline (defined in ADR-0004) is responsible for populating the knowledge graph from source documents.
- `## Related` sections in Markdown files are informal link annotations; they are not the knowledge graph itself.

## Related Terms

- [Open-Brain](./open-brain.md)
- [Tag](./tag.md)

## References

1. [Wikipedia: Knowledge Graph](https://en.wikipedia.org/wiki/Knowledge_graph) — definition and academic background.
2. [`_docs/adr/0004-provenance-model-and-control-plane.md`](../_docs/adr/0004-provenance-model-and-control-plane.md) — ADR defining the ontology architecture.
3. [`_docs/design/ontology-system-design.md`](../_docs/design/ontology-system-design.md) — full component and sequence diagrams for the knowledge graph implementation.
