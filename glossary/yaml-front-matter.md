---
title: "YAML Front Matter"
category: format
tags: [yaml, front-matter, metadata, markdown]
date: 2026-05-23
related:
  - term: "Memory File"
    file: memory-file.md
    rel: partOf
  - term: "Tag"
    file: tag.md
    rel: uses
  - term: "Superseded-by"
    file: superseded-by.md
    rel: uses
aliases: ["front matter", "frontmatter", "YAML header"]
---

**A block of YAML key-value metadata at the very top of a Markdown file, delimited by `---` lines, that provides structured fields for indexing and retrieval.**

## Definition

YAML front matter is a convention for embedding structured metadata inside a plain-text Markdown file. The block starts and ends with a line containing only three dashes (`---`) and must appear before any other content in the file. The content between the delimiters is parsed as YAML.

Front matter fields are not rendered as content by most Markdown renderers (GitHub, Jekyll, etc.); they are consumed by tooling that processes the file. In this system, the fields drive indexing, filtering, and knowledge graph maintenance.

The required fields in every memory file are: `title` (human-readable display name), `date` (ISO 8601), `tags` (list of strings for categorisation), and `superseded_by` (path to a newer file if this one is out of date, or an empty string).

## Usage in This System

Every `.md` memory file must begin with:

```yaml
---
title: "Human-readable title"
date: YYYY-MM-DD
tags: [tag1, tag2]
superseded_by: ""
---
```

Definition files in `glossary/` use an extended schema defined in `definition_scheme.md`, which adds `category`, `related`, and `aliases` fields.

## Related Terms

- [Memory File](./memory-file.md)
- [Tag](./tag.md)
- [Superseded-by](./superseded-by.md)

## References

1. [YAML Specification](https://yaml.org/spec/1.2.2/) — the YAML language standard.
2. [Jekyll Front Matter](https://jekyllrb.com/docs/front-matter/) — the convention that popularised YAML front matter in Markdown files.
3. [`definition_scheme.md`](../definition_scheme.md) — the extended front matter schema for glossary definition files.
