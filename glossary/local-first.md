---
title: "Local-first"
category: concept
tags: [local-first, architecture, offline, privacy, design]
date: 2026-05-23
related:
  - term: "Open-Brain"
    file: open-brain.md
    rel: relatedTerm
  - term: "LanceDB"
    file: lancedb.md
    rel: relatedTerm
  - term: "Agent-first"
    file: agent-first.md
    rel: relatedTerm
aliases: ["local first", "offline-first"]
---

**A software design philosophy in which the user's local device is the primary source of truth, with cloud storage used for backup and sync rather than as the authoritative store.**

## Definition

Local-first is a design principle, articulated by Ink & Switch in 2019, which holds that software should work fully offline, respond instantly (no network round-trips for core operations), and keep the user's data under their control on their own hardware. Cloud services are additive — they provide backup, sync, and sharing — but the application does not break or degrade if the cloud is unavailable.

The contrast is with "cloud-first" or "SaaS" architectures where the user's data lives primarily in a vendor's database and the local application is a thin client. If the vendor's service goes down, the user loses access to their own data.

For a memory system, local-first has concrete consequences: search should be fast and offline-capable (hence an embedded local vector database), writes should be instantaneous (no waiting for a remote API), and the data should be readable and editable without any application at all (hence plain Markdown files in a git repository).

## Usage in This System

- The README describes Open-Brain as "a local-first, agent-native memory system".
- LanceDB's embedded architecture (`.lancedb/` is a local folder, not a cloud endpoint) is the direct implementation of the local-first principle for the vector index.
- The `.md` files in the git repository are the implementation for the source-of-truth data layer.

## Related Terms

- [Open-Brain](./open-brain.md)
- [LanceDB](./lancedb.md)
- [Agent-first](./agent-first.md)

## References

1. [Ink & Switch: Local-first Software (2019)](https://www.inkandswitch.com/local-first/) — the foundational essay that defined and popularised the local-first design philosophy.
