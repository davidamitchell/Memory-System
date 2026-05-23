---
title: "Capture"
category: concept
tags: [capture, write, memory, input, friction]
date: 2026-05-23
related:
  - term: "Memory File"
    file: memory-file.md
  - term: "Inbox"
    file: inbox.md
  - term: "MCP Tool"
    file: mcp-tool.md
  - term: "Retrieval"
    file: retrieval.md
aliases: ["memory capture", "write", "add memory"]
---

**The act of storing a new piece of knowledge as a memory file — the write side of the memory system, in contrast to retrieval.**

## Definition

Capture is the process of getting information into the memory system. It covers every mechanism by which a new memory file is created: typing into a chat with an AI agent, running a CLI command, using an iOS Shortcut, sending a Telegram message, or having an agent autonomously capture a decision it just made.

Capture friction — anything that makes it harder or slower to capture — is a primary engineering concern. A memory system that is effortful to write to will be underused. Design decisions in Open-Brain (the inbox pattern, the iOS Shortcut, the CLI `remember` command) are all motivated by reducing capture friction. The system treats startup latency, capture friction, and retrieval quality as first-class engineering concerns (BACKLOG-v2.md Vision).

The capture surface is the set of tools and interfaces through which memories enter the system. In the BACKLOG-v2.md architecture diagram, the capture layer sits above the MCP server.

## Usage in This System

- `add_memory(title, content, folder)` is the programmatic capture tool.
- The planned capture surfaces include: iOS Shortcut (W-0104), CLI `remember` command (W-0105), Telegram bot (W-0108), Slack bot (W-0109).
- The inbox pattern (W-0102) removes the folder-decision friction from the capture path.

## Related Terms

- [Memory File](./memory-file.md)
- [Inbox](./inbox.md)
- [MCP Tool](./mcp-tool.md)
- [Retrieval](./retrieval.md)

## References

1. [`BACKLOG-v2.md`](../BACKLOG-v2.md) — Vision and Architecture sections define capture as a first-class concern.
2. [`BACKLOG.md` W-0008–W-0013](../BACKLOG.md) — discovery items covering all viable capture surfaces.
