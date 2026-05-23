---
title: "Open-Brain"
category: project
tags: [open-brain, memory-system, project, github]
date: 2026-05-23
related:
  - term: "Local-first"
    file: local-first.md
  - term: "Agent-first"
    file: agent-first.md
  - term: "MCP Server"
    file: mcp-server.md
  - term: "Knowledge Graph"
    file: knowledge-graph.md
aliases: ["GitHub Open-Brain", "Memory-System", "open brain"]
---

**The personal AI knowledge store implemented in this repository: a local-first, agent-native knowledge base backed by Markdown files and an ontology-based knowledge graph, exposed to AI tools via the Model Context Protocol.**

## Definition

Open-Brain is the project name for this repository's knowledge store. It is designed as the "single brain" across all AI tools a developer uses — rather than each AI assistant (Claude, Copilot, Cursor) maintaining its own private memory silo, Open-Brain provides one shared, agent-accessible knowledge base.

The core design goals are:
- **Local-first**: data lives on the user's machine as plain Markdown files in a git repository.
- **Agent-native**: AI agents can read and write knowledge autonomously via MCP tools.
- **Zero recurring cost**: uses free, open-source components and GitHub free tier.
- **Self-improving**: agents are constituted as "Architects", mandated to improve the system's structure as they work.

The knowledge representation is ontology-based: concepts are structured as a typed graph of upper and lower ontologies, not a flat vector index. See [ADR-0002](../docs/adr/0002-move-from-vector-storage-to-ontology.md) for the decision and [ADR-0004](../docs/adr/0004-provenance-model-and-control-plane.md) for the full architecture.

The name "Open-Brain" distinguishes the system from closed, vendor-proprietary memory features (e.g. ChatGPT Memory, Claude Projects) that lock knowledge inside a single vendor's platform.

## Usage in This System

- The repository root is the Open-Brain installation.
- `README.md` is the user-facing introduction to Open-Brain.
- `getting-started-prompt.md` preserves the original vector-storage concept (archived).
- The ontology-based MCP server is under active design; see `docs/design/ontology-system-design.md`.

## Related Terms

- [Local-first](./local-first.md)
- [Agent-first](./agent-first.md)
- [MCP Server](./mcp-server.md)
- [Knowledge Graph](./knowledge-graph.md)

## References

1. [`README.md`](../README.md) — user-facing documentation for Open-Brain.
2. [`getting-started-prompt.md`](../getting-started-prompt.md) — original architecture brief and PRD (archived).
