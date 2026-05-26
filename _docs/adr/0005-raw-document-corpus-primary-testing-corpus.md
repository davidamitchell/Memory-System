# 0005 — raw_document_corpus/ as the primary latent-extraction testing corpus

Date: 2026-05-24
Status: accepted

## Context

During the W-0200/W-0201 implementation phase, the 26-file `glossary/` corpus was chosen as the ground-truth test bed for the pipeline because every concept, alias, tag, and relationship is explicitly declared in structured front-matter. This made it possible to validate the rule-based extractor (p07) with near-zero ambiguity.

Separately, a set of 50 research documents was assembled on the `copilot/ontology-experiment` branch under `raw_document_corpus/`. These documents contain substantive prose — research questions, scope sections, findings, and citations — with YAML front-matter using a different schema (`themes`, `cites`, `related` as slugs rather than the glossary's `tags`, `aliases`, `related[].file`). They are the natural next input corpus for latent extraction work (W-0204 onward).

The corpus was on a separate branch and was not referenced in the BACKLOG.md test plan, creating confusion about which documents were intended as the prose extraction target.

## Decision

Copy `raw_document_corpus/` from `copilot/ontology-experiment` into `main` (and all working branches derived from it) as a first-class directory. This directory is the **primary latent-extraction testing corpus** for W-0204 and beyond. The `glossary/` corpus retains its role as the structured ground-truth baseline for eval harness scoring (W-0203).

The `raw_document_corpus/` front-matter schema differs from the glossary schema:

| Field | Glossary | raw_document_corpus |
|---|---|---|
| Title | `title` | `title` |
| Keywords | `tags: [...]` | `themes: [...]` |
| Aliases | `aliases: [...]` | *(absent)* |
| Cross-refs | `related: [{file, rel}]` | `cites: [slug]` + `related: [slug]` |

Processors p05 and p06 are extended to recognise the `raw_document_corpus/` path prefix and assign it the `ResearchDocument` domain. Processor p07 tolerates missing `tags`/`aliases`/`related` by falling back gracefully; the LLM extractor (W-0204) is responsible for extracting semantic content from the prose body.

## Consequences

- The `raw_document_corpus/` directory (50 files, date-prefixed) is version-controlled on `main` and all feature branches going forward.
- The W-0204 LLM extractor is tested against at least one `raw_document_corpus/` file, with the resulting concept card inspected and recorded in `PROGRESS.md`.
- `BACKLOG.md` is updated: W-0204 references `raw_document_corpus/` as the prose target.
- The `copilot/ontology-experiment` branch remains available but is no longer the canonical location for these documents.

## References

1. [`BACKLOG.md` W-0203](../../BACKLOG.md) — eval harness; glossary remains the scoring ground truth.
2. [`BACKLOG.md` W-0204](../../BACKLOG.md) — LLM extractor; raw_document_corpus is the prose target.
3. [`raw_document_corpus/`](../../raw_document_corpus/) — the 50-file research document corpus.
