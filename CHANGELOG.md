# Changelog

All notable changes to this project will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
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
- `README.md` updated to remove `AGENTS.md` reference, reflect current structure, and add headless-mode instructions
- `.github/copilot-instructions.md` section 7 replaced: "Mandatory System Self-Improvement" superseded by unified "Continuous Improvement & Learning" framework including Mini-Retro, improvement classes, and flywheel model
- Privacy section renumbered from 13 to 14 to accommodate new Chain-of-Thought Reasoning section
