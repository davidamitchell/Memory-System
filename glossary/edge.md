# Edge

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

An edge is a connection between two nodes in a graph that represents an association or relationship between the entities those nodes denote, optionally typed (labelled) and optionally directed.

**Necessary conditions:**
1. **Connects two nodes** — it has exactly two endpoints (source and target in a directed graph; two endpoints in an undirected graph).
2. **Graph-resident** — it exists within the context of a graph and has no meaning outside it.
3. **Representational** — it represents an association or relationship between the entities at its endpoints.

**Sufficient conditions:**  
Any connection between two nodes within a graph structure constitutes an edge.

---

## Operational Definition

An edge is operationally identified when:

1. It can be represented as a pair (or ordered pair for directed graphs) of node identifiers: `(source_id, target_id)`.
2. In a typed graph: it has a label or type identifier specifying the kind of association.
3. In an RDF graph: it corresponds to the predicate of a triple, with the subject and object as its endpoint nodes.
4. In a property graph: it may carry attributes (key-value pairs) and has a mandatory type label.
5. It can be traversed: starting from one endpoint node, it leads to the other.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Relationship** | A relationship is the knowledge-representation term for a typed, asserted connection between resources; an edge is the graph-theoretic term for a structural connection between nodes. |
| **Node** | A node is an endpoint entity; an edge is the connection between endpoint entities. |
| **Attribute** | An attribute is a property of a node with a data value; an edge connects two nodes (both are graph entities). |

---

## Related Terms

[node](node.md) · [graph](graph.md) · [relationship](relationship.md) · [weight](weight.md) · [rdf](rdf.md)
