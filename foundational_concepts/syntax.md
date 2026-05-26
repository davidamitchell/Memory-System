# Syntax

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

Syntax is the set of formal rules that define the structure and composition of well-formed expressions in a language, independent of the meanings those expressions carry.

**Necessary conditions:**
1. **Rule-governed** — it consists of explicit, finite rules that determine which strings or structures are well-formed.
2. **Structure-only** — it concerns the form of expressions, not their interpretation or truth conditions.
3. **Language-specific** — the rules apply to a particular language; the syntax of one language does not govern another.
4. **Decidable** — for any given expression, it is decidable (in finite steps) whether the expression is syntactically well-formed.

**Sufficient conditions:**  
Any complete, explicit set of rules that determines the well-formedness of expressions in a language, independently of their meaning, constitutes a syntax for that language.

---

## Operational Definition

Syntax is operationally applied when:

1. A parser can accept or reject any given expression as well-formed or ill-formed.
2. A serialiser can produce expressions that conform to the rules.
3. Two syntactically distinct expressions may be semantically equivalent (e.g., Turtle and RDF/XML serialising the same RDF graph).
4. A syntax validator can be run prior to, and independently of, any semantic processing.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Semantics** | Semantics assigns meaning to well-formed expressions; syntax only determines which expressions are well-formed. |
| **Format** | Format is an informal term for a data layout convention; syntax is a formal specification with decidable well-formedness. |
| **Schema** | A schema constrains the structure of data instances; syntax constrains the structure of the language's expressions before data meaning is considered. |

---

## Related Terms

[semantics](semantics.md) · [rdf](rdf.md) · [ontology](ontology.md) · [model](model.md)
