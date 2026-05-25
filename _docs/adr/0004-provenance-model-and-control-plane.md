# 0004 — Provenance model, control plane, and architectural principles

Date: 2026-05-23
Status: accepted
Supersedes: [0003-ontology-architecture.md](./0003-ontology-architecture.md)

## Context

[ADR-0003](./0003-ontology-architecture.md) established the two-tier ontology shape (upper/lower), the document model (raw → prepared → domain), and an 11-processor pipeline. Three gaps were identified after review:

1. **No governing principles** — the pipeline had no explicit constraints on immutability, provenance, or reproducibility. Without these, implementations could diverge silently.
2. **No provenance model** — assertions in the ontology had no formal link back to the source evidence that supports them. This made auditability and rollback incomplete.
3. **No control plane** — state transitions (version commits, upper ontology mutations, rollbacks) had no explicit governance layer distinct from the data pipeline.

A fourth refinement arose from the provenance requirement: document segments, not whole documents, are the right granularity for evidence references. A **Prepared Segment** — an immutable, content-addressed fragment — enables precise, stable provenance links.

This ADR supersedes ADR-0003. The design is still at the conceptual level; library and deployment choices are deferred.

## Decision

### 1. Six architectural principles

These are binding constraints on all processors, storage, and control decisions:

| Principle | Constraint |
|---|---|
| **Immutable Source Fidelity** | Raw source artefacts are stored verbatim and never modified |
| **Deterministic Transformation** | Every derived artefact is reproducible from source + processor version |
| **Assertion Provenance** | Every accepted ontology assertion must resolve to at least one supporting Prepared Segment |
| **Control/Data Separation** | Transformation processors (data plane) are distinct from governance and version control (control plane) |
| **Upper Ontology Stability** | Upper ontology mutations require explicit alignment governance acceptance |
| **Bidirectional Traceability** | Concepts resolve to source evidence; source evidence resolves to derived assertions |

### 2. Refined document model

One new component is added to the document layer:

| Component | Description |
|---|---|
| **Prepared Segment** | Immutable, content-addressed fragment of a Prepared Document. The atomic unit of evidence for assertion provenance. Identified by a content hash (SHA-256 URI scheme) |

### 3. Provenance layer

Four new components track assertion lineage:

| Component | Description |
|---|---|
| **Extraction Activity** | A recorded execution instance of a Concept Extraction Processor that produced a set of candidate assertions |
| **Processor Version** | The versioned identity of a processor (name + semver), recorded on every Extraction Activity |
| **Assertion Lineage** | The supersession and invalidation history of an Assertion Node across ontology versions |
| **Trust Metadata** | Attached to a Document Source or Prepared Document. Fields: `source_authority` (authoritative / secondary / inferred / unknown), `freshness_date` (ISO-8601), `approval_state` (pending / accepted / rejected). Confidence weighting is deferred — see Open Questions |

Assertions are linked to evidence via the following pattern:

```turtle
@prefix ex:   <https://memory.example.org/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# An accepted assertion in the domain ontology
ex:assertion/001
    a ex:AssertionNode ;
    ex:claim "LanceDB is an embedded vector database" ;
    ex:confidence "0.92"^^xsd:decimal ;
    ex:evidencedBy ex:segment/abc123 ;
    prov:wasGeneratedBy ex:activity/extract-2026-05-23-001 .

# The extraction run that produced this assertion
ex:activity/extract-2026-05-23-001
    a ex:ExtractionActivity ;
    prov:used ex:segment/abc123 ;
    prov:wasAssociatedWith ex:processor/concept-extractor-v1.2.0 ;
    prov:endedAtTime "2026-05-23T04:00:00Z"^^xsd:dateTime .

# The content-addressed segment that evidences the assertion
ex:segment/abc123
    a ex:PreparedSegment ;
    ex:contentHash "sha256:e3b0c44298fc1c149afbf4c8996fb924..." ;
    ex:sourceDocument ex:doc/lancedb-overview-2026 .
```

### 4. Control plane

Five controls govern ontology state transitions. They are distinct from data processors:

