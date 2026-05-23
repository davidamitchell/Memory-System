# Changelog

All notable changes to this project will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed — Full pivot documentation coherence pass
- `README.md` — Rewritten as single-architecture doc; removed dual-track framing, Quick Start, LanceDB and embedding model references
- `.github/copilot-instructions.md` — §1, §11, §12, §13, §15, §17, References updated to reflect ontology-only architecture
- `.github/copilot-setup-steps.yml` — Removed embedding model pre-warm step
- `glossary/open-brain.md` — Definition updated to describe ontology-based knowledge graph
- `glossary/lancedb.md` — Marked superseded; reframed as design concept replaced before implementation
- `glossary/retrieval.md` — Rewritten around ontology traversal and graph queries
- `glossary/semantic-search.md` — Marked superseded; reframed as the replaced approach
- `glossary/mcp-server.md` — `mcp_server.py` noted as legacy prototype; LanceDB references removed
- `glossary/knowledge-graph.md` — Rewritten to describe the ontology as the knowledge graph implementation
- `glossary/memory-file.md` — Removed LanceDB vector index as derived artefact; source document framing added
- `glossary/embedding-model.md` — Marked superseded; current production model framing removed
- `docs/design/build-loop-harness.md` — Phase 1 step 4 changed from "Call `search_brain`" to "Search the repository"

### Added
- `docs/design/build-loop-harness.md` — full Build Loop Harness protocol: five phases (Entry, Plan, Execute, Close, Self-Improve), validation checklist, drift correction, self-correction, Mermaid diagram, open questions
- `.github/copilot-instructions.md` §17 — condensed always-on Build Loop Harness reference with focus rules


- `docs/adr/0002-move-from-vector-storage-to-ontology.md` — decision to replace LanceDB vector storage with an ontology-based knowledge representation
- `docs/adr/0003-ontology-architecture.md` — decision establishing upper/lower ontology structure and the 11-processor pipeline
- `docs/adr/README.md` — updated index with ADR-0002 and ADR-0003

### Changed
- `README.md` — updated heading, added ontology direction notice, added target architecture diagram, updated repository layout
- `.github/copilot-instructions.md` — added architecture direction notice in §1, added `docs/design/` to folder structure table

- `definition_scheme.md` — mandatory schema, requirements, and cross-linking rules for all definition files
- `glossary/` folder with 26 definition files covering the full knowledge domain of this memory system
- `glossary/README.md` — index of all defined terms with categories and aliases
- New terms added to cover ontology gaps: `capture`, `triage`, `retrieval`, `superseded-by`, `mini-retro`, `agent-first`, `inbox`, `mcp-tool`, `mcp-server`
- `## References` section added to every content file in the repository
- Cross-links on first use of defined terms added across all content files (Wikipedia style)
- `§16 Glossary` section in `.github/copilot-instructions.md` with cross-linking rules and definition file requirements
- Glossary entry added to `README.md` repo layout and Further Reading section
- Glossary item added to the "What Done Means" checklist in `.github/copilot-instructions.md` §7

### Changed
- `README.md` — first uses of local-first, agent-native, LanceDB, semantic search, MCP, memory files, embedding model, vector database, MCP server, MCP tools, stdio transport cross-linked to glossary definitions


- `BACKLOG-v2.md` — 5 new work items (W-0111–W-0115) and 2 new phases (Phase 3 Structured relational layer, Phase 4 Human door); Phase 5–7 renumbered from previous Phase 3–5
- W-0111: discovery item — Supabase MCP integration architecture (two-server vs unified server)
- W-0112: implementation item — Supabase Postgres tables for contacts, meetings, and TBD (blocked by W-0111)
- W-0113: discovery/implementation item — human door auth model and Vercel skeleton (blocked by W-0112)
- W-0114: implementation item — contacts view, inline editing, quick-capture form (blocked by W-0113)
- W-0115: proactive/scheduled agent in Phase 7 Infrastructure (blocked by W-0114)
- `BACKLOG-v2.md` — implementation-ready roadmap (W-0100–W-0110) with Vision, Architecture, Research Cross-Reference, Outstanding Discovery sections, and 11 shaped work items across 5 phases
- `BACKLOG.md` items W-0003 through W-0015 — mobile capture and retrieval discovery backlog (Slack bot, Claude iOS, ChatGPT Actions, Gemini, Grok/X, iOS Shortcuts, Raycast/Alfred, `remember` CLI, Telegram bot, `inbox/` folder, Apple Watch dictation, self-hosted MCP options, LanceDB rebuild evaluation)
- `.github/copilot-setup-steps.yml` — bootstraps Copilot's cloud sandbox (Python 3.11, pip deps, pre-warmed embedding model)
- `.vscode/mcp.json` — MCP server configuration for VS Code Copilot and the headless coding agent
- Section 15 "GitHub Copilot — Headless / Web Mode" in `.github/copilot-instructions.md`
- "GitHub Copilot in Headless Mode" section in `README.md`
- `projects/2026-03-07-copilot-headless-mode.md` — project memory note for the setup
- `.github/copilot-instructions.md` (replaces AGENTS.md as agent instruction source)
- `.github/skills` submodule pointing to davidamitchell/Skills
- `.github/workflows/sync-skills.yml`
- `BACKLOG.md` in backlog-manager skill format
- `PROGRESS.md` for append-only session history
- `CHANGELOG.md` (this file)
- `docs/adr/` with ADR index and first decision record
- `## 13. Chain-of-Thought Reasoning` section in `.github/copilot-instructions.md` with memory-system-specific reasoning steps

### Removed
- `AGENTS.md` (content moved to `.github/copilot-instructions.md`)

### Changed
- `BACKLOG-v2.md` — W-0102 context updated: added capture friction note requiring the human-door quick-capture form to write to `inbox/` via GitHub Contents API (same path as iOS Shortcut and CLI, not a Supabase write path)
- `BACKLOG-v2.md` — Research Cross-Reference table extended with new items W-0111, W-0112, W-0114
- `BACKLOG-v2.md` — Outstanding Discovery table extended with W-0111, W-0113, and W-0115 discovery needs
- `BACKLOG-v2.md` — Phase 3 → Phase 5, Phase 4 → Phase 6, Phase 5 → Phase 7 (renumbered to make room for new phases)
- `README.md` updated to remove `AGENTS.md` reference, reflect current structure, and add headless-mode instructions
- `.github/copilot-instructions.md` section 7 replaced: "Mandatory System Self-Improvement" superseded by unified "Continuous Improvement & Learning" framework including Mini-Retro, improvement classes, and flywheel model
- Privacy section renumbered from 13 to 14 to accommodate new Chain-of-Thought Reasoning section

---

## References

1. [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) — the format used for this file.
2. [`.github/copilot-instructions.md` §6](../.github/copilot-instructions.md) — the agent instruction that mandates changelog entries for user-facing changes.
