# Graph

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A graph is a mathematical structure consisting of a non-empty set of nodes and a set of edges, where each edge connects two nodes, used to represent binary relationships between entities.

**Necessary conditions:**
1. **Node set** — it contains at least one node (non-empty).
2. **Edge set** — it contains a (possibly empty) set of edges, each connecting exactly two nodes (which may be the same node, in the case of a self-loop).
3. **Binary relationships** — edges represent pairwise connections; edges connect exactly two endpoints.
4. **Well-defined** — for any given structure, it is decidable whether each element is a node, an edge, or neither.

**Sufficient conditions:**  
Any structure consisting of a non-empty node set and an edge set where each edge connects two nodes constitutes a graph.

---

## Operational Definition

A graph is operationally identified when:

1. Its nodes can be enumerated and individually addressed.
2. Its edges can be enumerated, and for each edge, its two endpoint nodes are defined.
3. Graph algorithms (traversal, shortest path, clustering) can be applied to it.
4. In a directed graph: each edge has a defined source and target (not interchangeable).
5. In a labelled graph: each edge has a type label; in a property graph, nodes and edges also carry key-value attributes.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **RDF** | RDF is a specific, URI-grounded, triple-based instantiation of a directed labelled graph with formal semantics; a graph is the abstract mathematical structure that RDF instantiates. |
| **Tree** | A tree is a connected, acyclic graph; a general graph may have cycles and disconnected components. |
| **Network** | Network is an informal term often used for applied or weighted graphs; graph is the formal mathematical term. |
| **Knowledge Graph** | A knowledge graph is a graph whose nodes are entities or concepts and whose edges represent typed, asserted relationships, governed by an ontology; a graph is the abstract structure it instantiates. |

---

## Related Terms

[node](node.md) · [edge](edge.md) · [rdf](rdf.md) · [ontology](ontology.md) · [model](model.md) · [weight](weight.md)
