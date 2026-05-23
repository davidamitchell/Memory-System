# Component

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A component is a modular, functionally bounded part of a larger ontology or knowledge system that can be independently identified, defined, and composed with other components, and that fulfils a specific representational or functional role within the whole.

**Necessary conditions:**
1. **Modular** — it has defined boundaries that separate it from other components.
2. **Functionally bounded** — it serves a specific, nameable representational or functional purpose.
3. **Part of a larger whole** — it is a constituent of a system or ontology, not a standalone system in itself.
4. **Composable** — it can be combined with other components to form the whole, and its contribution to the whole is determinate.
5. **Independently identifiable** — it can be referenced, described, and reasoned about without requiring the entire system.

**Sufficient conditions:**  
Any modular, functionally bounded, independently identifiable part of a knowledge system that is composable into a larger whole constitutes a component.

---

## Operational Definition

A component is operationally identified when:

1. It has a defined scope: a set of classes, properties, or axioms that belong to it and a set that do not.
2. It can be serialised and loaded independently (e.g., as a separate ontology module via `owl:imports`).
3. Its interface is defined: what it exports (terms usable by other components) and what it imports (terms it depends on).
4. Removing it from the system produces a well-defined reduction in the system's capabilities.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Module** | Module is a near-synonym; component emphasises functional role and composability, while module emphasises encapsulation and reuse. |
| **Ontology** | An ontology is a complete, self-standing specification; a component is a bounded part designed to be assembled into a larger specification. |
| **Class** | A class is a single named type within an ontology; a component is a grouping of multiple related classes, properties, and axioms. |

---

## Related Terms

[ontology](ontology.md) · [model](model.md) · [meta-model](meta-model.md) · [class](class.md) · [graph](graph.md)
