---
title: "Semantic Search"
category: concept
tags: [search, retrieval, similarity, nlp, superseded]
date: 2026-05-23
superseded_by: "glossary/retrieval.md"
related:
  - term: "Vector Embedding"
    file: vector-embedding.md
  - term: "Vector Database"
    file: vector-database.md
  - term: "LanceDB"
    file: lancedb.md
  - term: "Retrieval"
    file: retrieval.md
aliases: ["vector search", "similarity search"]
---

> ⚠️ Semantic search via vector embeddings was the retrieval mechanism in the original Open-Brain design concept. That approach was replaced by ontology-based retrieval before implementation. See [ADR-0002](../docs/adr/0002-move-from-vector-storage-to-ontology.md) and [Retrieval](./retrieval.md) for the current approach.

**A search technique that finds documents by conceptual meaning rather than exact keyword matching, using vector similarity as the relevance signal.**

## Definition

Semantic search works by converting both the query and every stored document into vector embeddings, then finding the stored vectors that are geometrically closest to the query vector. Two texts are "semantically similar" if their vectors have a high cosine similarity — meaning the embedding model placed them near each other in the vector space.

This is fundamentally different from keyword search (which requires exact word overlap) or full-text search (which ranks by term frequency). Semantic search can match a query like "what did I decide about the database?" with a document titled "LanceDB architecture" even if the word "database" appears nowhere in that file.

The trade-off is that semantic search requires an embedding model and a vector database, and can occasionally surface false positives. It also provides no structural understanding of concepts or their relationships — it returns statistically similar documents, not logically related ones.

## Usage in This System

Semantic search is **not** the retrieval mechanism of this system. It was the original design concept and is retained here as a defined term for historical reference. The current retrieval approach is ontology-based graph traversal — see [Retrieval](./retrieval.md).

## Related Terms

- [Vector Embedding](./vector-embedding.md)
- [Vector Database](./vector-database.md)
- [LanceDB](./lancedb.md)
- [Retrieval](./retrieval.md)

## References

1. [ADR-0002](../docs/adr/0002-move-from-vector-storage-to-ontology.md) — decision to replace vector/semantic search with ontology-based retrieval.
2. [SBERT: Semantic Textual Similarity](https://www.sbert.net/docs/usage/semantic_textual_similarity.html) — background on cosine similarity as a relevance metric.
