# Knowledge Extraction

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

Knowledge extraction is the process of identifying concepts, relationships, and facts within unstructured or semi-structured source material and formalising them as structured, machine-processable representations conformant to a defined ontology or schema.

**Necessary conditions:**
1. **Source-to-structure** — it takes source material that is not yet in a formal structured form and produces output that is.
2. **Ontology-governed** — the output conforms to a pre-defined or concurrently-developed ontology or schema; the formalisation is not arbitrary.
3. **Explicit output** — the result is expressed in a form that is independently queryable, reasoned over, or integrated with other structured knowledge.
4. **Identifies and formalises** — it both locates relevant content in the source (identification) and expresses it formally (formalisation); neither alone is sufficient.

**Sufficient conditions:**  
Any process that takes unstructured or semi-structured sources and produces structured, ontology-conformant representations of concepts, relationships, and facts constitutes knowledge extraction.

---

## Operational Definition

Knowledge extraction is operationally applied when:

1. Source documents (e.g., natural-language text, semi-structured markdown) are processed by a defined method.
2. The output is a set of structured assertions (e.g., RDF triples, ontology instances) that can be validated against a schema.
3. Each extracted assertion can be traced back to evidence in the source (provenance).
4. The extracted assertions can be queried, merged with, or compared to other knowledge bases.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Information extraction** | Information extraction identifies and structures surface-level data (named entities, dates, relations) from text; knowledge extraction additionally formalises these into an ontology, enabling reasoning and inference. |
| **Data mining** | Data mining discovers statistical patterns in structured datasets; knowledge extraction operates on source documents and produces ontologically-grounded statements. |
| **Knowledge discovery** | Knowledge discovery is a broader term including insight generation; knowledge extraction is specifically the formalisation step that precedes or enables discovery. |

---

## Related Terms

[knowledge](knowledge.md) · [ontology](ontology.md) · [corpus](corpus.md) · [document](document.md) · [fact](fact.md) · [information](information.md)
