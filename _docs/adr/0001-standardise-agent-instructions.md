# 0001 — Standardise agent instruction files

Date: 2026-03-07
Status: accepted

## Context

Agent instructions lived in AGENTS.md at the repo root. The standard across the davidamitchell organisation is .github/copilot-instructions.md. AGENTS.md was referenced from README.md as the "constitution".

## Decision

Move all [AI agent](../../glossary/ai-agent.md) instructions to `.github/copilot-instructions.md`. Delete AGENTS.md. Update README.md. Add .github/skills submodule and supporting structure.

## Consequences

- Consistent with all other repos in the organisation
- All agents use the same well-known path
- README.md updated to reflect correct file locations

## References

1. [`_docs/adr/README.md`](./README.md) — index of all ADRs in this repository.
2. [`.github/copilot-instructions.md`](../../.github/copilot-instructions.md) — the file this decision establishes as the agent instruction source.
