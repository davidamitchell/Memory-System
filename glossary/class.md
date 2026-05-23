# Class

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A class is a formal, named set of individuals that share a common definition expressed as necessary and sufficient conditions, within an ontology, such that a reasoner can determine class membership for any individual.

**Necessary conditions:**
1. **Formally defined** — its membership conditions are expressed in a formal ontology language (e.g., OWL).
2. **Named** — it has a URI/IRI that uniquely identifies it within the ontology.
3. **Extensional** — its extension is the set of all individuals that satisfy its membership conditions at any point in time.
4. **Membership-determinate** — given an individual and the class definition, a reasoner can determine (or infer) membership.
5. **Closed under reasoning** — all individuals that satisfy the conditions are members, even if not explicitly asserted.

**Sufficient conditions:**  
Any formally defined, named construct in an ontology that groups individuals satisfying stated necessary and sufficient conditions constitutes a class.

---

## Operational Definition

A class is operationally identified when:

1. It is declared with `owl:Class` (or equivalent) in the ontology.
2. Its definition is stated using class axioms (e.g., `rdfs:subClassOf`, `owl:equivalentClass`, property restrictions).
3. A reasoner can classify any given individual as a member, non-member, or indeterminate.
4. Instances of the class can be queried via SPARQL using `rdf:type` or inference.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Concept** | A concept is the intensional meaning (the idea); a class is the formal implementation of that concept in an ontology language. |
| **Theme** | A theme is a soft, approximate grouping; a class has hard, formal membership conditions. |
| **Individual** | An individual is an instance of a class; the class is the type, the individual is the token. |
| **Set** | A mathematical set is defined only by its members; a class is defined by conditions that generate its membership, not by enumeration. |

---

## Related Terms

[concept](concept.md) · [individual](individual.md) · [ontology](ontology.md) · [relationship](relationship.md) · [attribute](attribute.md) · [rdf](rdf.md)
