---
title: "Skill"
category: entity
tags: [skill, agent, instruction, module, reusable]
date: 2026-05-23
related:
  - term: "AI Agent"
    file: ai-agent.md
    rel: relatedTerm
  - term: "Open-Brain"
    file: open-brain.md
    rel: partOf
  - term: "Architecture Decision Record"
    file: adr.md
    rel: relatedTerm
aliases: ["agent skill", "skill module"]
---

**A reusable, self-contained Markdown file in `.github/skills/` that provides an AI agent with specialised instructions for a well-defined task type.**

## Definition

A skill is a modular unit of agent instructions. Where `.github/copilot-instructions.md` defines the global rules that apply to every agent action in this repository, a skill provides deep, task-specific guidance for a particular class of work — writing a backlog item, authoring a decision record, reviewing code, or conducting research.

Skills live in the `.github/skills/` submodule (pointing to `davidamitchell/Skills`). Each skill is a `SKILL.md` file in its own subdirectory. An agent that needs to perform a task covered by a skill reads that skill's SKILL.md before starting, rather than improvising its own approach.

The skills architecture separates concerns: the constitution (copilot-instructions.md) governs behaviour, while skills govern craft. This means skills can be shared across repositories via the submodule, while the constitution remains repository-specific.

## Usage in This System

Available skills (via `.github/skills/`):
- `backlog-manager` — writing and maintaining backlog items.
- `research` — structured research and synthesis.
- `technical-writer` — documentation and prose quality.
- `code-review` — reviewing code changes.
- `strategy-author` — writing strategy documents.
- `decisions` — writing Architecture Decision Records in MADR format.

## Related Terms

- [AI Agent](./ai-agent.md)
- [Open-Brain](./open-brain.md)
- [Architecture Decision Record](./adr.md)

## References

1. [`.github/copilot-instructions.md` §2](../.github/copilot-instructions.md) — the skills section of the agent constitution.
2. [`davidamitchell/Skills` (GitHub)](https://github.com/davidamitchell/Skills) — the shared skills submodule repository.
