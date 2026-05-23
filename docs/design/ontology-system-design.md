# Ontology-Based Memory System — Design

**Status:** draft
**Version:** 3
**Date:** 2026-05-23
**Supersedes:** v1 (initial design, same file)
**Related ADRs:** [ADR-0002](../adr/0002-move-from-vector-storage-to-ontology.md) · [ADR-0004](../adr/0004-provenance-model-and-control-plane.md)

---

## 1. Purpose

This document describes the conceptual architecture for the ontology-based [Memory System](../../README.md). It covers the key components, the processing pipeline that transforms raw documents into versioned ontologies, and the relationships between them.

This is a **design-space document** — it operates in the conceptual plane. Implementation details (specific libraries, file formats, API contracts) are deferred to implementation ADRs.

---

## 2. Architectural Principles

Six constraints govern all design decisions. See [ADR-0004](../adr/0004-provenance-model-and-control-plane.md) for rationale.

| Principle | Constraint |
|-----------|-----------|
| **Immutable Source Fidelity** | Raw source artefacts are stored verbatim and never modified |
| **Deterministic Transformation** | Every derived artefact is reproducible from source + processor version |
| **Assertion Provenance** | Every accepted ontology assertion must resolve to at least one supporting Prepared Segment |
| **Control/Data Separation** | Transformation processors (data plane) are distinct from governance and version control (control plane) |
| **Upper Ontology Stability** | Upper ontology mutations require explicit alignment governance acceptance |
| **Bidirectional Traceability** | Concepts resolve to source evidence; source evidence resolves to derived assertions |

---

## 3. Architectural Components

### 3.1 Document Layer

| Component | Description |
|-----------|-------------|
| **Document** | Any information artefact in scope — structured (tables, schemas), semi-structured (Markdown, HTML), or lexical (plain prose) |
| **Document Source** | External origin: URL, API, filesystem path, feed, database export |
| **Raw Document** | Immutable verbatim capture of the source artefact — never modified after capture |
| **Prepared Document** | Canonical cleaned representation with structured metadata attached |
| **Prepared Segment** | Immutable, content-addressed fragment of a Prepared Document. Identified by a SHA-256 content URI. The atomic unit of evidence for assertion provenance |
| **Domain Document** | A prepared document assigned to one or more domains in the upper ontology |

### 3.2 Ontology Layer

| Component | Description |
|-----------|-------------|
| **Upper Ontology** | Stable domain taxonomy and alignment model. Mutates only through governed acceptance |
| **Domain Ontology** | Domain-scoped concept graph; the lower ontology tier |
| **Lower Ontology** | The collective set of all domain ontologies |
| **Ontology Delta Proposal** | Candidate assertions produced by extraction — not yet accepted into the graph |
| **Assertion Node** | An accepted ontology fact with confidence score and provenance links |
| **Versioned Ontology** | Immutable snapshot of the ontology at a point in time, tagged with a semantic version, carrying a semantic diff and rollback pointer |

### 3.3 Provenance Layer

| Component | Description |
|-----------|-------------|
| **Extraction Activity** | Recorded execution of a Concept Extraction Processor that produced a set of candidate assertions |
| **Processor Version** | Versioned identity (name + semver) recorded on every Extraction Activity |
| **Assertion Lineage** | Supersession and invalidation history of an Assertion Node across versions |
| **Trust Metadata** | Attached to a Document Source or Prepared Document: `source_authority` (authoritative / secondary / inferred / unknown), `freshness_date` (ISO-8601), `approval_state` (pending / accepted / rejected) |

### 3.4 Storage Layer

| Component | Description |
|-----------|-------------|
| **Document Store** | Object storage for raw artefacts, prepared documents, and segments |
| **Ontology Store** | Graph store for current ontology state (triple store or property graph — deferred) |
| **Resolver Service** | Maps content-addressed URIs (`sha256:…`) to physical storage locations |

---

## 4. Processing Architecture

### 4.1 Data Plane — Processors

Processors transform artefacts. Each has a defined input, output, and sole responsibility.

