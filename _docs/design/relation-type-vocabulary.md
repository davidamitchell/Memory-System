# Relation Type Vocabulary

**Status:** Active (W-0206)  
**Date:** 2026-05-26

---

## Overview

The pipeline extracts typed predicates between concepts. This document defines the minimal relation type vocabulary used in the `ms:` namespace. Each typed predicate has stronger semantics than the untyped `ms:relatedTerm` catch-all and enables reasoning, query precision, and eventual alignment with upper ontologies (BFO, schema.org).

The vocabulary is intentionally small. Six types plus a catch-all cover the relations that appear in the foundational concepts corpus. It will grow as new relation patterns are encountered and annotated.

---

## Relation Types

| Predicate | URI | Direction | Meaning |
|---|---|---|---|
| `relatedTerm` | `ms:relatedTerm` | undirected (symmetric) | Generic association. Use when no typed predicate applies. |
| `contrasts` | `ms:contrasts` | A contrasts B | A is explicitly distinguished from B. Commonly confused or adjacent concepts that must be kept apart. |
| `uses` | `ms:uses` | A uses B | A instrumentally employs B in its operation, structure, or definition. B is a dependency of A. |
| `partOf` | `ms:partOf` | A partOf B | A is a structural component or constituent part of B. B is the containing whole. |
| `instanceOf` | `ms:instanceOf` | A instanceOf B | A is a specific instance, token, or example of type B. B is the type, A is a member of its extension. |
| `implements` | `ms:implements` | A implements B | A is the formal or operational realisation of B. A makes concrete or machine-processable what B defines abstractly. |

---

## Selection Criteria

**`contrasts`** is appropriate when two concepts are:
- Explicitly compared in a "Distinguished From" table, or
- Commonly conflated (their distinction is load-bearing for the domain).

**`uses`** is appropriate when A's definition or operation requires B:
- "A consists of B and C" → A uses B, A uses C
- "A is processed using B" → A uses B
- "A's definition refers to B as an instrument" → A uses B

**`partOf`** is appropriate when A is a constituent part of B's structure:
- "A graph consists of nodes and edges" → node partOf graph, edge partOf graph
- A is one element in B's composition, not just a dependency

**`instanceOf`** is appropriate when A is a token/individual/instance of type B:
- "An individual is an instance of a class" → individual instanceOf class
- Distinct from `implements`: `instanceOf` is token-of-type; `implements` is concrete-realisation-of-abstract

**`implements`** is appropriate when A is the formal realisation of B:
- "A class is the formal, extensional implementation of a concept" → class implements concept
- "An edge is the graph-theoretic realisation of a relationship" → edge implements relationship
- Distinct from `instanceOf`: `implements` is a design/realisation relation, not a membership relation

**`relatedTerm`** should be used as a fallback:
- When a relation clearly exists but does not fit any typed predicate
- When the relation type is ambiguous or context-dependent

---

## Upper Ontology Alignment (Future)

| `ms:` predicate | OWL/BFO alignment |
|---|---|
| `partOf` | `bfo:part_of` / `owl:TransitiveProperty` candidate |
| `instanceOf` | `rdf:type` (when target is a class in the ontology) |
| `implements` | `schema:isBasedOn` (partial) |
| `contrasts` | No standard alignment; domain-specific |
| `uses` | `schema:instrument` (partial) |

---

## Ground Truth

The annotation file for evaluation is:

```
data/eval/typed-relations-ground-truth.json
```

It contains typed relation annotations for 10 foundational concepts files derived from their "Distinguished From" tables and operational definitions. This annotation is the ground truth for W-0206 typed extraction scoring.
