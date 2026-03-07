# Changelog

All notable changes to this project will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- .github/copilot-instructions.md (replaces AGENTS.md as agent instruction source)
- .github/skills submodule pointing to davidamitchell/Skills
- .github/workflows/sync-skills.yml
- BACKLOG.md in backlog-manager skill format
- PROGRESS.md for append-only session history
- CHANGELOG.md (this file)
- docs/adr/ with ADR index and first decision record
- `## 13. Chain-of-Thought Reasoning` section in `.github/copilot-instructions.md` with memory-system-specific reasoning steps

### Removed
- AGENTS.md (content moved to .github/copilot-instructions.md)

### Changed
- README.md updated to remove AGENTS.md reference and reflect current structure
- `.github/copilot-instructions.md` section 7 replaced: "Mandatory System Self-Improvement" superseded by unified "Continuous Improvement & Learning" framework including Mini-Retro, improvement classes, and flywheel model
- Privacy section renumbered from 13 to 14 to accommodate new Chain-of-Thought Reasoning section