| Control | Responsibility |
|---|---|
| **Validation Gate** | Blocks promotion of any graph state that fails consistency validation |
| **Alignment Governance** | Reviews and accepts or rejects proposed upper ontology mutations |
| **Version Commit Gate** | Commits a validated, approved ontology state as a new immutable version |
| **Rollback Controller** | Reverts the active ontology pointer to a prior version; does not delete history |
| **Invalidation Controller** | Marks Assertion Nodes as superseded when contradicting evidence is accepted |

### 5. Refined processing pipeline

The pipeline is extended to 12 processors. Naming is aligned with the document model above:

| # | Processor | Input | Output | Responsibility |
|---|---|---|---|---|
| 1 | **Sourcing Processor** | Document Source | Raw Document | Capture immutable source verbatim |
| 2 | **Preparation Processor** | Raw Document | Prepared Document | Clean and normalise content |
| 3 | **Segmentation Processor** | Prepared Document | Prepared Segments | Split into content-addressed, immutable fragments |
| 4 | **Metadata Processor** | Source + Prepared Document | Metadata Envelope | Attach retrieval, lineage, and trust metadata |
| 5 | **Domain Classification Processor** | Prepared Document | Domain Signals | Candidate domain labels from content analysis |
| 6 | **Domain Matching Processor** | Domain Signals | Domain Document | Map candidates to canonical upper ontology domains |
| 7 | **Concept Extraction Processor** | Domain Document + Segments | Ontology Delta Proposal + Extraction Activity | Extract candidate assertions with segment evidence |
| 8 | **Ontology Build Processor** | Delta Proposal | Candidate Domain Updates | Construct or update domain ontology graph |
| 9 | **Consistency Validation Processor** | Candidate Updates | Validation Report | Detect contradictions, circular definitions, collisions |
| 10 | **Reconciliation Processor** | Validation Conflicts | Canonical Merge Resolution | Resolve semantic conflicts; feed Alignment Governance for upper ontology changes |
| 11 | **Version Commit Processor** | Validated Graph State | Versioned Ontology | Tag, diff, and commit an immutable snapshot |
| 12 | **Export Processor** | Versioned Ontology | OWL / RDF-Turtle / JSON-LD | Serialise for external tooling and archival |

### 6. Storage layer

Three logical stores (physical implementation deferred):

| Component | Description |
|---|---|
| **Document Store** | Object storage for raw and prepared artefacts and segments |
| **Ontology Store** | Graph store for current ontology state (triple store or property graph) |
| **Resolver Service** | Maps content-addressed URIs (`sha256:...`) to physical storage locations. Implemented as a library function in the first iteration |

## Consequences

- All processors must record their version and execution context as an Extraction Activity
- Segments are the minimum addressable unit; whole documents are no longer sufficient as evidence references
- Upper ontology changes require Alignment Governance review — this introduces a human (or governed automated) gate
- Rollback is always safe: history is append-only, the active pointer is the only mutable state
- The provenance Turtle pattern above is the target assertion format; it can be extended but not simplified away
- The design document (`_docs/design/ontology-system-design.md`) is updated to v2 reflecting these changes

## Open Questions

- [ ] What is the confidence weighting model for Trust Metadata — numeric score, tier-based, or rule-derived?
- [ ] Is Alignment Governance a human approval gate, an automated consistency check, or both in different contexts?
- [ ] How does rollback propagate when downstream domain ontologies depend on an upper ontology version being rolled back?
- [ ] What triggers a Version Commit — every ingest, a scheduled batch, or a manual gate?
- [ ] Can a document span multiple domains, and if so, how are conflicting domain assignments resolved?
- [ ] How is the upper ontology seeded — manually authored, bootstrapped from BFO/SUMO/schema.org, or hybrid?

## References

1. [`_docs/adr/0003-ontology-architecture.md`](./0003-ontology-architecture.md) — superseded; established the foundation this ADR builds on
2. [`_docs/adr/0002-move-from-vector-storage-to-ontology.md`](./0002-move-from-vector-storage-to-ontology.md) — established the direction
3. [`_docs/design/ontology-system-design.md`](../design/ontology-system-design.md) — updated component and sequence diagrams
4. [W3C PROV-O](https://www.w3.org/TR/prov-o/) — the provenance ontology used in the Turtle pattern
5. [Basic Formal Ontology (BFO)](https://basic-formal-ontology.org/) — reference upper ontology pattern
6. [OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-overview/) — target serialisation standard
