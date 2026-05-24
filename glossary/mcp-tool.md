---
title: "MCP Tool"
category: entity
tags: [mcp, tool, api, capability]
date: 2026-05-23
related:
  - term: "Model Context Protocol"
    file: mcp.md
    rel: partOf
  - term: "MCP Server"
    file: mcp-server.md
    rel: partOf
  - term: "AI Agent"
    file: ai-agent.md
    rel: relatedTerm
aliases: ["tool call", "MCP capability"]
---

**A named, typed capability declared by an MCP server that an AI agent can discover and invoke autonomously.**

## Definition

An MCP Tool is a callable unit of functionality exposed by an MCP server. Each tool has a name (e.g. `search_brain`), a human-readable description that the AI uses to decide when to call it, and a JSON Schema specifying its arguments and their types. The AI client discovers the full tool list when it connects to the server, and can then invoke any tool by name during a conversation or agentic task.

Tools are the primary mechanism through which AI agents take actions in the world via MCP. Unlike a direct API call made by a human developer, an MCP tool call is initiated autonomously by the AI based on its understanding of the task — the human does not need to specify which tool to call or what arguments to pass.

## Usage in This System

- `search_brain(query: str) → list[dict]` — semantic search over all memory files.
- `add_memory(title: str, content: str, folder: str) → str` — creates a new timestamped memory file.
- `refactor_memory(file_path: str, new_content: str) → str` — overwrites an existing memory file.

These three tools are the complete public interface of `mcp_server.py`. Any AI client with MCP support can call them.

## Related Terms

- [Model Context Protocol](./mcp.md)
- [MCP Server](./mcp-server.md)
- [AI Agent](./ai-agent.md)

## References

1. [Model Context Protocol — Tools](https://modelcontextprotocol.io/docs/concepts/tools) — tool declaration schema, lifecycle, and invocation model.
2. [`.github/copilot-instructions.md` §11](../.github/copilot-instructions.md) — MCP tool reference for this repository.