| # | Processor | Input | Output | Responsibility |
|---|-----------|-------|--------|----------------|
| 1 | **Sourcing Processor** | Document Source | Raw Document | Capture immutable source verbatim |
| 2 | **Preparation Processor** | Raw Document | Prepared Document | Clean and normalise content |
| 3 | **Segmentation Processor** | Prepared Document | Prepared Segments | Split into content-addressed, immutable fragments |
| 4 | **Metadata Processor** | Source + Prepared Document | Metadata Envelope | Attach retrieval, lineage, and trust metadata |
| 5 | **Domain Classification Processor** | Prepared Document | Domain Signals | Candidate domain labels from content analysis |
| 6 | **Domain Matching Processor** | Domain Signals | Domain Document | Map candidates to canonical upper ontology domains |
| 7 | **Concept Extraction Processor** | Domain Document + Segments | Delta Proposal + Extraction Activity | Extract candidate assertions with segment evidence links |
| 8 | **Ontology Build Processor** | Delta Proposal | Candidate Domain Updates | Construct or update domain ontology graph |
| 9 | **Consistency Validation Processor** | Candidate Updates | Validation Report | Detect contradictions, circular definitions, collisions |
| 10 | **Reconciliation Processor** | Validation Conflicts | Canonical Merge Resolution | Resolve semantic conflicts; route upper ontology changes to Alignment Governance |
| 11 | **Version Commit Processor** | Validated Graph State | Versioned Ontology | Tag, diff, and commit an immutable snapshot |
| 12 | **Export Processor** | Versioned Ontology | OWL / RDF-Turtle / JSON-LD | Serialise for external tooling and archival |

### 4.2 Control Plane

Controls govern state transitions. They are distinct from data processors.

| Control | Responsibility |
|---------|----------------|
| **Validation Gate** | Blocks promotion of any graph state that fails consistency validation |
| **Alignment Governance** | Reviews and accepts or rejects proposed upper ontology mutations |
| **Version Commit Gate** | Commits a validated, approved graph state as a new immutable version |
| **Rollback Controller** | Reverts the active ontology pointer to a prior version; does not delete history |
| **Invalidation Controller** | Marks Assertion Nodes as superseded when contradicting evidence is accepted |

---

## 5. Component Diagram

```mermaid
graph TD
    subgraph Sources
        DS[Document Sources]
    end

    subgraph Doc_Layer["Document Layer"]
        RAW[Raw Document]
        PREP[Prepared Document]
        SEG[Prepared Segments]
        DD[Domain Document]
    end

    subgraph Prov_Layer["Provenance Layer"]
        EA[Extraction Activity]
        PV[Processor Version]
        AL[Assertion Lineage]
    end

    subgraph Ont_Layer["Ontology Layer"]
        DP[Delta Proposal]
        AN[Assertion Nodes]
        DO[Domain Ontologies]
        UO[Upper Ontology]
        VO[Versioned Ontology]
    end

    subgraph Store["Storage Layer"]
        DSTORE[Document Store]
        OSTORE[Ontology Store]
        RS[Resolver Service]
    end

    subgraph Control["Control Plane"]
        VG[Validation Gate]
        AG[Alignment Governance]
        VCG[Version Commit Gate]
        RC[Rollback Controller]
        IC[Invalidation Controller]
    end

    subgraph Pipeline["Data Plane — Processors"]
        P1[1 Sourcing]
        P2[2 Preparation]
        P3[3 Segmentation]
        P4[4 Metadata]
        P5[5 Domain Classification]
        P6[6 Domain Matching]
        P7[7 Concept Extraction]
        P8[8 Ontology Build]
        P9[9 Consistency Validation]
        P10[10 Reconciliation]
        P11[11 Version Commit]
        P12[12 Export]
    end

    DS --> P1 --> RAW
    RAW --> P2 --> PREP
    PREP --> P3 --> SEG
    PREP --> P4
    P4 --> DSTORE
    SEG --> DSTORE
    SEG --> RS

    PREP --> P5 --> P6 --> DD
    DD --> P7
    SEG --> P7
    P7 --> DP
    P7 --> EA
    EA --> PV

    DP --> P8 --> P9
    P9 --> VG
    VG -->|pass| P10
    VG -->|fail| P9
    P10 -->|upper changes| AG
    AG -->|accepted| AN
    AN --> DO
    AN --> UO
    AN --> AL

    DO --> P11
    UO --> P11
    P11 --> VCG --> VO
    VO --> OSTORE
    VO --> P12

    RC -.->|repoint| OSTORE
    IC -.->|supersede| AL
```

---

## 6. Sequence Diagram

End-to-end flow for ingesting a single document.

