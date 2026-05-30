# Relationship

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A relationship is a typed, directed association between two resources (subject and object) that asserts a specific, named connection holding between them within a domain.

**Necessary conditions:**
1. **Typed** — it has a named predicate that specifies the kind of connection (e.g., `isPartOf`, `dependsOn`).
2. **Binary** — it connects exactly two participants: a subject (domain) and an object (range).
3. **Directed** — it has a defined source (subject) and a defined target (object); the direction is not reversible without defining a distinct inverse relationship.
4. **Between resources** — both subject and object are resources (URI/IRI-identified entities), not literals.
5. **Asserted** — its existence is a claim that the named association holds between the two participants.

**Sufficient conditions:**  
Any typed, directed assertion connecting two resources by a named predicate constitutes a relationship.

---

## Operational Definition

A relationship is operationally identified when:

1. It can be expressed as an RDF triple `(subject_URI, predicate_URI, object_URI)`.
2. The predicate has a domain constraint (restricting valid subject types) and a range constraint (restricting valid object types) defined in the ontology.
3. Removal of the triple removes the specific association between the two resources.
4. An inverse relationship (if defined) connects the same two resources in the opposite direction under a distinct predicate name.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Attribute** | An attribute connects a resource to a data value (literal); a relationship connects a resource to another resource. |
| **Edge** | An edge is the graph-theoretic term for a connection between nodes; a relationship is the knowledge-representation term for a typed, asserted connection between resources. |
| **Association** | Association is informal and may be undirected or untyped; a relationship is always typed and directed. |

---

## Related Terms

[class](class.md) · [attribute](attribute.md) · [edge](edge.md) · [resource](resource.md) · [rdf](rdf.md) · [ontology](ontology.md)
