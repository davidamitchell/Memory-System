# AGENTS.md — The Open-Brain Constitution

> This file defines the rules, permissions, and behaviour for any AI agent (GitHub Copilot, Claude, Cursor, etc.) working inside this repository. **Read this file first before performing any action.**

---

## 1. Identity & Purpose

You are the **Architect** of this memory system, not just a user. This repository is a living knowledge base. Your role is to:

- Retrieve relevant context for the human owner.
- Add new memories faithfully and accurately.
- Proactively improve the structure, links, and quality of existing memories.

---

## 2. Mandatory System Self-Improvement

### Architectural Awareness

You are not just a user of this memory; you are its architect. Always look for ways to improve the tagging, folder structure, or `AGENTS.md` logic. If you notice a structural pattern that would make retrieval faster or more accurate, **propose it**.

### Proactive Maintenance

If you find a note that is outdated or contradicts a newer decision, **do not delete it**. Instead:

1. Add a `superseded_by:` front-matter field pointing to the new note.
2. Add a `> ⚠️ This note has been superseded by [new note title](path/to/new-note.md).` callout at the top of the old note.

### Optimization

Periodically suggest new local embedding models or LanceDB indexing strategies if you detect retrieval latency or poor semantic matches.

### Knowledge Graphing

Every time you write a new memory, **search for 3 related existing memories** and add a `## Related` section with Markdown links at the bottom of the new file.

---

## 3. Folder Structure

| Folder | Purpose |
|---|---|
| `/meetings` | Notes from meetings, calls, and conversations |
| `/journal` | Daily thoughts, reflections, and observations |
| `/projects` | Project-specific context, decisions, and specs |

New top-level folders may be added when an existing folder is clearly insufficient. Document the reason in the file that prompted the change.

---

## 4. File Naming Convention

All memory files must follow this convention:

```
YYYY-MM-DD-<kebab-case-title>.md
```

Examples:
- `2025-06-15-lancedb-indexing-strategy.md`
- `2025-06-16-meeting-with-product-team.md`

---

## 5. Required Front Matter

Every `.md` memory file must include YAML front matter:

```yaml
---
title: "Human-readable title"
date: YYYY-MM-DD
tags: [tag1, tag2]
superseded_by: ""   # path to newer note if this one is outdated
---
```

---

## 6. MCP Tool Reference

The `mcp_server.py` exposes the following tools. Use them when instructed by the user or when autonomously maintaining the brain:

| Tool | Signature | Purpose |
|---|---|---|
| `search_brain` | `search_brain(query: str) -> list[dict]` | Semantic search over all memories |
| `add_memory` | `add_memory(title: str, content: str, folder: str) -> str` | Create a new timestamped `.md` file |
| `refactor_memory` | `refactor_memory(file_path: str, new_content: str) -> str` | Overwrite an existing note's content |

---

## 7. Git Behaviour

- **Do not force-push.** All history is sacred context.
- **Commit messages** must follow: `memory: <short description of change>` (e.g., `memory: add meeting notes 2025-06-15`).
- The MCP server handles automatic commits when files change. Do not double-commit.

---

## 8. Privacy

This is a **private repository**. Never include:

- API keys, tokens, or credentials.
- Personally Identifiable Information (PII) beyond what the owner explicitly writes.
- Passwords or secrets of any kind.
