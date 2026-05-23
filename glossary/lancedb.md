---
title: "LanceDB"
category: tool
tags: [lancedb, vector-database, embedded, search]
date: 2026-05-23
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

**An embedded, serverless vector database that stores and searches high-dimensional numerical vectors, requiring no separate database process.**

## Definition

LanceDB is an open-source vector database built on the Lance columnar data format. Unlike server-based databases that require a separate running process (e.g. Postgres, Pinecone), LanceDB is embedded: it runs in-process and stores its index in a local folder (`.lancedb/`). This makes it well-suited to local-first applications that need semantic search without external infrastructure.

LanceDB stores vectors — numerical representations of text or other data — and retrieves the nearest neighbours to a query vector using approximate nearest-neighbour (ANN) algorithms. The result is semantic search: documents that are conceptually similar to the query are returned, even if they share no exact keywords.

Because the `.lancedb/` folder is a regular directory of files, it can be excluded from git and rebuilt from source data on any machine without a migration step.

## Usage in This System

- The `.lancedb/` folder lives locally and is excluded from git (listed in `.gitignore`).
- `mcp_server.py` maintains the LanceDB index: it embeds every `.md` file using the embedding model and stores the vectors in `.lancedb/`.
- On every `search_brain` call, `mcp_server.py` queries LanceDB with the embedded query and returns the nearest memory files.
- W-0100 in `BACKLOG-v2.md` addresses cold-start latency by pre-computing embeddings at write time so the index can be rebuilt from JSON files rather than re-embedding all text on startup.

## Related Terms

- [Vector Database](./vector-database.md)
- [Vector Embedding](./vector-embedding.md)
- [Semantic Search](./semantic-search.md)
- [Embedding Model](./embedding-model.md)

## References

1. [LanceDB Documentation](https://lancedb.github.io/lancedb/) — API reference, quickstart, and performance tuning.
2. [Lance Data Format](https://lancedb.github.io/lance/) — the underlying columnar format used by LanceDB.
