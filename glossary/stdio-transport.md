---
title: "stdio Transport"
category: protocol
tags: [stdio, transport, mcp, ipc, protocol]
date: 2026-05-23
related:
  - term: "Model Context Protocol"
    file: mcp.md
  - term: "MCP Server"
    file: mcp-server.md
aliases: ["stdio", "standard input/output transport"]
---

**The MCP transport mechanism that uses a process's standard input and standard output streams to exchange JSON-RPC messages between an MCP client and server.**

## Definition

stdio transport is one of the two standard transport mechanisms defined by the Model Context Protocol (the other being HTTP with Server-Sent Events). When using stdio, the MCP client spawns the MCP server as a child process and communicates with it by writing JSON-RPC messages to the server's stdin and reading responses from its stdout.

Because stdio transport requires the server to be a locally runnable process, it is the natural choice for local-first applications. There is no port to manage, no HTTP server to configure, and no authentication layer needed — the OS enforces process isolation. The client simply knows the command to run (`python mcp_server.py`) and the protocol takes care of the rest.

The limitation is that stdio transport only works when the client and server are on the same machine (or in the same ephemeral sandbox). For remote access, HTTP/SSE transport is required.

## Usage in This System

- `.vscode/mcp.json` configures the MCP client (VS Code Copilot or the headless Copilot sandbox) to launch `mcp_server.py` via stdio:
  ```json
  { "type": "stdio", "command": "python", "args": ["mcp_server.py"] }
  ```
- This configuration works identically in a local VS Code session and in the GitHub Actions sandbox spun up for headless Copilot mode.

## Related Terms

- [Model Context Protocol](./mcp.md)
- [MCP Server](./mcp-server.md)

## References

1. [MCP Specification: Transports](https://modelcontextprotocol.io/docs/concepts/transports) — official description of stdio and HTTP/SSE transport options.
