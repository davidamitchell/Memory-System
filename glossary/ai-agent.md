---
title: "AI Agent"
category: concept
tags: [agent, ai, autonomous, copilot, claude, cursor]
date: 2026-05-23
related:
  - term: "Model Context Protocol"
    file: mcp.md
    rel: uses
  - term: "MCP Tool"
    file: mcp-tool.md
    rel: uses
  - term: "Agent-first"
    file: agent-first.md
    rel: relatedTerm
  - term: "Skill"
    file: skill.md
    rel: uses
aliases: ["agent", "coding agent", "AI assistant", "Copilot agent"]
---

**An AI system that can autonomously take sequences of actions — including calling external tools — to complete a goal specified in natural language.**

## Definition

An AI agent is an AI system that goes beyond single-turn question-answering. Given a goal (in natural language), it plans a sequence of steps, calls tools to gather information or take actions, observes the results, and iterates until the goal is met. The key characteristic is autonomy: the agent decides which tools to call, in what order, and with what arguments — without the human specifying each step.

In the context of this repository, the primary agents are GitHub Copilot's coding agent, Claude Desktop, and Cursor. Each of these connects to `mcp_server.py` via the Model Context Protocol, which gives the agent access to the three MCP tools (`search_brain`, `add_memory`, `refactor_memory`). The agent uses these tools to read from and write to the memory system.

The copilot-instructions.md constitution explicitly frames the agent as the "Architect" of this repository — not just a passive consumer. This reflects an agent-first design: the system is built for AI agency, not retrofitted to accommodate it.

## Usage in This System

- GitHub Copilot's coding agent is the primary automated agent, triggered via GitHub Issues assigned to `@copilot`.
- Claude Desktop is a secondary agent, connected to the same `mcp_server.py` via a local MCP connection.
- `.github/copilot-instructions.md` is the constitution all agents must read before acting.

## Related Terms

- [Model Context Protocol](./mcp.md)
- [MCP Tool](./mcp-tool.md)
- [Agent-first](./agent-first.md)
- [Skill](./skill.md)

## References

1. [GitHub Copilot Coding Agent](https://docs.github.com/en/copilot/using-github-copilot/using-copilot-coding-agent) — how Copilot's coding agent works.
2. [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — design principles for agentic AI systems.
