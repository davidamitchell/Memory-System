# Glossary

This folder contains definition files for every key term used in this repository.
All definition files follow the schema in [`definition_scheme.md`](../definition_scheme.md).

The **Knowledge/Ontology Domain** section below contains an additional set of canonical
dual-form definitions (conceptual + operational) for core knowledge representation terms.

---

## Index

### System Terms

| Term | File | Category | Aliases |
|---|---|---|---|
| [AI Agent](./ai-agent.md) | `ai-agent.md` | concept | agent, coding agent, AI assistant, Copilot agent |
| [Agent-first](./agent-first.md) | `agent-first.md` | concept | agent-native, agent native |
| [Architecture Decision Record](./adr.md) | `adr.md` | practice | ADR, decision record |
| [Capture](./capture.md) | `capture.md` | concept | memory capture, write, add memory |
| [Embedding Model](./embedding-model.md) | `embedding-model.md` | tool | sentence encoder, text encoder |
| [Inbox](./inbox.md) | `inbox.md` | entity | inbox folder, capture inbox |
| [Knowledge Graph](./knowledge-graph.md) | `knowledge-graph.md` | concept | memory graph, vectorized knowledge graph |
| [LanceDB](./lancedb.md) | `lancedb.md` | tool | — |
| [Local-first](./local-first.md) | `local-first.md` | concept | local first, offline-first |
| [MADR](./madr.md) | `madr.md` | format | Markdown Any Decision Records |
| [MCP Server](./mcp-server.md) | `mcp-server.md` | entity | mcp_server.py, open-brain server |
| [MCP Tool](./mcp-tool.md) | `mcp-tool.md` | entity | tool call, MCP capability |
| [Memory File](./memory-file.md) | `memory-file.md` | entity | memory, note, brain file |
| [Mini-Retro](./mini-retro.md) | `mini-retro.md` | practice | mini retrospective, session retrospective, retro |
| [Model Context Protocol](./mcp.md) | `mcp.md` | protocol | MCP |
| [Open-Brain](./open-brain.md) | `open-brain.md` | project | GitHub Open-Brain, Memory-System |
| [Retrieval](./retrieval.md) | `retrieval.md` | concept | recall, memory retrieval, search |
| [Semantic Search](./semantic-search.md) | `semantic-search.md` | concept | vector search, similarity search |
| [Skill](./skill.md) | `skill.md` | entity | agent skill, skill module |
| [stdio Transport](./stdio-transport.md) | `stdio-transport.md` | protocol | stdio, standard input/output transport |
| [Superseded-by](./superseded-by.md) | `superseded-by.md` | practice | superseded, supersedes, superseded_by |
| [Tag](./tag.md) | `tag.md` | entity | label, category tag |
| [Triage](./triage.md) | `triage.md` | practice | inbox triage, classification |
| [Vector Database](./vector-database.md) | `vector-database.md` | tool | vector store, embedding store |
| [Vector Embedding](./vector-embedding.md) | `vector-embedding.md` | concept | embedding, text embedding, vector representation |
| [YAML Front Matter](./yaml-front-matter.md) | `yaml-front-matter.md` | format | front matter, frontmatter, YAML header |

---

## Categories

| Category | Description |
|---|---|
| `concept` | Abstract ideas and design patterns |
| `entity` | Concrete objects in the system |
| `format` | File formats and data structures |
| `practice` | Workflows, processes, and conventions |
| `project` | Named projects or systems defined in this repo |
| `protocol` | Communication standards and specifications |
| `tool` | Named external software, databases, or services |

Full category definitions and all definition file requirements are in [`definition_scheme.md`](../definition_scheme.md).

---

## Adding a New Term

1. Read [`definition_scheme.md`](../definition_scheme.md) before creating any file.
2. Create `glossary/<kebab-case-term>.md` following the schema exactly.
3. Add a row to the index table above.
4. Cross-link the term's first occurrence in any existing files where it appears.

---

### Knowledge/Ontology Domain Terms

### Foundation

