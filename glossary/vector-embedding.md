---
title: "Vector Embedding"
category: concept
tags: [embedding, vector, nlp, representation]
date: 2026-05-23
related:
  - term: "Embedding Model"
    file: embedding-model.md
    rel: uses
  - term: "Semantic Search"
    file: semantic-search.md
    rel: relatedTerm
  - term: "Vector Database"
    file: vector-database.md
    rel: partOf
  - term: "LanceDB"
    file: lancedb.md
    rel: relatedTerm
aliases: ["embedding", "text embedding", "vector representation"]
---

**A fixed-length list of numbers that encodes the meaning of a piece of text so that semantically similar texts produce numerically similar vectors.**

## Definition

A vector embedding is the output of running text through an embedding model: a dense list of floating-point numbers (typically 384 or 1536 dimensions) that represents the semantic content of that text in a high-dimensional space. Two texts that mean similar things will produce vectors that are geometrically close to each other (high cosine similarity), even if the texts share no common words.

Embeddings are what make semantic search possible. Instead of matching keywords, a search engine embeds the query and then finds the stored vectors closest to it — returning documents that are topically related rather than lexically identical.

Once generated, a vector embedding can be stored in a vector database and reused for every future query. Storing embeddings at write time ("pre-computing") avoids the cost of re-embedding all documents on every server startup.

## Usage in This System

- Every `.md` memory file has a corresponding `.embedding.json` file (written at `add_memory` time, per W-0100) containing its pre-computed vector.
- `mcp_server.py` loads these JSON files on startup to populate the LanceDB index without re-embedding from text.
- The embedding model used is `BAAI/bge-small-en-v1.5`, which produces 384-dimensional vectors.

## Related Terms

- [Embedding Model](./embedding-model.md)
- [Semantic Search](./semantic-search.md)
- [Vector Database](./vector-database.md)
- [LanceDB](./lancedb.md)

## References

1. [BAAI/bge-small-en-v1.5 on Hugging Face](https://huggingface.co/BAAI/bge-small-en-v1.5) — the embedding model used in this system.
2. [Sentence Transformers Documentation](https://www.sbert.net/) — the Python library used to run the embedding model.