```mermaid
sequenceDiagram
    autonumber
    actor Trigger as Trigger / Scheduler
    participant P1 as Sourcing
    participant P2 as Preparation
    participant P3 as Segmentation
    participant P4 as Metadata
    participant P5 as Domain Classification
    participant P6 as Domain Matching
    participant P7 as Concept Extraction
    participant P8 as Ontology Build
    participant P9 as Consistency Validation
    participant P10 as Reconciliation
    participant CP as Control Plane
    participant P11 as Version Commit
    participant P12 as Export
    participant Store as Storage

    Trigger->>P1: ingest(source)
    P1->>Store: store Raw Document

    P1->>P2: raw document
    P2->>P3: prepared document
    P3->>Store: store Prepared Segments (content-addressed)
    P2->>P4: prepared document
    P4->>Store: attach Trust Metadata

    P3->>P5: prepared document
    P5->>P6: domain signals
    P6->>Store: store Domain Document

    P6->>P7: domain document + segments
    P7->>Store: record Extraction Activity (processor version, segments used)
    P7->>P8: Delta Proposal

    P8->>P9: candidate graph updates
    P9->>CP: validation report

    alt conflicts detected
        CP->>P10: route conflicts to Reconciliation
        P10->>CP: canonical resolution
        CP-->>CP: upper ontology changes → Alignment Governance review
    end

    CP->>P11: validated + approved state
    P11->>Store: commit Versioned Ontology (semver tag + diff + rollback pointer)

    P11->>P12: versioned ontology
    P12->>Store: write OWL / RDF / JSON-LD artefact
```

---

## 7. Provenance Example

An assertion in the ontology links back through an Extraction Activity to the Prepared Segment that evidences it.

```turtle
@prefix ex:   <https://memory.example.org/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

ex:assertion/001
    a ex:AssertionNode ;
    ex:claim "LanceDB is an embedded vector database" ;
    ex:confidence "0.92"^^xsd:decimal ;
    ex:evidencedBy ex:segment/abc123 ;
    prov:wasGeneratedBy ex:activity/extract-2026-05-23-001 .

ex:activity/extract-2026-05-23-001
    a ex:ExtractionActivity ;
    prov:used ex:segment/abc123 ;
    prov:wasAssociatedWith ex:processor/concept-extractor-v1.2.0 ;
    prov:endedAtTime "2026-05-23T04:00:00Z"^^xsd:dateTime .

ex:segment/abc123
    a ex:PreparedSegment ;
    ex:contentHash "sha256:e3b0c44298fc1c149afbf4c8996fb924..." ;
    ex:sourceDocument ex:doc/lancedb-overview-2026 .
```

---

## 9. Target State and Proposed Extraction Phases

> **These phases are proposals — descriptive, not prescriptive.** They describe a plausible route from the current state to the target state. Sequence, scope, and naming will evolve as the work proceeds.

### 9.1 Target State

The pipeline should be able to ingest an arbitrary unstructured prose document and produce a well-formed, versioned, provenance-traced ontology contribution that includes:

| Capability | Description |
|-----------|-------------|
| **Named entity extraction** | Concepts and classes identified from prose without hand-authored front-matter |
| **Alias / synonym grouping** | Multiple surface forms of the same concept collapsed to a canonical node |
| **Typed relation extraction** | Directed, labelled predicates between concepts (e.g. `partOf`, `causedBy`, `instanceOf`, `precedes`) rather than undifferentiated `relatedTerm` |
| **Taxonomic hierarchy** | `subClassOf` / `rdf:type` edges enabling is-a reasoning; not just associative links |
| **Confidence-weighted assertions** | Every extracted assertion carries a confidence score derived from extraction method and source authority |
| **Full provenance tracing** | Every node resolves to the segment(s) that evidenced it; every segment resolves to its source document |
| **Consistency validation** | Contradictions and collisions are detected before any version is committed |
| **Evaluable output** | Extraction quality can be measured against a known-good ground truth corpus |

The pipeline's processor interface (`delta_proposal` dict in / versioned Turtle out) is stable across all phases. Each phase improves the quality and coverage of what p07 (Concept Extraction) produces, without changing what p08–p12 consume.

---

### 9.2 Current State (as of W-0201)

The pipeline is end-to-end and produces correct, provenance-traced Turtle. Extraction is **rule-based**: it reads explicitly declared fields from YAML front-matter. This works perfectly for the glossary corpus (structured, hand-authored) and provides a verifiable ground truth for evaluating future extraction strategies.

