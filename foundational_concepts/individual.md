# Individual

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

An individual is a specific, named or identified instance of one or more classes within an ontology; the atomic unit of the extensional domain that the ontology describes.

**Necessary conditions:**
1. **Specific** — it refers to exactly one particular entity in the domain, not a type or category.
2. **Instance** — it falls under at least one class defined in the ontology (explicitly asserted or inferred).
3. **Identifiable** — it has a URI/IRI or a uniquely scoped blank node identifier.
4. **Atomic** — it is not itself composed of other individuals by the class definition; it is the base-level unit of assertion.

**Sufficient conditions:**  
Any entity that is identified by a URI/IRI (or scoped blank node) and is asserted or inferred to be an instance of at least one class in the ontology constitutes an individual.

---

## Operational Definition

An individual is operationally identified when:

1. An `rdf:type` triple exists linking its URI to a class URI (e.g., `ex:ResearchItem rdf:type ex:Document`).
2. Property assertions (attributes and relationships) about it are stored as triples with its URI as subject.
3. A reasoner can classify it under further classes based on its properties and the ontology's class axioms.
4. It can be returned as a result of a SPARQL `SELECT` or `ASK` query.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Class** | A class is the type; an individual is the token that is an instance of the type. |
| **Concept** | A concept is the intensional meaning of a type; an individual is a specific thing that falls under that type. |
| **Resource** | A resource is any URI-identified entity; an individual is specifically a resource that is classified as an instance in an ontology. All individuals are resources; not all resources are individuals. |
| **Node** | A node is a graph-structural term; an individual is an ontological term. An individual is typically represented as a node. |

---

## Related Terms

[class](class.md) · [concept](concept.md) · [resource](resource.md) · [node](node.md) · [ontology](ontology.md) · [rdf](rdf.md)
