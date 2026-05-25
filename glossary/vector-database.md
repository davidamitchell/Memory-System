---
title: "Vector Database"
category: tool
tags: [database, vector, storage, search]
date: 2026-05-23
related:
  - term: "LanceDB"
    file: lancedb.md
    rel: relatedTerm
  - term: "Vector Embedding"
    file: vector-embedding.md
    rel: uses
  - term: "Semantic Search"
    file: semantic-search.md
    rel: relatedTerm
aliases: ["vector store", "embedding store"]
---

**A database purpose-built to store and retrieve high-dimensional numerical vectors using approximate nearest-neighbour algorithms.**

## Definition

A vector database is a data store whose primary index structure is optimised for high-dimensional vector similarity queries, not for exact row lookups or keyword matching. Where a relational database answers "give me all rows where name = 'Alice'", a vector database answers "give me the 5 stored vectors most similar to this query vector".

Most vector databases use approximate nearest-neighbour (ANN) algorithms — such as HNSW or IVF — that trade a small accuracy loss for dramatically faster query times compared to exhaustive brute-force search. They typically support filtering by metadata alongside the vector similarity score.

Vector databases range from fully managed cloud services (Pinecone, Weaviate Cloud) to embedded libraries (LanceDB, ChromaDB) that run in-process with no separate server. This system uses LanceDB because it is embedded and requires no hosted infrastructure.

## Usage in This System

- LanceDB is the vector database implementation in this repository.
- The index lives in `.lancedb/` and is excluded from git.
- The index is rebuilt from pre-computed `.embedding.json` files on every server startup (per W-0100 design).

## Related Terms

- [LanceDB](./lancedb.md)
- [Vector Embedding](./vector-embedding.md)
- [Semantic Search](./semantic-search.md)

## References

1. [LanceDB Documentation](https://lancedb.github.io/lancedb/) — the embedded vector database used in this system.
2. [Vector Database Landscape (2024)](https://tge.ai/vector-database-landscape/) — overview of vector database categories and trade-offs.
