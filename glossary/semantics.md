# Semantics

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

Semantics is the systematic assignment of meaning to the expressions of a formal language, defined as a function from syntactic expressions to their interpretations in a model, specifying the truth conditions of those expressions.

**Necessary conditions:**
1. **Meaning-assigning** — it specifies what expressions in a language refer to or denote.
2. **Model-theoretic** — it defines interpretation via a model (a mathematical structure) that assigns referents to symbols and truth values to sentences.
3. **Language-relative** — it is defined for a specific formal or formal-ish language; the semantics of one language does not transfer to another.
4. **Truth-conditional** — for every well-formed sentence of the language, the semantics determines the conditions under which the sentence is true in a model.

**Sufficient conditions:**  
Any systematic specification of a function from syntactic expressions to interpretations in a model, defining truth conditions for those expressions, constitutes a semantics for that language.

---

## Operational Definition

Semantics is operationally applied when:

1. For every expression in the language, a defined interpretation function specifies its referent or truth value.
2. A reasoner uses the semantics to derive entailments: if a set of statements is true, what else must be true.
3. Inconsistency detection is possible: the semantics can identify when a set of statements has no satisfying model.
4. Two serialisations of the same knowledge are judged semantically equivalent when they have identical entailments.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Syntax** | Syntax specifies the structural rules for well-formed expressions; semantics specifies what those expressions mean. A syntactically valid expression may be semantically void or inconsistent. |
| **Pragmatics** | Pragmatics concerns the use of language in context; semantics concerns meaning independent of use context. |
| **Ontology** | An ontology encodes domain semantics in a formal language; semantics is the theory that defines what the ontology's statements mean. |

---

## Related Terms

[syntax](syntax.md) · [ontology](ontology.md) · [rdf](rdf.md) · [model](model.md) · [concept](concept.md) · [knowledge](knowledge.md)