Gaps relative to target state:
- No NLP preprocessing (no tokenisation, POS tagging, NER, or dependency parsing)
- Concepts and relations are explicitly declared, not inferred from prose
- All relations are untyped (`ms:relatedTerm`)
- No taxonomic hierarchy (`subClassOf` is absent)
- No extraction quality evaluation framework

---

### 9.3 Proposed Phases

#### Phase 0 — Structured extraction (complete)
*Single glossary file → end-to-end pipeline → queryable concept card.*
All 12 processors wired. Ground truth established. The glossary corpus forms the evaluation baseline for all future phases.

#### Phase 1 — Full structured corpus (current)
*All 26 glossary files → full graph → traversable concept neighbourhood.*
Multi-file merging, graph traversal queries, ~80 typed `relatedTerm` edges. The first real graph, not a toy.

#### Phase 2 — Evaluation harness
*Measure what the pipeline extracts against what it should extract.*
Define precision/recall metrics for concept extraction, alias grouping, and relation extraction. Run the existing rule-based extractor against the glossary corpus and record the baseline scores. This harness is the gate for all subsequent phases: every new extraction strategy is only accepted if it meets or exceeds baseline on the structured corpus.

#### Phase 3 — LLM-based concept extraction (prose, single document)
*Swap p07 for a prompt-based extractor on one unstructured research document.*
The extractor produces the same `delta_proposal` dict shape; p08–p12 are unchanged. Evaluate output against the Phase 2 harness (using the glossary as proxy ground truth). First evidence that latent extraction is viable on this architecture.

#### Phase 4 — NLP enrichment layer
*Add tokenisation, POS tagging, and NER as an enrichment step in p02.*
Feeds richer signal (named entity spans, dependency parses) to p07. Evaluate whether NLP preprocessing improves extraction quality over Phase 3 baseline. spaCy or equivalent; no model training required at this phase.

#### Phase 5 — Typed relation extraction
*Extend `delta_proposal` to carry typed predicates.*
Move from `ms:relatedTerm` (undifferentiated) to labelled relations (e.g. `ms:partOf`, `ms:causedBy`, `ms:instanceOf`). A minimal relation type vocabulary is defined in the upper ontology. Evaluate: does typed extraction on the glossary corpus recover the implicit relation types that the hand-authored `related:` fields imply?

#### Phase 6 — Taxonomy induction
*Introduce `subClassOf` / `rdf:type` hierarchy.*
Extracted concepts are assigned to class nodes, not just a flat assertion list. Enables is-a reasoning and aligns with OWL semantics. Evaluated against a small set of known hierarchical relationships in the glossary (e.g. `VectorEmbedding subClassOf Representation`).

#### Phase 7 — Confidence weighting and Trust Metadata
*Attach numeric confidence scores to extracted assertions.*
Score derives from extraction method (rule-based > LLM-certain > LLM-uncertain), source authority, and segment evidence count. Consistency validation and reconciliation processors use scores to rank competing assertions. Evaluated: does the confidence model correctly rank assertions from authoritative vs inferred sources?

---

## 8. Open Questions

- [ ] What is the confidence weighting model for Trust Metadata — numeric score, tier-based, or rule-derived?
- [ ] Is Alignment Governance a human approval gate, an automated check, or context-dependent?
- [ ] How does rollback propagate when domain ontologies depend on an upper ontology version being rolled back?
- [ ] What triggers a Version Commit — every ingest, scheduled batch, or manual gate?
- [ ] Can a document span multiple domains, and if so, how are conflicting domain assignments resolved?
- [ ] How is the upper ontology seeded — manually authored, bootstrapped from BFO/SUMO/schema.org, or hybrid?
- [ ] What is the internal representation format before serialisation (RDF graph, property graph, custom AST)?

---

## References

1. [ADR-0002 — Move from vector storage to ontology](../adr/0002-move-from-vector-storage-to-ontology.md)
2. [ADR-0004 — Provenance model and control plane](../adr/0004-provenance-model-and-control-plane.md)
3. [W3C PROV-O](https://www.w3.org/TR/prov-o/) — provenance ontology used in the example
4. [Basic Formal Ontology (BFO)](https://basic-formal-ontology.org/) — reference upper ontology
5. [OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-overview/) — target serialisation standard
6. [Mermaid — diagram-as-code](https://mermaid.js.org/) — diagramming syntax used above
7. [BACKLOG.md W-0203–W-0206](../../BACKLOG.md) — implementation items for latent extraction phases

