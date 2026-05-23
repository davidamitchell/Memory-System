---
title: "Embedding Model"
category: tool
tags: [embedding, model, nlp, bge, model2vec]
date: 2026-05-23
related:
  - term: "Vector Embedding"
    file: vector-embedding.md
  - term: "Semantic Search"
    file: semantic-search.md
  - term: "LanceDB"
    file: lancedb.md
aliases: ["sentence encoder", "text encoder"]
---

**A machine-learning model that converts text into a fixed-length vector of numbers representing its semantic content.**

## Definition

An embedding model takes a string of text as input and produces a vector embedding as output. The model has learned, from large amounts of training data, to place texts with similar meanings close together in the vector space it outputs. Different models produce vectors of different lengths (dimensionality) and with different trade-offs between accuracy and speed.

Two models are relevant to this system. `BAAI/bge-small-en-v1.5` is a 384-dimension model from the Beijing Academy of Artificial Intelligence, released under the MIT licence. It is the current production model. `Model2Vec` (specifically `potion-base-8M`) is a distillation-based alternative that is roughly 200× faster than comparable models with a modest accuracy trade-off; it is under evaluation in W-0101 as a potential replacement to reduce cold-start latency further.

## Usage in This System

- `BAAI/bge-small-en-v1.5` is loaded via the `sentence-transformers` Python library in `mcp_server.py`.
- `.github/copilot-setup-steps.yml` pre-warms the model by downloading its ~130 MB weights before the Copilot agent starts work, so the first tool call is not blocked by a download.
- The model is kept out of git; only the `.embedding.json` output vectors are committed (per W-0100).

## Related Terms

- [Vector Embedding](./vector-embedding.md)
- [Semantic Search](./semantic-search.md)
- [LanceDB](./lancedb.md)

## References

1. [BAAI/bge-small-en-v1.5 on Hugging Face](https://huggingface.co/BAAI/bge-small-en-v1.5) — model card, benchmarks, and download.
2. [Sentence Transformers](https://www.sbert.net/) — the library used to load and run the model.
3. [Model2Vec](https://github.com/MinishLab/model2vec) — the candidate replacement model under evaluation.
