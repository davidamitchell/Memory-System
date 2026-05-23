# Ontology

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

An ontology is a formal, explicit, shared specification of the concepts, relationships, and constraints that constitute a domain of discourse, enabling both human understanding and machine-processable reasoning over that domain.

**Necessary conditions:**
1. **Formal** — expressed in a language with a defined syntax and model-theoretic semantics (not natural language prose alone).
2. **Explicit** — all concepts, relationships, and constraints are named and defined; nothing is left implicit.
3. **Shared** — represents an intersubjective (community-agreed) conceptualisation, not a private one.
4. **Domain-scoped** — covers exactly one bounded region of discourse; terms have their defined meanings only within that scope.
5. **Includes constraints** — specifies which combinations of instances and relationships are permitted (not merely what exists).

**Sufficient conditions:**  
Any artifact that is formal, explicit, shared, domain-scoped, and specifies concepts + relationships + constraints constitutes an ontology.

---

## Operational Definition

An ontology can be identified and applied by the following criteria:

1. It is encoded in a formal language (e.g., OWL, RDF Schema, Common Logic).
2. Every term in it has a definition expressible as necessary and sufficient conditions.
3. A reasoner can use it to classify individuals, detect inconsistencies, and derive inferences.
4. Two parties working independently with the same ontology will assign the same interpretation to the same term in the same context.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Taxonomy** | A taxonomy organises concepts in a hierarchy (is-a only); an ontology additionally defines non-hierarchical relationships and formal constraints. |
| **Vocabulary / Glossary** | A vocabulary assigns natural-language definitions to terms; an ontology assigns formal, machine-processable definitions. |
| **Schema** | A schema constrains data structures; an ontology additionally carries semantic commitments about what entities and relationships mean. |
| **Model** | A model represents selected aspects of a domain for a purpose; an ontology is a normative specification of the domain's conceptual structure. |
| **Knowledge Graph** | A knowledge graph is a populated instance of an ontology (individuals + assertions); the ontology is the schema governing it. |

---

## Related Terms

[domain](domain.md) · [concept](concept.md) · [class](class.md) · [relationship](relationship.md) · [individual](individual.md) · [semantics](semantics.md) · [meta-model](meta-model.md) · [knowledge](knowledge.md)
