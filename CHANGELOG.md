# Changelog

All notable changes to this project will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- `glossary/` — 35 canonical definitions for the knowledge/ontology domain (ontology, domain, meta-model, model, semantics, syntax, corpus, document, metadata, concept, term, theme, class, individual, attribute, relationship, component, list, graph, node, edge, weight, resource, rdf, rdf-star, data, information, knowledge, fact, true, insight, wisdom, knowledge-extraction, process, capability) with `glossary/README.md` index and dependency map
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