| Term | File | One-line summary |
|------|------|-----------------|
| Ontology | [ontology.md](ontology.md) | Formal, explicit, shared specification of a domain's concepts, relationships, and constraints |
| Domain | [domain.md](domain.md) | Bounded region of discourse within which terms have fixed, determinate meanings |
| Meta-model | [meta-model.md](meta-model.md) | A model that specifies the valid constructs and constraints for a class of models |
| Model | [model.md](model.md) | Purposive, selective formal representation of a domain for reasoning or design |
| Semantics | [semantics.md](semantics.md) | Systematic assignment of meaning to language expressions via model-theoretic interpretation |
| Syntax | [syntax.md](syntax.md) | Formal rules determining the well-formedness of expressions in a language |

### Source Material

| Term | File | One-line summary |
|------|------|-----------------|
| Corpus | [corpus.md](corpus.md) | Finite, purposively assembled collection of documents used as source material |
| Document | [document.md](document.md) | Discrete, self-contained, addressable unit of recorded content |
| Metadata | [metadata.md](metadata.md) | Attributes describing a resource's identity, provenance, and structure |

### Conceptual Structure

| Term | File | One-line summary |
|------|------|-----------------|
| Concept | [concept.md](concept.md) | Abstract unit of meaning defined by necessary and sufficient membership conditions |
| Term | [term.md](term.md) | Linguistic expression assigned exactly one denotation within a domain |
| Theme | [theme.md](theme.md) | Recurrent, semantically coherent grouping without hard membership boundaries |
| Class | [class.md](class.md) | Formal, named set of individuals defined by necessary and sufficient conditions in an ontology |
| Individual | [individual.md](individual.md) | Specific, identified instance of one or more classes in an ontology |
| Attribute | [attribute.md](attribute.md) | Named property of a resource with a typed data value as its range |
| Relationship | [relationship.md](relationship.md) | Typed, directed association between two resources |
| Component | [component.md](component.md) | Modular, functionally bounded part of an ontology or knowledge system |
| List | [list.md](list.md) | Ordered, finite sequence of elements where position is significant |

### Graph & RDF

| Term | File | One-line summary |
|------|------|-----------------|
| Graph | [graph.md](graph.md) | Mathematical structure of nodes and edges representing binary relationships |
| Node | [node.md](node.md) | Discrete vertex in a graph representing a distinct entity or value |
| Edge | [edge.md](edge.md) | Connection between two nodes representing an association |
| Weight | [weight.md](weight.md) | Numeric value assigned to a node or edge under a defined measurement scheme |
| Resource | [resource.md](resource.md) | Any URI-identified entity about which statements can be made |
| RDF | [rdf.md](rdf.md) | W3C standard data model expressing statements as subject–predicate–object triples |
| RDF* | [rdf-star.md](rdf-star.md) | Extension of RDF allowing triples to appear as subjects or objects of other triples |

### Knowledge Hierarchy

| Term | File | One-line summary |
|------|------|-----------------|
| Data | [data.md](data.md) | Discrete recorded symbols or measurements that are not yet contextualised |
| Information | [information.md](information.md) | Contextualised, interpretable data that reduces uncertainty |
| Knowledge | [knowledge.md](knowledge.md) | Verified, true, relationally understood statements enabling reasoning and action |
| Fact | [fact.md](fact.md) | Verified true proposition recorded in a knowledge base |
| True | [true.md](true.md) | Property of a proposition that corresponds to the state of its domain |
| Insight | [insight.md](insight.md) | Derived, non-obvious statement grounded in facts with explanatory or actionable value |
| Wisdom | [wisdom.md](wisdom.md) | Capacity for sound evaluative judgment in applying knowledge to novel situations |

### Process & Capability

| Term | File | One-line summary |
|------|------|-----------------|
| Knowledge Extraction | [knowledge-extraction.md](knowledge-extraction.md) | Process of formalising concepts, relationships, and facts from unstructured sources |
| Process | [process.md](process.md) | Bounded, sequential, rule-governed sequence of operations transforming inputs to outputs |
| Capability | [capability.md](capability.md) | Stable, preconditioned, constrained ability to perform a class of operations |

---

## Relationship Map

The following partial ordering shows definitional dependencies (a → b means b's definition depends on a):

```
data → information → knowledge → insight → wisdom
data → fact → knowledge
true → fact
syntax → semantics → ontology
node + edge → graph → rdf → resource
concept → class → individual
term → concept
domain → ontology → meta-model
ontology → knowledge extraction → corpus ← document
model → meta-model
```
