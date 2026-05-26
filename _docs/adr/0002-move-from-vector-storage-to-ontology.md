# 0002 — Move from vector storage to ontology-based knowledge representation

Date: 2026-05-23
Status: accepted

## Context

The initial architecture of this [memory system](../../glossary/open-brain.md) used [LanceDB](../../glossary/lancedb.md) as an embedded [vector database](../../glossary/vector-database.md) for [semantic search](../../glossary/semantic-search.md). Documents were embedded using [`BAAI/bge-small-en-v1.5`](../../glossary/embedding-model.md) and stored as dense [vector embeddings](../../glossary/vector-embedding.md). Retrieval was purely similarity-based with no structured representation of concepts, relationships, or domains.

While this approach provided fast keyword-proximity search, it lacked:

- Explicit representation of **concepts** and their **relationships**
- **Domain scoping** — the ability to retrieve knowledge within a defined domain boundary
- **Versioning** of the knowledge structure itself
- **Reasoning** — the ability to infer new knowledge from existing relationships
- **Auditability** — clear lineage between source documents and derived knowledge

The decision was made to move toward an **ontology-based** representation, where knowledge is structured as a graph of concepts, properties, and relationships — enabling richer retrieval, domain-scoped queries, and versionable knowledge artefacts.

## Decision

Replace [LanceDB](../../glossary/lancedb.md) vector storage as the primary knowledge representation layer with an ontology-based architecture consisting of:

1. An **upper ontology** — a domain-agnostic taxonomy of all domains known to the system
2. A set of **lower (domain) ontologies** — per-domain concept graphs derived from source documents
3. A **document processing pipeline** — a set of processors that extract, clean, enrich, and transform source documents into ontological concepts

Vector embeddings may still be used as an implementation detail within individual processors (e.g., concept clustering) but are no longer the primary retrieval and storage mechanism.

## Consequences

- The `mcp_server.py` [MCP server](../../glossary/mcp-server.md) will be redesigned to query the ontology rather than a vector index
- `requirements.txt` will be updated to remove LanceDB/sentence-transformer dependencies and add ontology tooling
- `copilot-setup-steps.yml` will be updated to remove the embedding model pre-warm step
- The README.md, `copilot-instructions.md`, and all glossary terms referencing the vector layer will be updated
- A new design space (`_docs/design/`) documents the target architecture
- This is a breaking change to the storage layer; existing `.lancedb/` folders can be discarded

## References

1. [`_docs/adr/0003-ontology-architecture.md`](./0003-ontology-architecture.md) — the architectural detail of the upper/lower ontology design
2. [`_docs/design/ontology-system-design.md`](../design/ontology-system-design.md) — component and sequence diagrams for the new architecture
3. [`_docs/adr/README.md`](./README.md) — index of all ADRs in this repository
