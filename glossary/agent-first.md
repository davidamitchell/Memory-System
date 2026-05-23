---
title: "Agent-first"
category: concept
tags: [agent-first, agent-native, design, architecture, ai]
date: 2026-05-23
related:
  - term: "AI Agent"
    file: ai-agent.md
  - term: "Local-first"
    file: local-first.md
  - term: "Model Context Protocol"
    file: mcp.md
  - term: "Open-Brain"
    file: open-brain.md
aliases: ["agent-native", "agent native", "agent first"]
---

**A design philosophy that treats AI agents as primary users of a system, building in autonomous read/write access, versioned context, and self-correction from the start rather than adding them as afterthoughts.**

## Definition

Agent-first (also called agent-native) is a design philosophy for software systems. A system is agent-first when it is designed from the ground up for autonomous AI use, rather than being a human-facing application with AI bolted on. The three hallmarks of an agent-first system are:

1. **Bi-directional access**: the agent doesn't just read data; it has the authority to create and update it.
2. **Versioned context**: the agent can use version history to understand how the data (and the thinking behind it) has evolved over time.
3. **Self-correction**: the agent is explicitly tasked with finding and fixing structural errors in the data — not just consuming it passively.

Open-Brain is agent-first in all three senses: agents use `add_memory` and `refactor_memory` to write (not just `search_brain` to read), the git history is available as context, and the constitution explicitly mandates that agents act as "Architects" who improve the system rather than just users who consume it.

## Usage in This System

- README.md describes Open-Brain as "agent-native".
- The agent constitution in `.github/copilot-instructions.md` is the primary implementation of the agent-first design: it gives agents permission and mandate to improve the repository structure.

## Related Terms

- [AI Agent](./ai-agent.md)
- [Local-first](./local-first.md)
- [Model Context Protocol](./mcp.md)
- [Open-Brain](./open-brain.md)

## References

1. [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — principles for systems designed around agentic AI.
2. [`getting-started-prompt.md` §3](../getting-started-prompt.md) — the original "Standard Agent-First Definition" in the project PRD.
