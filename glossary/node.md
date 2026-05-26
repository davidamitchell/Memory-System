# Node

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A node is a discrete vertex in a graph that represents a distinct entity, resource, concept, or value, and that may be connected to other nodes by edges.

**Necessary conditions:**
1. **Discrete** — it is a distinct element in the graph; it has identity separate from all other nodes.
2. **Graph-resident** — it exists only within the context of a graph structure.
3. **Connectable** — it may be the source or target of zero or more edges (including isolated nodes with no edges).

**Sufficient conditions:**  
Any discrete, identifiable vertex within a graph structure constitutes a node.

---

## Operational Definition

A node is operationally identified when:

1. It can be assigned a unique identifier within the graph (URI, blank node ID, or index).
2. It can be addressed in graph traversal or query operations.
3. In an RDF graph: it corresponds to a resource (URI or blank node) or a literal appearing in subject or object position.
4. In a property graph: it may carry attributes (key-value pairs) describing its properties.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Resource** | A resource is the knowledge-representation term for an identifiable entity; a node is the graph-theoretic term for a vertex. In an RDF graph, resources correspond to nodes, but the concepts belong to different levels of abstraction. |
| **Individual** | An individual is an ontological term for an instance of a class; a node is a graph-structural term. An individual is typically represented as a node, but not all nodes are individuals. |
| **Edge** | An edge is a connection between nodes; a node is the connected entity itself. |

---

## Related Terms

[edge](edge.md) · [graph](graph.md) · [resource](resource.md) · [individual](individual.md) · [rdf](rdf.md) · [weight](weight.md)
