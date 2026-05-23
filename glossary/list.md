# List

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A list is an ordered, finite sequence of elements in which the position of each element is significant and the sequence has defined first and last members.

**Necessary conditions:**
1. **Ordered** — the elements have a defined linear sequence; position is meaningful.
2. **Finite** — it has a definite number of members (including the possibility of zero, an empty list).
3. **Position-significant** — the identity of a list is determined by both its members and their order; reordering the same members produces a distinct list.
4. **Bounded** — it has a defined first element (head) and a defined last element (tail terminus).

**Sufficient conditions:**  
Any finite, ordered sequence of elements where position is significant and boundaries are defined constitutes a list.

---

## Operational Definition

A list is operationally identified when:

1. Each element can be addressed by a non-negative integer index.
2. The elements can be iterated in a stable, reproducible order.
3. Inserting, appending, or reordering elements produces a distinct list.
4. In RDF: it is encoded using `rdf:List` with `rdf:first` and `rdf:rest` properties, terminating at `rdf:nil`.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Set** | A set is unordered and contains no duplicates; a list is ordered and may contain duplicates. |
| **Bag (multiset)** | A bag is unordered but allows duplicates; a list is ordered. |
| **Sequence** | Sequence is a synonym for list in most formal contexts; used interchangeably here. |
| **Graph** | A graph is a non-linear structure of nodes and edges; a list is a strictly linear structure. |

---

## Related Terms

[individual](individual.md) · [rdf](rdf.md) · [attribute](attribute.md) · [graph](graph.md)
