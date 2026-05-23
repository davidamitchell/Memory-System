# Meta-model

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A meta-model is a model whose domain of discourse is models themselves: it specifies the structure, valid constructs, constraints, and semantics that all conforming models within a defined class must satisfy.

**Necessary conditions:**
1. **Models models** — its subject matter is the structure and valid elements of models, not of a first-order domain.
2. **Normative** — it prescribes what constitutes a valid model in its class; conformance to the meta-model is testable.
3. **Structural** — it defines the types of constructs (classes, properties, relationships) that may appear in conforming models.
4. **Constraining** — it imposes restrictions on how constructs may be combined, ordered, or typed.
5. **Class-scoped** — it governs a family of models, not a single model instance.

**Sufficient conditions:**  
Any model that defines the valid constructs, structure, and constraints for a class of models, and against which those models can be validated for conformance, constitutes a meta-model.

---

## Operational Definition

A meta-model is operationally identified when:

1. A schema or formal specification exists that lists the permitted element types and their valid combinations.
2. Any candidate model can be tested for conformance: the meta-model determines pass/fail.
3. Modelling tools use it to constrain what can be created (e.g., an ontology editor enforcing OWL syntax and semantics).
4. It is itself expressed in a meta-modelling language (e.g., OWL is the meta-model for OWL ontologies; MOF is the meta-model for UML).

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Model** | A model represents a first-order domain; a meta-model represents the space of valid models. Every meta-model is a model, but not every model is a meta-model. |
| **Ontology** | An ontology specifies the concepts and relationships of a first-order domain; a meta-model specifies the constructs and rules for building models (which may include ontologies). |
| **Schema** | A schema constrains data instances within a single model; a meta-model constrains the structure of models themselves. |

---

## Related Terms

[model](model.md) · [ontology](ontology.md) · [component](component.md) · [semantics](semantics.md) · [syntax](syntax.md)
