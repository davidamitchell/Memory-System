# Attribute

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

An attribute is a typed property of a resource or class that takes a data value (literal) as its range, asserting a named characteristic of a resource expressed as a primitive value rather than a link to another resource.

**Necessary conditions:**
1. **Named** — it has a URI/IRI identifying the property type.
2. **Data-valued** — its range is a literal (string, number, date, boolean, etc.), not a URI/IRI-identified resource.
3. **Subject-attached** — it is asserted of a specific resource (the subject).
4. **Typed** — the literal value has a datatype (explicit or inferred, e.g., `xsd:string`, `xsd:dateTime`).

**Sufficient conditions:**  
Any named property whose range is a typed data value, asserted of a resource, constitutes an attribute.

---

## Operational Definition

An attribute is operationally identified when:

1. It is expressed as an RDF triple `(subject_URI, predicate_URI, literal_value)` where the object is a literal.
2. The predicate is declared as an `owl:DatatypeProperty` (or `rdf:Property` with a datatype range) in the ontology.
3. The literal value can be validated against a declared datatype (e.g., `xsd:integer`, `xsd:boolean`).

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Relationship** | A relationship connects a resource to another resource; an attribute connects a resource to a data value. |
| **Metadata** | Metadata is the set of attributes (and relationships) that describe a resource's identity and provenance; an attribute is the primitive unit from which metadata is composed. |
| **Property** | Property is the general term in RDF for both relationships (object properties) and attributes (datatype properties); attribute specifically denotes the datatype-valued kind. |

---

## Related Terms

[relationship](relationship.md) · [class](class.md) · [individual](individual.md) · [metadata](metadata.md) · [rdf](rdf.md)
