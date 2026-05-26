---
title: "Embedding Model"
category: tool
tags: [embedding, model, nlp, superseded]
date: 2026-05-23
superseded_by: "glossary/knowledge-graph.md"
related:
  - term: "Vector Embedding"
    file: vector-embedding.md
    rel: uses
  - term: "Semantic Search"
    file: semantic-search.md
    rel: relatedTerm
  - term: "LanceDB"
    file: lancedb.md
    rel: relatedTerm
aliases: ["sentence encoder", "text encoder"]
---

> ⚠️ Embedding models were part of the original vector-storage design concept for Open-Brain. That approach was replaced by the ontology-based architecture before full implementation. See [ADR-0002](../_docs/adr/0002-move-from-vector-storage-to-ontology.md). Embedding models are **not** used in the current system.

**A machine-learning model that converts text into a fixed-length vector of numbers representing its semantic content.**

## Definition

An embedding model takes a string of text as input and produces a vector embedding as output. The model has learned, from large amounts of training data, to place texts with similar meanings close together in the vector space it outputs. Different models produce vectors of different lengths (dimensionality) and with different trade-offs between accuracy and speed.

In the original Open-Brain design, `BAAI/bge-small-en-v1.5` (a 384-dimension model from the Beijing Academy of Artificial Intelligence) was selected as the embedding model for LanceDB-backed semantic search. `Model2Vec` (`potion-base-8M`) was under evaluation as a faster alternative. Neither is used in the current ontology-based system.

## Usage in This System

Embedding models are **not** used in this system. The legacy prototype `mcp_server.py` references `BAAI/bge-small-en-v1.5` via `sentence-transformers`, but this code is from the superseded design. The `.github/copilot-setup-steps.yml` no longer pre-warms any embedding model.

## Related Terms

- [Vector Embedding](./vector-embedding.md)
- [Semantic Search](./semantic-search.md)
- [LanceDB](./lancedb.md)

## References

1. [ADR-0002](../_docs/adr/0002-move-from-vector-storage-to-ontology.md) — decision to replace the vector/embedding approach with ontology-based knowledge representation.
2. [BAAI/bge-small-en-v1.5 on Hugging Face](https://huggingface.co/BAAI/bge-small-en-v1.5) — the model that was selected for the superseded design.
