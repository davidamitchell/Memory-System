---
title: "Semantic Search"
category: concept
tags: [search, retrieval, similarity, nlp]
date: 2026-05-23
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

**A search technique that finds documents by conceptual meaning rather than exact keyword matching, using vector similarity as the relevance signal.**

## Definition

Semantic search works by converting both the query and every stored document into vector embeddings, then finding the stored vectors that are geometrically closest to the query vector. Two texts are "semantically similar" if their vectors have a high cosine similarity — meaning the embedding model placed them near each other in the vector space.

This is fundamentally different from keyword search (which requires exact word overlap) or full-text search (which ranks by term frequency). Semantic search can match a query like "what did I decide about the database?" with a memory file titled "LanceDB architecture" even if the word "database" appears nowhere in that file.

The trade-off is that semantic search requires an embedding model and a vector database, and can occasionally surface false positives (documents that are statistically similar but contextually irrelevant). Hybrid search — combining vector similarity with BM25 keyword scoring — is one mitigation, explored in W-0106.

## Usage in This System

- `search_brain(query)` in `mcp_server.py` implements semantic search using LanceDB and the current embedding model.
- All AI agents working in this repository call `search_brain` before writing a new memory, to check whether the information already exists.

## Related Terms

- [Vector Embedding](./vector-embedding.md)
- [Vector Database](./vector-database.md)
- [LanceDB](./lancedb.md)
- [Retrieval](./retrieval.md)

## References

1. [LanceDB: Vector Search](https://lancedb.github.io/lancedb/search/) — how LanceDB executes vector similarity queries.
2. [SBERT: Semantic Textual Similarity](https://www.sbert.net/docs/usage/semantic_textual_similarity.html) — background on cosine similarity as a relevance metric.
