# Weight

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A weight is a numeric value assigned to a node or edge in a graph that quantifies a specific property of that node or edge — such as confidence, frequency, strength, cost, or importance — within the context of a defined measurement scheme.

**Necessary conditions:**
1. **Numeric** — it is a quantitative value (integer or real number) on a defined scale.
2. **Assigned** — it is attributed to a specific node or edge, not to the graph as a whole.
3. **Scheme-relative** — its interpretation is defined by a named measurement scheme that specifies what the number represents and on what scale.
4. **Comparative** — it is meaningful in comparison to the weights of other nodes or edges under the same scheme.

**Sufficient conditions:**  
Any numeric value assigned to a node or edge under a defined measurement scheme, intended for comparative use, constitutes a weight.

---

## Operational Definition

A weight is operationally identified when:

1. A numeric value is stored as an attribute of a node or edge.
2. The attribute has a declared type that specifies what property it measures (e.g., `confidence`, `co-occurrence_count`, `semantic_similarity`).
3. It can be used in graph algorithms (e.g., shortest path, ranking, clustering) where numeric edge or node values are required.
4. Its scale is declared (e.g., `[0, 1]` for probability; `[1, ∞)` for cost).

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Attribute** | An attribute is any named property with a data value; a weight is specifically a numeric attribute used for quantitative comparison or algorithmic computation. |
| **Label** | A label is a categorical identifier; a weight is a quantitative value. |

---

## Related Terms

[edge](edge.md) · [node](node.md) · [graph](graph.md) · [attribute](attribute.md)
