---
title: "Model Context Protocol"
category: protocol
tags: [mcp, protocol, ai, integration]
date: 2026-05-23
related:
  - term: "MCP Server"
    file: mcp-server.md
    rel: relatedTerm
  - term: "MCP Tool"
    file: mcp-tool.md
    rel: relatedTerm
  - term: "stdio Transport"
    file: stdio-transport.md
    rel: relatedTerm
  - term: "AI Agent"
    file: ai-agent.md
    rel: relatedTerm
aliases: ["MCP"]
---

**An open standard that lets AI assistants call external tools and data sources through a structured interface, replacing one-off integrations with a single universal protocol.**

## Definition

The Model Context Protocol (MCP) is an open standard introduced by Anthropic in 2024 that defines how AI assistants — such as Claude, GitHub Copilot, and Cursor — communicate with external tools and data sources. Before MCP, every AI application needed bespoke integration code for every tool it wanted to call. MCP replaces that fragmentation with a single client–server protocol: an MCP client (embedded in the AI assistant) connects to an MCP server (a process that exposes tools), and the two communicate over a defined JSON-RPC message format.

The protocol operates over a transport layer — most commonly stdio for local servers or HTTP/SSE for remote servers. The server declares which tools it provides; the client discovers them at connection time and calls them by name with typed arguments.

MCP is explicitly "agent-native": it is designed so that AI agents can autonomously decide when to call a tool, what arguments to pass, and how to interpret the result — without requiring the human user to manually orchestrate each call.

## Usage in This System

- `mcp_server.py` is the MCP server for this repository. It exposes three tools (`search_brain`, `add_memory`, `refactor_memory`) to any MCP-compatible client.
- `.vscode/mcp.json` configures VS Code and the GitHub Copilot coding agent to connect to `mcp_server.py` via stdio transport.
- `.github/copilot-setup-steps.yml` ensures `mcp_server.py` is installed and the embedding model is pre-warmed before the Copilot agent begins its session.

## Related Terms

- [MCP Server](./mcp-server.md)
- [MCP Tool](./mcp-tool.md)
- [stdio Transport](./stdio-transport.md)
- [AI Agent](./ai-agent.md)

## References

1. [Model Context Protocol — Official Documentation](https://modelcontextprotocol.io/) — specification, architecture overview, and SDK references.
2. [Anthropic: Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) — original announcement and design rationale.
