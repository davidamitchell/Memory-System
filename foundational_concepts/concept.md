# Concept

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A concept is an abstract unit of meaning that represents a category of entities or a type of thing, defined by necessary and sufficient conditions that determine which individuals fall under it.

**Necessary conditions:**
1. **Abstract** — it is not itself an individual instance; it represents a type, not a token.
2. **Intensional** — it is defined by a set of properties that characterise membership, not by enumeration of members.
3. **Determinate** — for any candidate individual, the necessary and sufficient conditions allow a fact-of-the-matter determination of membership (even if that determination requires inference).
4. **Domain-relative** — its definition holds within a specified domain; its meaning does not shift across that domain.

**Sufficient conditions:**  
Any abstract, intensionally defined unit of meaning with determinate membership conditions, operating within a domain, constitutes a concept.

---

## Operational Definition

A concept is operationally identified when:

1. It can be given a term (label) within a domain vocabulary.
2. Its necessary and sufficient conditions can be stated.
3. Given any individual and the concept's conditions, it is possible (in principle) to determine whether the individual is an instance.
4. It participates in at least one relationship (subsumption, composition, or association) with another concept in the domain.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Term** | A term is the linguistic label assigned to a concept; multiple terms may denote the same concept (synonyms). |
| **Class** | A class is the formal, extensional implementation of a concept in an ontology language (e.g., OWL class); a concept is the intensional meaning that the class encodes. |
| **Theme** | A theme groups related concepts by semantic proximity without formal membership conditions; a concept has determinate membership criteria. |
| **Individual** | An individual is an instance that falls under a concept; the concept is the type, the individual is the token. |

---

## Related Terms

[term](term.md) · [class](class.md) · [individual](individual.md) · [theme](theme.md) · [ontology](ontology.md) · [semantics](semantics.md)
