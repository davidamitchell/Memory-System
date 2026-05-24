---
title: "LanceDB"
category: tool
tags: [lancedb, vector-database, embedded, search, superseded]
date: 2026-05-23
superseded_by: "_docs/adr/0002-move-from-vector-storage-to-ontology.md"
related:
  - term: "Vector Database"
    file: vector-database.md
  - term: "Vector Embedding"
    file: vector-embedding.md
  - term: "Semantic Search"
    file: semantic-search.md
  - term: "Embedding Model"
    file: embedding-model.md
aliases: []
---

> ⚠️ Superseded by [ADR-0002](../_docs/adr/0002-move-from-vector-storage-to-ontology.md). LanceDB was the original design concept for the retrieval layer of Open-Brain. It was replaced by the ontology-based architecture before full implementation. The legacy prototype (`mcp_server.py`) references LanceDB but is not the system.

**An embedded, serverless vector database that stores and searches high-dimensional numerical vectors, requiring no separate database process.**

## Definition

LanceDB is an open-source vector database built on the Lance columnar data format. Unlike server-based databases that require a separate running process (e.g. Postgres, Pinecone), LanceDB is embedded: it runs in-process and stores its index in a local folder (`.lancedb/`). This makes it well-suited to local-first applications that need semantic search without external infrastructure.

LanceDB stores vectors — numerical representations of text or other data — and retrieves the nearest neighbours to a query vector using approximate nearest-neighbour (ANN) algorithms. The result is semantic search: documents that are conceptually similar to the query are returned, even if they share no exact keywords.

## Usage in This System

LanceDB is **not** the retrieval layer of this system. It was the original design concept; the decision to replace it with an ontology-based knowledge representation is recorded in [ADR-0002](../_docs/adr/0002-move-from-vector-storage-to-ontology.md). The legacy prototype `mcp_server.py` contains LanceDB code but represents the abandoned approach, not the target architecture.

## Related Terms

- [Vector Database](./vector-database.md)
- [Vector Embedding](./vector-embedding.md)
- [Semantic Search](./semantic-search.md)
- [Embedding Model](./embedding-model.md)

## References

1. [LanceDB Documentation](https://lancedb.github.io/lancedb/) — API reference, quickstart, and performance tuning.
2. [ADR-0002](../_docs/adr/0002-move-from-vector-storage-to-ontology.md) — decision to replace LanceDB with ontology-based storage.
