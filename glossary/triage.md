---
title: "Triage"
category: practice
tags: [triage, inbox, classification, automation]
date: 2026-05-23
related:
  - term: "Inbox"
    file: inbox.md
  - term: "Capture"
    file: capture.md
  - term: "Memory File"
    file: memory-file.md
  - term: "AI Agent"
    file: ai-agent.md
aliases: ["inbox triage", "memory triage", "classification"]
---

**The process of reviewing inbox files, inferring the correct destination folder and front matter, and moving each file to its permanent location.**

## Definition

Triage is the second step of the inbox pattern. After items are captured into `/inbox` without a folder decision, a triage step processes them: an agent (or the human owner) reads each inbox file, decides whether it belongs in `meetings/`, `journal/`, or `projects/`, writes or completes its front matter (title, date, tags), and moves the file to its destination.

Triage decouples the two concerns that create capture friction: getting the information into the system (must be instant) and organising it correctly (can be deferred). By separating these, the inbox pattern eliminates the "what folder does this go in?" decision from the capture moment.

Triage can be run on demand (by asking an agent to "process the inbox") or on a schedule (a weekly automated agent pass). W-0103 in BACKLOG.md covers the implementation of automated triage.

## Usage in This System

- Triage is a planned feature (not yet implemented) dependent on W-0102 (inbox folder).
- The triage agent will use `search_brain` to find similar existing memories before classifying a new one, to avoid duplication.

## Related Terms

- [Inbox](./inbox.md)
- [Capture](./capture.md)
- [Memory File](./memory-file.md)
- [AI Agent](./ai-agent.md)

## References

1. [`BACKLOG.md` W-0012](../BACKLOG.md) — the original inbox/triage discovery item.
2. [`BACKLOG.md` W-0102–W-0103](../BACKLOG.md) — shaped build items for inbox and triage automation.
