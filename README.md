# Memory-System — GitHub Open-Brain

A **[local-first](./glossary/local-first.md)**, [agent-native](./glossary/agent-first.md) knowledge store backed by GitHub Markdown files and an **ontology-based [knowledge graph](./glossary/knowledge-graph.md)**, exposed to [AI](./glossary/ai-agent.md) tools (Claude Desktop, Cursor, GitHub Copilot) via the [Model Context Protocol (MCP)](./glossary/mcp.md).

> **AI agents: read [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) for the rules and conventions that govern this repository.**

---

## How It Works

```
┌──────────────────────────────────────────┐
│  Document Sources                        │
└─────────────────┬────────────────────────┘
                  │ ingest
                  ▼
         ┌─────────────────┐
         │  Processing     │  Sourcing → Cleaning → Metadata
         │  Pipeline       │  → Domain Classification → Matching
         │                 │  → Concept Extraction → Ontology Build
         │                 │  → Consistency Validation → Versioning
         └────────┬────────┘
                  │
          ┌───────▼────────┐
          │ Ontology Store  │  Upper Ontology
          │                 │  Lower Ontologies (per domain)
          │                 │  Versioned snapshots (OWL/RDF/JSON-LD)
          └───────┬─────────┘
                  │ MCP tools
                  ▼
        ┌──────────────────┐
        │  MCP Server      │  ← AI Agent Interface
        └──────────────────┘
```

1. **Storage** — Knowledge lives as [memory files](./glossary/memory-file.md) (`.md` files) in `/meetings`, `/journal`, and `/projects`, and as versioned ontology snapshots in the Ontology Store.
2. **Processing Pipeline** — A 12-processor pipeline (see [ADR-0004](./docs/adr/0004-provenance-model-and-control-plane.md)) extracts concepts from source documents, builds domain ontologies, validates consistency, and commits versioned ontology snapshots.
3. **Ontology Store** — An upper ontology (domain taxonomy) and per-domain lower ontologies, serialised as OWL/RDF/JSON-LD. Every assertion traces back to a content-addressed source segment.
4. **MCP Bridge** — The [MCP server](./glossary/mcp-server.md) exposes [MCP tools](./glossary/mcp-tool.md) to any MCP-compatible AI client for querying and writing to the knowledge store.
5. **Auto-sync** — Every write is automatically committed and pushed to GitHub.

See the [design space](./docs/design/ontology-system-design.md) for full component and sequence diagrams.

---

## Status

The architecture is fully designed (ADR-0002 through ADR-0004, `docs/design/`). The ontology-based MCP server is **not yet implemented**. Active work is focused on implementing the processing pipeline and ontology store.

> For historical context on the original vector-storage concept that this design replaces, see [`getting-started-prompt.md`](./getting-started-prompt.md) (archived) and [ADR-0002](./docs/adr/0002-move-from-vector-storage-to-ontology.md).

---

## GitHub Copilot in Headless Mode (Web / Mobile)

You can assign issues to Copilot from **github.com or the GitHub mobile app** — no local IDE or terminal required.

### Step-by-step

1. Open this repository on **github.com** (or the mobile app).
2. Go to **Issues → New issue** and describe the task (design work, documentation, backlog items, ADRs).
3. In the **Assignees** panel, assign the issue to **Copilot**.
4. Copilot opens a session, runs `copilot-setup-steps.yml` to set up the Python environment, and works on the task.
5. It opens a **Pull Request** with the resulting file changes.
6. Review and merge the PR from the browser or phone.

### MCP configuration

`.vscode/mcp.json` configures the MCP server for both VS Code Copilot and the headless coding agent. Update this file when the ontology-based MCP server is implemented.

---

## Repository Layout

```
Memory-System/
├── .github/
│   ├── copilot-instructions.md  # AI agent instructions (read this first)
│   ├── copilot-setup-steps.yml  # Copilot sandbox setup
│   ├── skills/                  # Agent skills submodule (davidamitchell/Skills)
│   └── workflows/
│       └── sync-skills.yml      # Weekly skills submodule update
├── docs/
│   ├── adr/                     # Architecture Decision Records (MADR format)
│   └── design/                  # Conceptual design space — components and diagrams
├── glossary/                    # Controlled vocabulary — one definition file per term
├── definition_scheme.md         # Schema and rules every definition file must follow
├── mcp_server.py              # Legacy prototype (vector/LanceDB-based) — to be replaced
├── requirements.txt           # Python dependencies
├── getting-started-prompt.md  # Original vector-storage concept (archived)
├── BACKLOG.md                 # Work backlog (backlog-manager skill format)
├── PROGRESS.md                # Append-only session history
├── CHANGELOG.md               # User-facing change log (Keep a Changelog)
├── meetings/                  # Meeting notes
├── journal/                   # Daily thoughts & reflections
└── projects/                  # Project context & decisions
```

---

## Cost

| Component | Cost |
|---|---|
| GitHub storage | Free |
| Ontology tooling (OWL/RDF, local) | Free |
| **Total** | **$0.00 / month** |

---

## Further Reading

- [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) — rules for AI agents working in this repo
- [`docs/design/ontology-system-design.md`](./docs/design/ontology-system-design.md) — full architecture: components, pipeline, diagrams
- [`docs/adr/README.md`](./docs/adr/README.md) — all Architecture Decision Records
- [`glossary/README.md`](./glossary/README.md) — controlled vocabulary: definitions for every key term in the system
- [`definition_scheme.md`](./definition_scheme.md) — the schema every glossary definition file must follow

---

## References

1. [Model Context Protocol](https://modelcontextprotocol.io/) — the open standard used to expose knowledge tools to AI clients.
2. [OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-overview/) — the serialisation standard for ontology snapshots.
3. [W3C PROV-O](https://www.w3.org/TR/prov-o/) — the provenance ontology used for assertion lineage.
4. [Ink & Switch: Local-first Software](https://www.inkandswitch.com/local-first/) — the design philosophy behind this system's architecture.
