---
title: "Inbox"
category: entity
tags: [inbox, capture, triage, folder]
date: 2026-05-23
related:
  - term: "Memory File"
    file: memory-file.md
    rel: relatedTerm
  - term: "Capture"
    file: capture.md
    rel: partOf
  - term: "Triage"
    file: triage.md
    rel: relatedTerm
  - term: "Open-Brain"
    file: open-brain.md
    rel: partOf
aliases: ["inbox folder", "capture inbox"]
---

**A designated `/inbox` folder where memory files can be dropped without a folder decision, title, or full front matter, for later classification by an agent.**

## Definition

The inbox is a frictionless capture drop zone. The design insight behind it is that requiring a writer to choose a destination folder and write full front matter at capture time adds friction that discourages capture. An inbox removes that decision: anything can be dropped into `/inbox` immediately, and a separate triage step — automated by an agent or deferred to a low-urgency session — moves each item to its correct folder with proper metadata.

The inbox is not for permanent storage. Files that land there are transient: a triage agent periodically reads the inbox, infers a folder (`meetings/`, `journal/`, `projects/`), writes appropriate front matter, and moves the file. The inbox thus decouples capture latency (must be zero) from classification quality (can be slow and careful).

This pattern is described in BACKLOG.md W-0012 and shaped into a build item as W-0102 in BACKLOG.md. It is not yet implemented.

## Usage in This System

- `/inbox` does not yet exist in the repository (pending W-0102).
- Once implemented, any capture tool (iOS Shortcut, CLI, Telegram bot) can write to `/inbox` without needing to specify a folder.
- The `add_memory` MCP tool will accept `folder: "inbox"` as a valid target.

## Related Terms

- [Memory File](./memory-file.md)
- [Capture](./capture.md)
- [Triage](./triage.md)
- [Open-Brain](./open-brain.md)

## References

1. [`BACKLOG.md` W-0012](../BACKLOG.md) — discovery item defining the inbox pattern.
2. [`BACKLOG.md` W-0102](../BACKLOG.md) — shaped build item for inbox implementation.
