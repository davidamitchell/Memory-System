---
title: "MCP Server"
category: entity
tags: [mcp, server, python, bridge]
date: 2026-05-23
related:
  - term: "Model Context Protocol"
    file: mcp.md
    rel: implements
  - term: "MCP Tool"
    file: mcp-tool.md
    rel: relatedTerm
  - term: "stdio Transport"
    file: stdio-transport.md
    rel: uses
aliases: ["mcp_server.py", "open-brain server"]
---

**A process that implements the Model Context Protocol server side, exposing a named set of tools that AI clients can discover and call.**

## Definition

An MCP Server is a process that speaks the server side of the Model Context Protocol. It declares a list of tools — each with a name, description, and typed argument schema — that an MCP client can discover at connection time and invoke by name. The server handles each tool call, executes the underlying logic (database query, file write, API call), and returns a structured result.

MCP servers communicate with clients over a transport. The standard choice for local servers is stdio transport; for remote servers it is HTTP with SSE.

## Usage in This System

- `mcp_server.py` at the repo root is a **legacy prototype** from the original vector-storage design. It is not the target system.
- The ontology-based MCP server is not yet built. Its tool interface will be defined and recorded in an ADR as part of implementation. See `_docs/design/ontology-system-design.md` for the architecture.
- `.vscode/mcp.json` currently points to `mcp_server.py`; this will be updated when the ontology server is implemented.

## Related Terms

- [Model Context Protocol](./mcp.md)
- [MCP Tool](./mcp-tool.md)
- [stdio Transport](./stdio-transport.md)

## References

1. [Model Context Protocol — Server Concepts](https://modelcontextprotocol.io/docs/concepts/servers) — what a server is, how it declares tools, and how the lifecycle works.
2. [`_docs/design/ontology-system-design.md`](../_docs/design/ontology-system-design.md) — target system architecture the MCP server will expose.
