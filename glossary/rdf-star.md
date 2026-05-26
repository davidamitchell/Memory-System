# RDF* (RDF-star)

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

RDF-star (RDF*) is an extension of RDF that allows an existing triple to be used directly as the subject or object of another triple — called an *embedded triple* — enabling statements about statements without full reification.

**Necessary conditions:**
1. **Superset of RDF** — all valid RDF graphs are valid RDF-star graphs; it adds to, not replaces, RDF.
2. **Embedded triples** — a triple `(s, p, o)` may itself appear in the subject or object position of an outer triple.
3. **Asserted and quoted forms** — an embedded triple may be *asserted* (claimed to be true) or *quoted* (referenced without asserting truth), depending on the context.
4. **Preserves RDF semantics** — triples not involving embedded triples are interpreted identically to standard RDF.

**Sufficient conditions:**  
Any extension of RDF in which triples can appear in subject or object position of other triples, and which preserves standard RDF semantics for non-embedded triples, constitutes RDF-star.

---

## Operational Definition

RDF-star is operationally applied when:

1. A dataset requires statements about statements (e.g., provenance, confidence scores, temporal validity on individual triples).
2. The data is serialised in an RDF-star-compatible syntax (e.g., Turtle-star, N-Triples-star).
3. An RDF-star-aware query engine is used to process the embedded triples.
4. The embedded triple syntax `<< s p o >>` appears in the serialisation.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **RDF reification** | RDF reification uses four standard triples to describe a triple; RDF-star uses compact embedded-triple syntax without creating new blank nodes. |
| **Named graphs** | Named graphs assign provenance or context to a *set* of triples; RDF-star assigns metadata to an *individual* triple. |
| **RDF** | RDF does not permit triples in subject/object position; RDF-star extends this capability. |

---

## Related Terms

[rdf](rdf.md) · [graph](graph.md) · [resource](resource.md) · [relationship](relationship.md) · [metadata](metadata.md)
