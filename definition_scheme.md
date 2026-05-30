# Definition Scheme

This file defines the mandatory schema every file in `foundational_concepts/` must follow.
It is the single source of truth for structure, required fields, and cross-linking rules.
Any agent creating or editing a definition file must read this file first.

---

## Requirements

### 1. File location

All definition files live in `foundational_concepts/`.
Filename must be `<kebab-case-term>.md` (lower-case, hyphens, no spaces).

Examples: `foundational_concepts/ontology.md`, `foundational_concepts/concept.md`, `foundational_concepts/syntax.md`

### 2. Required YAML front matter

Every definition file must open with this front matter block:

```yaml
---
title: "Human-readable term name"
category: <one of the categories listed below>
tags: [tag1, tag2]
date: YYYY-MM-DD
related:
  - term: "Related Term"
    file: related-term.md
aliases: []          # alternative names or abbreviations for this term
---
```

All fields are mandatory. Use `[]` for empty lists.

**Category values** (pick exactly one):

| Category | Use for |
|---|---|
| `protocol` | Communication standards and specifications (MCP, HTTP, stdio) |
| `tool` | Named external software, databases, or services (LanceDB, sentence-transformers) |
| `concept` | Abstract ideas and design patterns (semantic search, local-first, knowledge graph) |
| `format` | File formats and data structures (YAML front matter, MADR, Markdown) |
| `practice` | Workflows, processes, and conventions (ADR, mini-retro, triage) |
| `entity` | Concrete objects in the system (memory file, inbox, skill) |
| `project` | Named projects or systems defined in this repo (Open-Brain) |

### 3. Required sections (in order)

Every definition file must contain these sections in this exact order:

#### § One-line definition

Immediately after the YAML front matter, before any section heading, write a single bold sentence that defines the term. This is the summary a reader sees without scrolling.

```markdown
**Short definition in one sentence.**
```

#### § `## Definition`

Two to four paragraphs. Cover:
- What the term means in this system's context
- Why it exists / what problem it solves
- How it is used in practice within this repository

Do not duplicate the one-line definition. Expand on it.

#### § `## Usage in This System`

One to three bullet points showing concretely how the term appears or is used in this repository. Reference specific files, tools, or configurations where relevant.

#### § `## Related Terms`

Bullet list of related terms with links to their definition files.
Use relative paths: `[Term Name](./other-term.md)`.
Minimum one entry. If no related terms exist yet, link to the most conceptually adjacent term and note the gap.

#### § `## References`

Numbered list of external sources. Minimum one canonical source. Format:

```
1. [Title](URL) — one-line description of what this source covers.
```

If no external URL exists, cite the relevant file in this repository:
```
1. [`path/to/file.md`](../path/to/file.md) — description.
```

### 4. Cross-linking rule (Wikipedia style)

When a defined term appears in **any** file in this repository:
- Link it **on its first occurrence only** in that file.
- Do not link it again in the same file (not in headers, not in the same section, not in code blocks).
- Use the relative path from the file's location to `foundational_concepts/`.
  - From repo root: `[Term](./foundational_concepts/term.md)`
  - From a first-level subfolder (`projects/`, `journal/`, etc.): `[Term](../foundational_concepts/term.md)`
  - From a second-level subfolder (`_docs/adr/`): `[Term](../../foundational_concepts/term.md)`
- Do not link terms inside YAML front matter, code blocks, or inline code spans.

### 5. Aliases

If a term has common abbreviations or alternative names (e.g. MCP → "Model Context Protocol", ADR → "Architecture Decision Record"), list them in the `aliases` field in the front matter. Agents and writers should cross-link any alias to the same definition file as the canonical term.

### 6. Naming consistency

The `title` field in the front matter is the canonical display name for the term.
Use this exact string everywhere the term is mentioned in prose (including links), not the filename slug.

### 7. Adding a new term — checklist

- [ ] File created in `foundational_concepts/<kebab-case>.md`
- [ ] All front matter fields present and valid category used
- [ ] One-line bold definition present
- [ ] All four required sections present in correct order
- [ ] Minimum one external reference
- [ ] New entry added to `foundational_concepts/README.md` index table
- [ ] First occurrence of the term cross-linked in any files where it appears

### 8. Updating an existing term

- Edit the definition file in place.
- If the meaning changes substantially, note the old meaning in `## Definition` and explain the change.
- Do not delete history — this is a living knowledge base.
- Update `foundational_concepts/README.md` if the category or title changes.

---

## References

1. [Wikipedia: Manual of Style — Linking](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Linking) — the Wikipedia first-use linking convention this scheme is modelled on.
2. [`glossary/README.md`](./glossary/README.md) — index of all defined terms.
3. [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) — agent constitution that requires glossary use.
