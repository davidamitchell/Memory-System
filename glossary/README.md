# Glossary

This folder contains definition files for every key term used in this repository.
All definition files follow the schema in [`definition_scheme.md`](../definition_scheme.md).

---

## Index

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
