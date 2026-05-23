# 0003 — Ontology architecture: upper ontology, lower ontologies, and the document processing pipeline

Date: 2026-05-23
Status: accepted

## Context

Following ADR-0002 (move from vector storage to ontology), the system requires a concrete architecture for how ontologies are built, structured, versioned, and queried.

The core design questions are:

1. What is the **shape** of the ontology (upper vs lower; domain scoping)?
2. What **document types** are in scope?
3. What **processing steps** transform raw documents into ontological knowledge?
4. How is the ontology **versioned** so changes are auditable and reversible?
5. What additional processors are needed beyond the obvious ones?

## Decision

### Ontology Shape

Adopt a **two-tier ontology**:

| Tier | Name | Scope |
|------|------|-------|
| Upper | **Upper Ontology** | Domain-agnostic taxonomy; enumerates and relates all recognised domains |
| Lower | **Lower Ontology** (set of Domain Ontologies) | Per-domain concept graphs; each scoped to one domain from the upper ontology |

This mirrors the [BFO](https://basic-formal-ontology.org/) / [SUMO](https://www.ontologyportal.org/) pattern and is well-suited to a multi-domain memory system.

### Document Model

Three document layers:

| Layer | Name | Description |
|-------|------|-------------|
| Source | **Sourced Document (Raw)** | Verbatim copy from the source; never modified |
| Prepared | **Sourced Document (Prepared)** | Cleaned, stripped of markup/images/non-readable chars; enriched with metadata (source, retrieval time, method, MIME type, lineage, tags) |
| Scoped | **Domain Document** | A prepared document assigned to one or more domain buckets |

### Processing Pipeline

Eight processor types:

| # | Processor | Input → Output |
|---|-----------|----------------|
| 1 | **Sourcing** | Document Source → Sourced Document (Raw) |
| 2 | **Cleaning** | Raw → Prepared (strip markup, images, non-text) |
| 3 | **Metadata** | Prepared + source context → enriched Prepared (MIME type, lineage, retrieval time, tags) |
| 4 | **Domain Extraction** | Prepared → domain signals (candidate domain labels) |
| 5 | **Domain Matching** | Domain signals → Domain Document (assignment to upper ontology domain) |
| 6 | **Concept Extraction** | Domain Document → concepts + relationships (entities, properties, axioms) |
| 7 | **Ontology Build** | Concepts + relationships → Domain Ontology (lower); merges into Upper Ontology |
| 8 | **Ontology Versioning** | Ontology snapshot → versioned artefact (diff, changelog, rollback pointer) |

Three additional processors needed to complete a production-grade versionable ontology:

| # | Processor | Rationale |
|---|-----------|-----------|
| 9 | **Consistency Validation** | Checks for contradictions, circular definitions, and broken axioms across domain ontologies before a version is committed |
| 10 | **Ontology Merge / Reconciliation** | Resolves concept collisions when two domain ontologies claim the same term with different definitions; produces a canonical merged representation in the upper ontology |
| 11 | **Export / Serialisation** | Converts the internal ontology representation to standard interchange formats (OWL, RDF/Turtle, JSON-LD) for downstream tools and long-term archival |

### Versioning Strategy

- Each committed ontology snapshot is tagged with a semantic version (`major.minor.patch`)
- Diffs are stored as human-readable changelogs alongside the ontology artefact
- Rollback is by pointer — the prior snapshot is never deleted (append-only, same philosophy as `PROGRESS.md`)

## Consequences

- A new `docs/design/` folder documents the full component and sequence diagrams
- The processor pipeline is the primary unit of testability and extension
- Ontology versioning satisfies the audit/lineage requirements that vector storage could not meet
- Export/serialisation enables interoperability with standard ontology tooling (Protégé, SPARQL endpoints)
- Consistency validation prevents silent corruption of the knowledge graph as new documents are sourced

## References

1. [`docs/adr/0002-move-from-vector-storage-to-ontology.md`](./0002-move-from-vector-storage-to-ontology.md) — the parent decision establishing why we moved to ontologies
2. [`docs/design/ontology-system-design.md`](../design/ontology-system-design.md) — component diagram and sequence diagram for this architecture
3. [`docs/adr/README.md`](./README.md) — index of all ADRs in this repository
4. [Basic Formal Ontology (BFO)](https://basic-formal-ontology.org/) — reference upper ontology pattern
5. [OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-overview/) — target serialisation format
