# Resource

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A resource is any entity that can be uniquely identified by a URI/IRI and about which statements can be made in an RDF-based knowledge representation; the atomic unit of reference in a knowledge graph.

**Necessary conditions:**
1. **Identifiable** — it is or can be assigned a URI/IRI that uniquely identifies it within the open web or a closed system.
2. **Referenceable** — it can appear as the subject or object of a statement.
3. **Entity-neutral** — it may be a physical thing, a digital artifact, a concept, a person, an event, or any other kind of entity; the category imposes no restriction.

**Sufficient conditions:**  
Any entity that has been assigned a URI/IRI and can appear in the subject or object position of a statement constitutes a resource.

---

## Operational Definition

A resource is operationally identified when:

1. A URI/IRI can be assigned to it (e.g., `https://example.org/ontology/Agent`).
2. At least one triple exists with the resource's URI as subject or object.
3. The resource can be dereferenced (optionally) to retrieve a description of it.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Document** | A document is a specific type of resource — one that is a recorded-content artifact; not all resources are documents. |
| **Individual** | An individual is a resource that is an instance of a class in an ontology; a resource may or may not be classified as an individual. |
| **Node** | A node is a graph-theoretic term for a vertex; in RDF, a resource in subject or object position corresponds to a node in the RDF graph. |
| **Literal** | A literal is a data value (string, number, date); it can appear in object position but is not a resource (it has no URI). |

---

## Related Terms

[rdf](rdf.md) · [individual](individual.md) · [node](node.md) · [document](document.md) · [graph](graph.md)
