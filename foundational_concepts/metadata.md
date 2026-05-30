# Metadata

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

Metadata is the set of attributes and relationships that describe the identity, provenance, structure, and administrative properties of a resource or document, without constituting the primary subject-matter content of that resource.

**Necessary conditions:**
1. **Descriptive of a resource** — it is about a resource, not the primary content of that resource.
2. **Structural or administrative** — it concerns identity (what the resource is), provenance (where it came from, when, by whom), structure (how it is organised), or administrative status (its lifecycle state).
3. **Distinct from content** — removing the metadata leaves the substantive content of the resource intact; removing the content leaves the metadata structurally valid (though pointing to nothing).

**Sufficient conditions:**  
Any set of attributes and relationships that describe the identity, provenance, structure, or administrative properties of a resource, and that is distinct from the resource's primary content, constitutes metadata.

---

## Operational Definition

Metadata is operationally identified when:

1. It is stored separately from (or clearly delimited within) the resource's primary content (e.g., YAML frontmatter, HTTP headers, an RDF graph about the resource).
2. It includes at least one identifier attribute (e.g., `title`, `URI`, `slug`).
3. It can be processed and queried without parsing the resource's primary content.
4. It remains valid and useful even when the primary content is unavailable.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Data** | Data is the raw, uninterpreted primary content; metadata is the structured description *about* that content. |
| **Attribute** | An attribute is a single name–value property; metadata is the aggregate collection of attributes (and relationships) describing a resource. |
| **Content** | Content is what the resource is about (its subject matter); metadata is what the resource is (its description). |

---

## Related Terms

[attribute](attribute.md) · [document](document.md) · [resource](resource.md) · [data](data.md) · [ontology](ontology.md)
