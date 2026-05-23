---
title: "MCP Server"
category: entity
tags: [mcp, server, python, bridge]
date: 2026-05-23
related:
  - term: "Model Context Protocol"
    file: mcp.md
  - term: "MCP Tool"
    file: mcp-tool.md
  - term: "stdio Transport"
    file: stdio-transport.md
  - term: "LanceDB"
    file: lancedb.md
aliases: ["mcp_server.py", "open-brain server"]
---

**A process that implements the Model Context Protocol server side, exposing a named set of tools that AI clients can discover and call.**

## Definition

An MCP Server is a process that speaks the server side of the Model Context Protocol. It declares a list of tools — each with a name, description, and typed argument schema — that an MCP client can discover at connection time and invoke by name. The server handles each tool call, executes the underlying logic (database query, file write, API call), and returns a structured result.

In this repository, the MCP server is `mcp_server.py`. It runs locally on the developer's machine (or in a GitHub Actions sandbox during headless Copilot sessions). It combines three responsibilities: serving MCP tool calls, maintaining the LanceDB vector index, and watching the file system for changes to keep the index fresh.

MCP servers communicate with clients over a transport. The standard choice for local servers is stdio transport; for remote servers it is HTTP with SSE.

## Usage in This System

- `mcp_server.py` at the repo root is the sole MCP server implementation.
- It is launched via `.vscode/mcp.json` (both locally in VS Code and remotely in the Copilot sandbox).
- Cold-start performance of `mcp_server.py` is tracked as an explicit engineering constraint (see W-0100 in `BACKLOG-v2.md`).

## Related Terms

- [Model Context Protocol](./mcp.md)
- [MCP Tool](./mcp-tool.md)
- [stdio Transport](./stdio-transport.md)
- [LanceDB](./lancedb.md)

## References

1. [Model Context Protocol — Server Concepts](https://modelcontextprotocol.io/docs/concepts/servers) — what a server is, how it declares tools, and how the lifecycle works.
2. [`mcp_server.py`](../mcp_server.py) — the implementation in this repository.
