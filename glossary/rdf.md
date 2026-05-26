# RDF (Resource Description Framework)

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

RDF is a W3C standard data model for expressing statements about resources as directed, typed triples of the form `(subject, predicate, object)`, where each component is either a URI/IRI (identifying a resource), a blank node (an anonymous resource), or a literal (a data value).

**Necessary conditions:**
1. **Triple-based** — every statement is expressed as exactly one subject–predicate–object triple.
2. **Subject** — is a URI/IRI or blank node (never a literal).
3. **Predicate** — is always a URI/IRI identifying a named relationship.
4. **Object** — is a URI/IRI, blank node, or typed/language-tagged literal.
5. **URI-identified** — resources are identified by URIs/IRIs, ensuring global uniqueness and dereference potential.
6. **Open-world** — the absence of a statement does not entail its falsity.

**Sufficient conditions:**  
Any data model that represents information exclusively as subject–predicate–object triples where subjects and predicates are URI/IRI-identified conforms to RDF.

---

## Operational Definition

RDF is operationally applied when:

1. A dataset can be serialised in a conformant RDF syntax (e.g., Turtle, N-Triples, JSON-LD, RDF/XML).
2. Each triple can be extracted and processed independently by an RDF-aware processor.
3. Two RDF graphs can be merged by taking the union of their triple sets without name collisions (given shared URI namespaces).
4. SPARQL queries can be executed against the dataset.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **RDF\*** (RDF-star) | RDF\* extends RDF to allow triples themselves to be subjects or objects of other triples; standard RDF does not permit this. |
| **OWL** | OWL (Web Ontology Language) is built on top of RDF and adds formal ontological constructs (class axioms, property restrictions); RDF is the underlying data model. |
| **JSON / XML** | JSON and XML are serialisation formats; RDF is a semantic data model (multiple serialisations are possible for the same RDF graph). |
| **Graph** | A graph is a mathematical structure of nodes and edges; RDF is a specific, URI-grounded, triple-based instantiation of a directed labelled graph. |

---

## Related Terms

[rdf-star](rdf-star.md) · [resource](resource.md) · [triple](relationship.md) · [graph](graph.md) · [ontology](ontology.md) · [semantics](semantics.md) · [syntax](syntax.md)
