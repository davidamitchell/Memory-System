# Model

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A model is a purposive, selective formal or semi-formal representation of a domain that captures specific aspects of its structure, entities, relationships, or behaviour for purposes of reasoning, prediction, communication, or design.

**Necessary conditions:**
1. **Representational** — it stands for a domain; it is not the domain itself.
2. **Selective** — it captures only chosen aspects of the domain; no model is exhaustive.
3. **Purposive** — it is constructed for an explicit purpose that determines what is and is not included.
4. **Interpretable** — its elements can be mapped to (or evaluated against) the domain it represents.
5. **Formal or semi-formal** — its structure is defined with sufficient precision to be used consistently across agents.

**Sufficient conditions:**  
Any purposive, selective, interpretable representation of a domain with sufficient formal precision constitutes a model.

---

## Operational Definition

A model is operationally identified when:

1. A correspondence can be stated between its elements and elements of the domain it represents.
2. Questions about the domain can be answered by querying the model (within its defined scope).
3. Its scope conditions can be stated: the class of questions it is designed to answer and the class it is not.
4. Two agents using the same model for the same purpose produce consistent results.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Ontology** | An ontology is a normative, shared, formal specification of a domain's conceptual structure; a model is any selective representation. Every ontology is a model, but not every model is an ontology. |
| **Meta-model** | A meta-model is a model whose subject is models themselves; it defines what constitutes a valid model. |
| **Schema** | A schema constrains the structure of data instances; a model additionally carries semantic interpretation and may enable reasoning. |
| **Simulation** | A simulation is a dynamic model that enacts processes over time; a model in the general sense may be static or dynamic. |

---

## Related Terms

[ontology](ontology.md) · [meta-model](meta-model.md) · [semantics](semantics.md) · [graph](graph.md) · [component](component.md)
