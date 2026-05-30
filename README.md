# Memory-System — GitHub Open-Brain

A **GitHub-native**, [agent-native](./foundational_concepts/concept.md) knowledge store backed by GitHub Markdown files and an **ontology-based [knowledge graph](./foundational_concepts/graph.md)**, exposed to [AI](./foundational_concepts/knowledge.md) tools (Claude Desktop, Cursor, GitHub Copilot) via the [Model Context Protocol (MCP)](./foundational_concepts/semantics.md).

All pipeline processing runs inside **GitHub Actions**. There is no local deployment and no CLI interaction required from the user. Push a document to the repository and the pipeline runs automatically. The only deployment target is GitHub.

> **AI agents: read [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) for the rules and conventions that govern this repository.**

---

## How It Works

```
┌──────────────────────────────────────────┐
│  Document Sources                        │
└─────────────────┬────────────────────────┘
                  │ push to GitHub
                  ▼
        ┌──────────────────┐
        │  GitHub Actions  │  ← pipeline trigger (no local CLI required)
        │  Workflow        │
        └────────┬─────────┘
                 │ run_pipeline.py --strategy llm
                 ▼
         ┌─────────────────┐
         │  Processing     │  Sourcing → Cleaning → Metadata
         │  Pipeline       │  → Domain Classification → Matching
         │                 │  → Concept Extraction (LLM) → Ontology Build
         │                 │  → Consistency Validation → Versioning
         └────────┬────────┘
                  │
          ┌───────▼────────┐
          │ Ontology Store  │  Upper Ontology
          │                 │  Lower Ontologies (per domain)
          │                 │  Versioned snapshots (OWL/RDF/JSON-LD)
          └───────┬─────────┘
                  │ GitHub Pages (live) · MCP tools (future)
                  ▼
        ┌──────────────────┐
        │  Query / Browse  │  ← AI Agent Interface (future MCP)
        └──────────────────┘
```

1. **Storage** — Knowledge lives as [memory files](./foundational_concepts/document.md) (`.md` files) in `/meetings`, `/journal`, and `/projects`, and as versioned ontology snapshots in the Ontology Store.
2. **Processing Pipeline** — A 12-processor pipeline (see [ADR-0004](./_docs/adr/0004-provenance-model-and-control-plane.md)) extracts concepts from source documents using LLM (via `gh models run`), builds domain ontologies, validates consistency, and commits versioned ontology snapshots.
3. **Ontology Store** — An upper ontology (domain taxonomy) and per-domain lower ontologies, serialised as OWL/RDF/JSON-LD. Every assertion traces back to a content-addressed source segment.
4. **GitHub Actions Trigger** — Every pipeline run is triggered by a GitHub Actions workflow, not local CLI. Push a document to `raw_document_corpus/` and the pipeline runs automatically, commits the updated ontology, and redeploys the Pages site.
5. **MCP Bridge** — The [MCP server](./foundational_concepts/resource.md) exposes [MCP tools](./foundational_concepts/capability.md) to any MCP-compatible AI client for querying and writing to the knowledge store (not yet implemented — see [ADR-0002](./_docs/adr/0002-move-from-vector-storage-to-ontology.md)).

See the [design space](./_docs/design/ontology-system-design.md) for full component and sequence diagrams.

---

## Status

The architecture is fully designed (ADR-0002 through ADR-0004, `_docs/design/`). The ontology-based MCP server is **not yet implemented**. Active work is focused on implementing the processing pipeline and ontology store.

> For historical context on the original vector-storage concept that this design replaces, see [`getting-started-prompt.md`](./getting-started-prompt.md) (archived) and [ADR-0002](./_docs/adr/0002-move-from-vector-storage-to-ontology.md).

---

## GitHub-Native Execution

This system runs entirely on GitHub. There is no local deployment, no local server to run, and no CLI interaction required from the user. GitHub Actions workflows are the trigger functions for all pipeline processing.

| How to interact | What happens |
|---|---|
| **Push documents** to `raw_document_corpus/` | `pipeline.yml` workflow fires, processes all documents with LLM extraction, commits updated ontology, redeploys GitHub Pages site |
| **Assign an issue to Copilot** | Copilot runs in an ephemeral cloud sandbox (no local IDE required), opens a PR |
| **Trigger manually** | `workflow_dispatch` on `pipeline.yml` runs a full corpus reprocessing |

### Agent workflow (no local env required)

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
├── docs/                        # GitHub Pages site (index.html, style.css, app.js, data/)
├── _docs/
│   ├── adr/                     # Architecture Decision Records (MADR format)
│   └── design/                  # Conceptual design space — components and diagrams
├── foundational_concepts/       # Base ontology — foundational meta-model definitions
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
- [`_docs/design/ontology-system-design.md`](./_docs/design/ontology-system-design.md) — full architecture: components, pipeline, diagrams
- [`_docs/adr/README.md`](./_docs/adr/README.md) — all Architecture Decision Records
- [`foundational_concepts/README.md`](./foundational_concepts/README.md) — base ontology: foundational meta-model definitions
- [`definition_scheme.md`](./definition_scheme.md) — the schema every foundational concept definition file must follow

---

## References

1. [Model Context Protocol](https://modelcontextprotocol.io/) — the open standard used to expose knowledge tools to AI clients.
2. [OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-overview/) — the serialisation standard for ontology snapshots.
3. [W3C PROV-O](https://www.w3.org/TR/prov-o/) — the provenance ontology used for assertion lineage.
4. [Ink & Switch: Local-first Software](https://www.inkandswitch.com/local-first/) — the design philosophy behind this system's architecture.
