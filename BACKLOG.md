---
title: "BACKLOG — Implementation-Ready Roadmap"
date: 2026-03-13
tags: [backlog, roadmap, architecture, planning]
superseded_by: ""
---

# BACKLOG — Implementation-Ready Roadmap

> Items are ordered top-to-bottom: highest priority at the top, dependencies respected.
> Discovery items from the earlier research phase are preserved in the [Historical Discovery Items](#historical-discovery-items) appendix at the bottom of this file.

---

## Vision

The memory system is an ontology-based knowledge graph that makes personal and research knowledge queryable and traversable. Input begins with documents from the Research repository — markdown files with structured front-matter processed through a 12-processor pipeline into a queryable RDF knowledge graph stored as Turtle. The system is agent-native, local-first, and designed to improve the quality of its own structure over time. Additional input sources may be added in the future; the pipeline's input/output interface is stable and source-agnostic.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                             │
│   glossary/ (active)  ·  Research repository docs (next)      │
│   Additional sources: to be determined                        │
└────────────────────────────┬───────────────────────────────────┘
                             │  pipeline/run_pipeline.py <path>
┌────────────────────────────▼───────────────────────────────────┐
│                    12-PROCESSOR PIPELINE                       │
│   1 Ingest · 2 Parse · 3 Segment · 4 Provenance               │
│   5 Domain · 6 Entity · 7 Relation · 8 Assertion Node         │
│   9 Validate · 10 Reconcile · 11 Version Commit · 12 Export   │
└─────────────────────────────────────────────────────────────────┘
                             │  data/ontology/vNNNN.ttl
┌────────────────────────────▼───────────────────────────────────┐
│                        QUERY LAYER                             │
│   pipeline/query.py (SPARQL via rdflib)                        │
│   Future: MCP tools — ontology server not yet implemented     │
└────────────────────────────────────────────────────────────────┘
```

Documents enter the pipeline via `pipeline/run_pipeline.py`. Each document flows through all 12 processors and produces a versioned Turtle file in `data/ontology/`. The query layer runs SPARQL queries via rdflib against the Turtle graph; the same `.rq` query files will work unchanged against any external SPARQL endpoint when the graph store is upgraded. The legacy vector prototype (`mcp_server.py`) is not the target architecture — see ADR-0002.

---

## Research Cross-Reference

| Research item | Informs |
|---|---|
| `_docs/adr/0002-move-from-vector-storage-to-ontology.md` | W-0200, W-0201 |
| `_docs/adr/0003-ontology-architecture.md` | W-0200, W-0201 |
| `_docs/adr/0004-provenance-model-and-control-plane.md` | W-0200, W-0201, W-0202 |
| `_docs/design/ontology-system-design.md` | W-0200, W-0201, W-0202 |

---

## Outstanding Discovery

No discovery items are blocking active work. The deferred capture-surface items (W-0102–W-0115) have their own discovery prerequisites recorded in their individual entries and can be revisited when capture-surface work is prioritised.

---

## Phase 1 — Ontology pipeline: thin slices

> Build the 12-processor pipeline end-to-end, starting with the glossary corpus, then expanding to Research repository documents.

---

> Two additive vertical slices through all 12 processors. Each goes **deep and thin**: every processor fires on every run; none are skipped or deferred to a later item. The goal is a working seam from raw markdown to a CLI-queryable ontology before any processor is hardened.
>
> **Reversibility principle:** every technical choice in this phase is made to keep all doors open. rdflib can be swapped for any SPARQL endpoint without changing a single query. Turtle can be converted to JSON-LD or OWL in one call. The `ms:` namespace can be aligned to BFO or schema.org incrementally via `owl:equivalentClass`. Rule-based domain classification can be replaced by an LLM without changing the processor interface. Nothing in this phase requires a server, a cloud service, or an irreversible schema commitment.

---

## W-0200

status: done
created: 2026-05-23
updated: 2026-05-23
completed: 2026-05-23
blocks: [W-0201]
blocked-by: []
research: [_docs/adr/0004-provenance-model-and-control-plane.md, _docs/design/ontology-system-design.md]
assumptions:
  - rdflib is sufficient for the in-memory graph (no triple-store server required); if performance is unacceptable at 26 files, W-0201 migrates — but this is tested, not assumed
  - Glossary files (26 files, one concept each, structured front-matter with title/tags/related/aliases) are the right input corpus: curated, small, already linked to each other
  - The `related:` front-matter field contains the graph edges; extracting them as `ms:relatedTerm` triples is free and high-value
  - One body paragraph = one Prepared Segment (SHA-256 addressed); sub-paragraph splitting is deferred
  - Domain classification is rule-based: path prefix `glossary/` → domain signal `Vocabulary` (ML/LLM classification is deferred but the processor interface is stable)
  - Version "commit" = write a numbered `.ttl` file to `data/ontology/`; the git commit of that file is the immutable snapshot
  - Confidence weighting is deferred (Open Question Q1 from ADR-0004); `source_authority=authoritative` is assigned to all glossary files in this iteration
  - The CLI query tool uses SPARQL SELECT via rdflib; the same `.rq` files will work unchanged against any external SPARQL endpoint (Oxigraph, Fuseki, AllegroGraph) when the store is upgraded
reversibility:
  - rdflib → any SPARQL endpoint: zero query changes; only the graph load call changes
  - Turtle → JSON-LD: one `rdflib.Graph().serialize(format="json-ld")` call
  - `ms:` namespace → BFO/schema.org alignment: add `owl:equivalentClass` statements; existing triples remain valid
  - Rule-based domain → LLM domain: swap the classifier function; processor 5's input/output interface is unchanged
  - argparse CLI → MCP tool: the query functions are imported directly; only the entry point changes
doors-kept-open:
  - No triple-store server is introduced (keeps local-first)
  - No confidence score is committed to storage (open question stays open)
  - No upper ontology import (BFO/SUMO/schema.org) is added (alignment can happen later without migration)
  - No custom non-RDF format is written (all tooling remains compatible)
  - Segment files are tracked in git unmodified (no gitignore); this preserves the option explored in W-0202 — git's own object store may be the Resolver Service
uncertainty:
  - Whether rdflib in-memory holds at 26 files (measured in this slice — if not, W-0201 adds Oxigraph)
  - Whether `ms:relatedTerm` edges form a connected graph or produce isolated islands (measured by the CLI query output)

### Outcome

`pipeline/run_pipeline.py glossary/vector-embedding.md` runs end-to-end through all 12 processors and produces `data/ontology/v0001.ttl`. `pipeline/query.py "vector embedding"` prints a concept card to the terminal. Both commands complete in under 5 seconds. The Turtle file is inspectable by eye and parseable by any RDF tool.

**What this unlocks:** the first time the system produces a human-readable, machine-queryable representation of a concept that traces back to its source document. Every processor is wired; none are hypothetical.

**Experiments answered by this slice:**
- **Q7 (representation format):** does rdflib hold as the working representation? Answered by whether the slice passes or requires a workaround.
- **Q6 (upper ontology seeding):** do the 26 glossary terms find homes in a minimal `ms:VocabularyDomain` node, or does BFO vocabulary appear immediately necessary? Answered by writing the first domain node and observing friction.

### Context

ADR-0004 defined the pipeline and provenance model conceptually. Until one file flows end-to-end to a queryable output, every decision is theoretical. This slice validates the seam. It deliberately uses `glossary/vector-embedding.md` as the input because that file has rich `related:` edges (4 links), aliases, and a body that is easy to verify by eye. The CLI query is included in this slice — not deferred — because "a Turtle file exists" is not user-visible value; "I can type a term and see its card" is.

The `glossary/` folder contains 26 files with consistent YAML front-matter. Each has a `related:` field listing linked terms with `file:` references — these are the graph edges available for free. Extracting them here means W-0201 gets a real graph with ~50+ edges to traverse, not a flat list of isolated nodes.

### Acceptance criteria

- `pipeline/run_pipeline.py <path>` runs without error against `glossary/vector-embedding.md`
- All 12 processors are implemented as distinct Python functions/classes; none are absent or silently skipped; each logs its processor number and name on execution
- The output `data/ontology/v0001.ttl` is valid Turtle (parseable by `rdflib.Graph().parse(...)`)
- The output contains:
  - One `ms:AssertionNode` per concept, with `rdfs:label` (title), `rdfs:comment` (first paragraph of body), and `ms:aliases` (from front-matter `aliases:`)
  - `ms:relatedTerm` triples for each entry in the `related:` front-matter field (4 edges for `vector-embedding.md`)
  - `ms:hasTag` triples for each tag in the `tags:` field
  - One `prov:wasGeneratedBy` link to an `ms:ExtractionActivity`
  - One `prov:used` link from the activity to the `ms:PreparedSegment`
  - The segment carries `ms:contentHash` (`sha256:<hex>` of the body text) and `ms:sourceDocument` (relative path to the `.md` file)
- Processor 9 (Consistency Validation) produces a validation report with zero conflicts; the report is written to `data/reports/validation-v0001.json`
- Processor 10 (Reconciliation) logs "no conflicts to reconcile — no-op" and exits cleanly
- `data/segments/<sha256-hex>.txt` exists containing the raw body text used as evidence
- `pipeline/query.py "vector embedding"` (exact or partial match on `rdfs:label` or `ms:aliases`) prints a terminal concept card:
  ```
  ── Vector Embedding ─────────────────────────────────────
  Definition : A fixed-length list of numbers that encodes…
  Aliases    : embedding, text embedding, vector representation
  Tags       : embedding, vector, nlp, representation
  Related    : Embedding Model · Semantic Search · Vector Database · LanceDB
  Evidence   : data/segments/e3b0c4…txt (sha256:e3b0c4…)
  Source     : glossary/vector-embedding.md
  ─────────────────────────────────────────────────────────
  ```
- The SPARQL query used by `query.py` is saved as `pipeline/queries/concept_card.rq` (plain `.rq` file, portable to any SPARQL endpoint)
- `pipeline/README.md` documents: how to run the pipeline, how to run a query, the processor list, and the `ms:` namespace prefix table
- Integration test `tests/test_pipeline_w0200.py` runs the pipeline against `glossary/vector-embedding.md`, asserts valid Turtle, asserts the expected triple count (label + comment + 4 related + 4 tags + provenance chain = ≥12 triples), and asserts `query.py "vector embedding"` exits 0 and prints "Vector Embedding"

---

## W-0201

status: done
created: 2026-05-23
updated: 2026-05-23
blocks: []
blocked-by: []
research: [_docs/adr/0004-provenance-model-and-control-plane.md]
assumptions:
  - The Turtle format established in W-0200 is stable; W-0201 only extends it (additive)
  - All 26 glossary files share the same front-matter schema; no file will require a new processor branch
  - The `related:` edges across all 26 files form a mostly-connected graph (the glossary was written with cross-links); this is tested, not assumed
  - rdflib remains the in-memory representation; if load time exceeds 5 seconds for 26 files, the fix is Oxigraph (a drop-in replacement with the same SPARQL interface)
reversibility:
  - All W-0200 reversibility notes carry forward unchanged
  - `--format json` output from `query.py` is the future MCP tool response shape; switching to MCP requires no format changes
  - Version diff is a plain text log; it can be structured as JSON later without changing the Version Commit Processor interface
doors-kept-open:
  - No persistence layer change (still rdflib + file); the store upgrade decision is informed by the measured load time from this slice
  - No domain classification upgrade (still rule-based); the multi-domain count from this slice informs whether ML is needed
  - No upper ontology import added
uncertainty:
  - Whether any of the 26 files triggers a duplicate-label conflict in Processor 9 (the glossary was hand-authored; near-synonyms like "ai-agent" and "agent-first" may share labels)
  - Whether `ms:relatedTerm` edges across all 26 files form a connected graph or fragment into islands (measured by the `--related` query)

### Outcome

`pipeline/run_pipeline.py glossary/` processes all 26 files in batch mode (p01–p08 per file, p09–p12 once), producing a single unified ontology version. `pipeline/query.py --related "vector embedding"` traverses the graph and prints a two-hop concept neighbourhood. `pipeline/query.py --format json "mcp"` outputs JSON, demonstrating the pivot format for automated testing.

**Measured results (2026-05-23):**
- 26 `ms:AssertionNode` subjects, 83 `ms:relatedTerm` directed edges, 838 total triples
- rdflib graph load time: 0.026 s (well below 5 s threshold — no Oxigraph upgrade needed)
- 0 duplicate-label conflicts; 0 domain tie-breaks required (all 26 files → VocabularyDomain)
- 16/16 acceptance tests passing (9 W-0200 + 7 W-0201)

**What this unlocks:** the graph edges are live. You can navigate from any concept to its neighbours. The CLI is the first working query interface over the full ontology, and the JSON output format is the exact shape a future MCP tool or test harness will consume.

**Experiments answered by this slice:**
- **Q5 (multi-domain documents):** how many of the 26 files produce >1 domain signal? If >30%, a resolution strategy is load-bearing. Measured by Processor 5 log output.
- **Q4 (version commit trigger):** the diff between v0001 (1 file) and v0002 (26 files) makes the per-commit vs batch question concrete — the diff output is the evidence.
- **Q7 (representation format, continued):** rdflib load time for 26 files is measured; if >5 seconds, the upgrade path to Oxigraph is triggered here (not deferred to a future item).

### Context

W-0200 validated the pipeline seam with one file and produced a queryable concept card. W-0201 makes the graph real by ingesting all 26 glossary files and wiring their cross-references. The `related:` links in the glossary amount to ~80 directed edges across 26 nodes — a real graph, not a toy. The `--related` traversal query is the first time the system demonstrates graph navigation rather than flat lookup. The `--format json` flag is deliberately included here as the testing pivot: every acceptance criterion that checks CLI output can be verified with `json.loads()` rather than terminal parsing.

The version diff (v0001 → v0002) is the first concrete answer to the "what triggers a commit" open question: seeing 25 files → 25 × N triples added in one diff makes the batch-vs-per-ingest decision legible.

### Acceptance criteria

- `pipeline/run_pipeline.py glossary/` processes all 26 `.md` files in a single pass without error
- The output `data/ontology/v0002.ttl` contains one `ms:AssertionNode` per glossary file (26 nodes) and all `ms:relatedTerm` edges from all `related:` fields (expected: ~80 directed edges)
- The Version Commit Processor prints a diff to stdout: `v0001 → v0002: +N triples, 0 removed` and writes `data/reports/diff-v0001-v0002.json` with structured additions/removals
- Processor 5 (Domain Classification) logs, for each file: the domain signal(s) detected and whether a tie-break was applied; if any file produced >1 signal, the tie-break rule is documented in `pipeline/README.md` and the count is logged as a summary line
- Processor 9 (Consistency Validation) checks for duplicate `rdfs:label` values across all 26 nodes; if any are found, they are surfaced as structured conflicts in `data/reports/validation-v0002.json` (not a crash)
- `pipeline/query.py --related "vector embedding"` traverses `ms:relatedTerm` edges up to two hops and prints a neighbourhood card:
  ```
  ── Vector Embedding (neighbours) ────────────────────────
  Direct   : Embedding Model · Semantic Search · Vector Database · LanceDB
  Via Embedding Model : BAAI/bge-small-en-v1.5 · …
  ─────────────────────────────────────────────────────────
  ```
- `pipeline/query.py --format json "vector embedding"` outputs valid JSON with keys `label`, `definition`, `aliases`, `tags`, `related`, `evidence`; `json.loads()` on the output does not raise
- `pipeline/query.py --format json --related "vector embedding"` outputs valid JSON with key `neighbours` (list of concept objects up to two hops)
- The SPARQL queries used by `--related` and `--format json` are saved as `pipeline/queries/neighbours.rq` and `pipeline/queries/concept_json.rq`
- `pipeline/README.md` is updated with: multi-file usage, `--related` and `--format` flag docs, the version diff format, and the domain tie-break rule (if applied)
- Integration test `tests/test_pipeline_w0201.py` asserts: 26 nodes in `v0002.ttl`, `--format json` output is valid JSON, `--related` output contains at least one second-hop neighbour, and `diff-v0001-v0002.json` reports >0 additions

---

## W-0207

status: done
created: 2026-05-24
updated: 2026-05-25
blocks: [W-0203]
blocked-by: [W-0201]
research: []
assumptions:
  - The latest `data/ontology/v*.ttl` file is the canonical snapshot to export
  - rdflib is already a declared dependency (requirements.txt)
  - GitHub Pages can be enabled on this repository and serves from the `docs/` directory
  - The 26 glossary concept IDs map directly to their source filenames (e.g. `adr` → `glossary/adr.md`), allowing the document→concept link to be derived without prov triples
uncertainty:
  - Whether the GitHub Pages environment needs to be manually enabled in repository settings before the workflow can deploy
  - Whether the single shared `prov:wasGeneratedBy` activity (batch mode) is sufficient for the browser, or whether per-concept provenance should be added in a later pass

### Outcome

A GitHub Pages site at `https://davidamitchell.github.io/Memory-System/` that lets you browse the ontology without local tooling. Four tabs: Overview (counts, version), Concepts (table with detail panel), Relations (edge list), Documents (source files + segment counts). The site is a progressively-enhanced static page: plain HTML tables work without JS; JS adds tab switching, live search, and a concept detail panel.

### Context

The pipeline (W-0200/W-0201) produces a versioned Turtle file but provides no way to explore it without running local Python. This item adds a zero-dependency, always-on browser that is regenerated automatically on every push to `main`. It makes the ontology inspectable for humans and serves as a lightweight integration test: if the exporter runs without error and produces a page with correct counts, the pipeline data is structurally sound.

Two new pipeline scripts handle the export:
- `pipeline/export_json.py` — parses the latest TTL and emits `docs/data/ontology.json`
- `pipeline/export_html.py` — stamps the JSON into `docs/index.html` (pre-rendered tables, no JS required)

`docs/style.css` and `docs/app.js` provide the visual layer and progressive enhancements. The GitHub Actions workflow `.github/workflows/pages.yml` runs both exporters and deploys on every push to `main`.

### Acceptance criteria

- `python pipeline/export_json.py` produces `docs/data/ontology.json` with correct counts (26 concepts, 83 relations, 26 documents for the W-0201 corpus)
- `python pipeline/export_html.py` produces `docs/index.html` that is valid HTML and renders all four sections without JS
- `docs/style.css` and `docs/app.js` are present; the page enhances correctly with JS enabled
- `.github/workflows/pages.yml` deploys to GitHub Pages on push to `main`
- The deployed site is navigable: Overview counts match the ontology, Concepts table shows all 26 nodes, Relations table shows all 83 edges, Documents table shows all 26 source files
- All existing tests pass unchanged (`python -m pytest tests/ -v`)

---

## W-0208

status: todo
created: 2026-05-24
updated: 2026-05-24
blocks: []
blocked-by: [W-0207]
research: []

### Outcome

GitHub Pages is served cleanly from `main` via the GitHub Actions workflow (`pages.yml`), not from a feature branch via the "Deploy from branch" setting.

### Context

Pages was temporarily pointed at the `copilot/check-access-github-repository` branch (the W-0207 feature branch) using the "Deploy from branch → /docs" setting so the site could be previewed before merging. Once W-0207 merges to `main`, Pages should be reconfigured in the repository Settings → Pages → Source to **GitHub Actions** so that `pages.yml` controls all future deployments. The "Deploy from branch" mode and the Actions-based workflow conflict; only one should be active.

The `_docs/adr/` and `_docs/design/` reorganisation (done in W-0208 prep) also means the `docs/` folder now contains only site assets — no further directory cleanup is needed when switching to Actions-based deploy.

### Acceptance criteria

- Repository Settings → Pages → Source is set to **GitHub Actions** (not "Deploy from branch")
- A push to `main` triggers `pages.yml` and the site redeploys successfully
- The site at `https://davidamitchell.github.io/Memory-System/` reflects the latest ontology

---

## W-0202

status: deferred
created: 2026-05-23
updated: 2026-05-24
blocks: []
blocked-by: [W-0201]
research: []
assumptions:
  - Git's object store is a content-addressed store backed by SHA-1 (legacy) or SHA-256 (new repos); every blob committed to the repo already has a content hash as its identifier
  - The Resolver Service in ADR-0004 maps `sha256:<hex>` URIs to physical storage locations; git blobs do exactly this
  - `git cat-file blob <sha>` retrieves any committed file by its content hash without knowing its path — the same primitive the Resolver Service needs
  - Segment provenance in Turtle already records `ms:contentHash "sha256:<hex>"` — if the hex matches a git object SHA, no separate store is needed at all
uncertainty:
  - Git uses SHA-1 for legacy repos; this repository may not be initialised with `--object-format=sha256`; SHA-1 and SHA-256 hashes for the same content differ, so the URI scheme used in W-0200 (`sha256:<hex>`) must be reconciled with the actual git object hash algorithm in use
  - Whether storing segment blobs as standalone committed files (`data/segments/<sha>.txt`) is redundant once they are also tracked as git blobs — or whether the filepath itself is the necessary indirection
  - Whether `git log -- <filepath>` provides sufficient provenance history for the Assertion Lineage requirement in ADR-0004, or whether the explicit `prov:` triples are still needed alongside it

### Outcome

A design note (in `_docs/design/` or as a PROGRESS entry) that evaluates whether git's object store can serve as the Resolver Service backing store, replacing the `data/segments/` directory. The evaluation covers: SHA algorithm compatibility, retrieval primitive (`git cat-file`), history (`git log`), and whether explicit PROV-O triples are still necessary given git's built-in provenance.

### Context

ADR-0004 describes a Resolver Service that "maps content-addressed URIs (`sha256:...`) to physical storage locations" and notes it will be "implemented as a library function in the first iteration." Git is already a content-addressed object store: every blob committed to the repository is retrievable by its SHA hash. If the segment files committed in W-0200 and W-0201 are stored as git-tracked files, their git object SHAs are already content-addressed URIs — the Resolver Service may already exist as `git cat-file blob <sha>`.

This is an exploration item, not an implementation item. The goal is to determine whether the architecture can be simplified by treating git as the document store, segment store, and Resolver Service simultaneously — which would eliminate `data/segments/` as a separate directory and use the git object store as the single source of truth. This aligns with the existing "local-first, git-backed" design principle and the observation that git commits are already used as version snapshots.

The SHA algorithm mismatch (SHA-1 vs SHA-256) is the key risk: the `ms:contentHash` URI scheme must use the same algorithm as the git object store, or the resolver cannot perform a direct lookup. This must be measured against the actual repository configuration before committing to either approach.

### Acceptance criteria (exploration — output is a design note, not code)

- Determine the git object hash algorithm in use in this repository (`git config --get extensions.objectformat` or `git rev-parse --show-object-format`)
- Verify that `git cat-file blob <sha>` can retrieve a committed segment file by its object hash
- Compare: does the git blob SHA of `data/segments/<sha256-hex>.txt` equal the SHA-256 hash of the file content, or are they different? (Git SHA-1 objects are computed over `blob <size>\0<content>`, not raw content)
- Write up the finding as a dated entry in `PROGRESS.md` or a short note in `_docs/design/`
- Conclude with one of: (a) git object store IS the Resolver Service — update W-0200/W-0201 acceptance criteria to remove `data/segments/` directory; or (b) git object store is useful for history but not for direct SHA-256 URI resolution — keep `data/segments/` and document why

---

## W-0203

status: done
created: 2026-05-23
updated: 2026-05-24
blocks: [W-0204]
blocked-by: [W-0201, W-0207]
research: []
assumptions:
  - The 26 glossary files constitute ground truth: every concept label, alias, tag, and relatedTerm declared in their front-matter is a known-correct extraction target
  - Precision and recall are computable by comparing `delta_proposal` output from any extractor against the hand-authored front-matter values
  - The existing rule-based p07 extractor should score near-perfect on the glossary corpus (it reads the front-matter directly) — this becomes the baseline ceiling
uncertainty:
  - Whether a simple F1 score is sufficient or whether weighted metrics (penalise missing labels more than missing aliases) are needed
  - Whether evaluation should run per-file or aggregate across all 26 files

### Outcome

An evaluation CLI (`pipeline/eval.py`) that runs any extractor against the glossary corpus and prints per-file and aggregate precision/recall/F1 for concepts (label match), aliases, tags, and relatedTerm edges. The existing rule-based p07 is run first, establishing the baseline scores. The eval harness is the gate for all subsequent latent extraction phases: a new extractor is only accepted if it meets or exceeds baseline on the structured corpus.

### Context

Before any latent extraction work begins, the system needs a way to measure whether a new extractor is better or worse than the existing one. The glossary corpus is the ideal evaluation set because every extraction target is explicitly declared — there is no ambiguity about what the correct output should be. Running the existing rule-based extractor against this harness first establishes the ceiling (it should score ~1.0 since it reads the fields directly), which gives a clear reference point.

This is the thinnest possible first step for latent extraction: no new model, no new NLP library, no architecture change. Just an evaluation tool that makes extraction quality visible. Every subsequent work item (W-0204 onward) runs this harness as part of its acceptance criteria.

### Acceptance criteria

- `pipeline/eval.py --corpus glossary/` runs without error and prints a structured report
- Report includes: per-file precision/recall/F1 for labels, aliases, tags, and related edges; aggregate scores across all 26 files
- Running against the existing rule-based p07 produces near-perfect scores (≥0.95 aggregate F1) — this is recorded as the baseline in `PROGRESS.md`
- The eval harness accepts an `--extractor` flag so future extractors can be swapped in without changing the harness itself
- `python -m pytest tests/test_eval_w0203.py` passes

---

## W-0204

status: done
created: 2026-05-23
updated: 2026-05-24
blocks: [W-0205]
blocked-by: [W-0203]
research: []
assumptions:
  - An LLM can produce the same `delta_proposal` dict shape that the rule-based extractor produces — the interface is stable
  - A structured prompt (system prompt defining the schema + user prompt with document content) is sufficient to get consistent JSON output from an LLM
  - One research document is sufficient for the first slice — the goal is to establish viability, not coverage
  - The W-0203 eval harness is used to validate that the LLM extractor performs acceptably on the glossary corpus before being run on unstructured prose
  - Primary testing corpus is `raw_document_corpus/` (50 files from `copilot/ontology-experiment` branch — see ADR-0005)
uncertainty:
  - Which LLM to use (local model vs API call); the processor interface is agnostic — the choice is an implementation decision for this item
  - Whether the LLM requires a structured output schema (JSON mode / function calling) or whether prompt engineering is sufficient
  - What score threshold on the W-0203 eval harness is "acceptable" for the LLM extractor before it is trusted on unstructured prose
  - Whether a single research document is representative enough to draw conclusions about latent extraction viability

### Outcome

A new extraction strategy for p07 that uses an LLM to produce `delta_proposal` from unstructured prose. The extractor is evaluated against the W-0203 harness on the glossary corpus, establishing a score vs the rule-based baseline. It is then run against one selected research document, producing a concept card that is inspected by eye. The processor interface (`delta_proposal` dict shape) is unchanged — p08–p12 receive identical input regardless of which extraction strategy was used.

### Context

W-0201 and W-0203 give us a working graph and a measurement tool. This item is the first time the pipeline ingests a document that does not have hand-authored front-matter. The goal is viability, not perfection: does the LLM extractor produce plausible concepts and relations from prose? The W-0203 harness scores the output on the glossary corpus as a proxy for quality. If the score is below threshold, the extractor is refined before moving to W-0205. If it is above threshold, the pipeline is ready to expand the corpus.

The design principle is: the extractor is a pluggable strategy in p07. Swapping rule-based → LLM is one function swap. Nothing in p08–p12 changes. This was the design intent from the beginning (BACKLOG.md W-0200 rationale: "Rule-based domain → LLM domain: swap the classifier function; processor 5's input/output interface is unchanged").

### Acceptance criteria

- `pipeline/processors/p07_concept_extraction.py` has a `--strategy` flag (or equivalent) selecting `rule-based` (default, existing) or `llm`
- Running `--strategy llm` on any glossary file produces a `delta_proposal` with the same dict schema as the rule-based extractor
- `pipeline/eval.py --corpus glossary/ --strategy llm` produces a score that is recorded in `PROGRESS.md` alongside the rule-based baseline from W-0203
- Running `--strategy llm` on one selected research document completes without error and produces a concept card inspectable via `pipeline/query.py`
- The concept card from the research document is recorded by eye in `PROGRESS.md` — plausibility is noted, not scored (no ground truth exists for prose yet)
- All existing tests pass unchanged (`python -m pytest tests/ -v`)
- `python -m pytest tests/test_llm_extraction_w0204.py` passes

---

## W-0205

status: active
created: 2026-05-23
updated: 2026-05-25
blocks: [W-0206]
blocked-by: [W-0204]
research: []
assumptions:
  - spaCy (or equivalent NLP library) is available and can be added as a dependency without breaking the existing pipeline
  - NER and dependency parsing outputs can be fed as enrichment to p07 without changing the processor's output schema
  - Adding NLP preprocessing to p02 is additive — the existing `prepared_text` output is unchanged; NLP annotations are a new key in state
  - The W-0203 eval harness can measure whether NLP enrichment improves extraction quality over the W-0204 LLM-only baseline
uncertainty:
  - Whether spaCy's default English model is sufficient or whether a specialised scientific/research NER model is needed
  - Whether NER output improves LLM extraction quality or introduces noise (to be measured, not assumed)
  - Performance impact of adding NLP preprocessing to the pipeline (target: still completes in under 10 seconds per document)

### Outcome

p02 (Preparation Processor) is extended with an optional NLP enrichment step that attaches named entity spans, POS tags, and noun chunks to pipeline state. p07 (Concept Extraction, LLM strategy) consumes these annotations as additional signal when constructing its extraction prompt. The W-0203 eval harness measures whether NLP enrichment improves F1 over the W-0204 LLM-only baseline on the glossary corpus.

### Context

Phase 3 (W-0204) establishes that LLM-based extraction works on prose. This item tests the hypothesis that feeding the LLM structured NLP annotations (named entities, noun chunks) as part of the prompt produces better extractions than sending raw text alone. This is a targeted, measurable improvement: the eval harness scores both approaches and the delta is the evidence. If enrichment does not improve quality, it is not added — the measurement decides.

The NLP layer belongs in p02 because it is a preparation step (transforming raw text into richer structured input) not an extraction step. This separation preserves the single-responsibility design of the pipeline and ensures that any future extractor (not just LLM) can benefit from NLP enrichment.

### Acceptance criteria

- `pipeline/processors/p02_preparation.py` adds an optional NLP enrichment step controlled by a config flag; when disabled, output is identical to the W-0201 state
- Pipeline state gains a `nlp_annotations` key when NLP is enabled: named entity spans, POS-tagged tokens, noun chunks
- `pipeline/eval.py --corpus glossary/ --strategy llm --nlp` runs and produces scores recorded in `PROGRESS.md` alongside the W-0204 LLM-only baseline
- The delta (NLP-enriched vs LLM-only) is explicitly noted: improvement, no change, or regression — all are valid outcomes; the measurement is the deliverable
- All existing tests pass unchanged (`python -m pytest tests/ -v`)
- `python -m pytest tests/test_nlp_enrichment_w0205.py` passes

### Notes

**2026-05-25 — Implementation complete; eval score comparison blocked.**

All code deliverables are done:
- `p02_preparation.py`: NLP enrichment added (`state["nlp"]=True` activates it); `spacy>=3.7` + `en_core_web_sm` required; model cached lazily via `_nlp_model` seam.
- `p07_concept_extraction.py`: LLM strategy appends NLP pre-analysis (entities, noun chunks) to the user prompt via `_format_nlp_annotations()`.
- `pipeline/eval.py`: `--nlp` flag added; threaded through `evaluate_file()` and `print_report()`.
- `requirements.txt`: `spacy>=3.7` added.
- `tests/test_nlp_enrichment_w0205.py`: 12 tests, all passing.

**Blocker:** The eval criterion `pipeline/eval.py --corpus glossary/ --extractor llm --nlp` requires `OPENAI_API_KEY` to run. This key is not available in the agent sandbox. The delta score (NLP-enriched vs LLM-only baseline) cannot be recorded until a session with the key set runs this command and appends the result to `PROGRESS.md`.

To complete: run `python pipeline/eval.py --corpus glossary/ --extractor llm --nlp` in an environment with `OPENAI_API_KEY` set, record the aggregate F1 in `PROGRESS.md` alongside the W-0204 baseline (1.000 rule-based), then mark this item done.

---

## W-0206

status: ready
created: 2026-05-23
updated: 2026-05-23
blocks: []
blocked-by: [W-0205]
research: []
assumptions:
  - A minimal relation type vocabulary can be defined in the upper ontology without destabilising existing `ms:relatedTerm` edges
  - The `delta_proposal` dict can be extended with a `typed_relations` list alongside `related` without breaking p08–p12
  - The glossary corpus contains implicit relation types that a human can annotate for a small subset — this annotation becomes the ground truth for evaluating typed extraction
  - `ms:relatedTerm` is retained as a fallback when the extractor cannot determine a typed predicate
uncertainty:
  - Which relation types are load-bearing for this corpus (partOf, instanceOf, causedBy, precedes, usedBy, etc.) — a small annotation pass on the glossary will determine this
  - Whether LLM-based relation typing is reliable enough without fine-tuning
  - How typed relations interact with the consistency validation in p09 — typed predicates have stronger semantics than untyped ones

### Outcome

The pipeline extracts typed predicates (e.g. `ms:instanceOf`, `ms:usedBy`, `ms:precedes`) in addition to the existing untyped `ms:relatedTerm`. A minimal relation type vocabulary is defined in the upper ontology (`data/ontology/upper.ttl` or equivalent). A small human-annotated subset of the glossary corpus (5–10 files) provides ground truth for evaluating typed extraction quality. The W-0203 eval harness is extended to score typed relation extraction (macro-averaged F1 per relation type).

### Context

Typed relations are what distinguish an ontology from a property graph. An untyped `relatedTerm` edge says "these two concepts are somehow connected." A typed `ms:usedBy` edge says "concept A is used by concept B." The difference matters for reasoning, query precision, and eventual alignment with upper ontologies (BFO, schema.org). This item introduces typed relations at the minimum viable granularity — enough to demonstrate the capability and measure it, not a full OWL axiom set.

The minimal relation vocabulary is determined by annotation, not assumption: a human pass over the glossary `related:` edges, classifying each as partOf / instanceOf / usedBy / precedes / associatedWith (catch-all), reveals which types are actually present in the corpus. This annotation is the ground truth. The extractor is then evaluated against it.

### Acceptance criteria

- A minimal relation type vocabulary (5–8 types plus `ms:relatedTerm` catch-all) is defined and documented in `_docs/design/` or as a schema section in the ontology
- A human annotation of 5–10 glossary files' `related:` edges with typed predicates is committed to `data/eval/typed-relations-ground-truth.json`
- The LLM extractor (W-0204 strategy) is extended to output typed predicates in `delta_proposal.typed_relations`
- p08 (Ontology Build) writes typed predicates to Turtle alongside `ms:relatedTerm`
- `pipeline/eval.py --typed-relations` scores typed extraction against the ground truth annotation
- Scores are recorded in `PROGRESS.md`
- All existing tests pass unchanged (`python -m pytest tests/ -v`)
- `python -m pytest tests/test_typed_relations_w0206.py` passes

---

## W-0209

status: done
created: 2026-05-25
updated: 2026-05-25
blocks: []
blocked-by: [W-0207]
research: []
assumptions:
  - The target viewing platform is mobile (primary) and desktop (secondary)
  - Progressive enhancement is maintained: plain HTML tables work without JS; JS layers on mobile UX
  - The GitHub Pages site is the browsing surface
uncertainty:
  - Whether card layout for concepts is sufficient or whether future rich mobile views (e.g. swipe gestures, inline definition cards) are needed

### Outcome

The GitHub Pages ontology browser is mobile-first. Key improvements shipped:
- **Bottom tab navigation** (fixed, 56 px): nav links move from the sticky header to a fixed bottom bar on ≤640 px viewports, giving thumb-reachable navigation
- **Concept card layout**: concept table rows render as full-width cards on mobile, with label prominent, domain as a labelled sub-line, and tag/related counts inline
- **Bottom sheet detail panel**: the concept detail panel is a fixed bottom sheet (65 vh max, above the nav bar) with a backdrop overlay and body scroll lock on mobile
- **Horizontal scroll wrappers**: relations and documents tables are wrapped in `.table-scroll` divs, preventing horizontal overflow on narrow viewports
- **Full-width search**: search input expands to full viewport width on mobile
- `pipeline/export_html.py` updated to emit `data-label` attributes on all table cells and `.table-scroll` wrappers on relations and documents tables
- `docs/index.html` regenerated

### Acceptance criteria

- Bottom nav bar visible on viewport ≤640 px
- Concept rows render as cards (no horizontal overflow) on narrow viewports
- Tapping a concept card opens the detail panel as a bottom sheet with a backdrop
- Relations and documents tables scroll horizontally on narrow viewports
- Search input is full-width on mobile
- All 42 existing tests pass unchanged (`python -m pytest tests/ -v`)

---

## W-0210

status: done
created: 2026-05-25
updated: 2026-05-25
blocks: []
blocked-by: [W-0209]
research: []
assumptions:
  - Hash-based routing is sufficient for a static site with no server
  - Browser back/forward button must work correctly for concept and relation pages
  - Progressive enhancement maintained: tables remain navigable without JS

### Outcome

Concept rows and relation rows now navigate to full detail pages (hash routes `#concept/<id>` and `#relation/<from>/<pred>/<to>`) instead of opening a modal or bottom sheet.

- **Concept detail page** (`#concept/<id>`): full-page view with definition, domain badge, aliases, tags, related concepts (linked), outgoing/incoming relations (linked), and source documents. Back button returns to the concepts list.
- **Relation detail page** (`#relation/<from>/<pred>/<to>`): full-page view with from/to concept cards (linked), predicate badge, and a full list of other relations with the same predicate. Back button returns to the relations list.
- Hash-based routing handles browser back/forward correctly
- Relation rows are now clickable (tabindex, cursor, keyboard)
- Links within rendered pages use the same hash scheme so navigation is composable
- Removed old bottom-sheet detail panel; cleaned up dead CSS

### Acceptance criteria

- Clicking any concept row navigates to `#concept/<id>` full-page view ✓
- Back button from concept page returns to `#concepts` list ✓
- Clicking any relation row navigates to `#relation/<from>/<pred>/<to>` full-page view ✓
- Back button from relation page returns to `#relations` list ✓
- Browser back/forward works ✓
- All 42 existing tests pass unchanged ✓

---

## References

1. [`BACKLOG.md`](./BACKLOG.md) — discovery-phase research items; historical record.
2. [`definition_scheme.md`](./definition_scheme.md) — the schema and requirements for all glossary definition files.
3. [`glossary/README.md`](./glossary/README.md) — controlled vocabulary; terms used throughout this file are defined there.
4. [Model Context Protocol](https://modelcontextprotocol.io/) — the protocol underlying the future MCP server architecture.
5. [Ink & Switch: Local-first Software](https://www.inkandswitch.com/local-first/) — the design philosophy behind the zero-infrastructure goal.
6. [rdflib](https://rdflib.readthedocs.io/) — the Python RDF library used in W-0200 and W-0201 for in-memory graph construction, SPARQL queries, and Turtle serialisation.
7. [W3C PROV-O](https://www.w3.org/TR/prov-o/) — the provenance ontology used in the Turtle pattern (ADR-0004).
8. [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/) — the query language used in `pipeline/queries/*.rq`; queries written here run unchanged against any SPARQL endpoint.
9. [`_docs/design/ontology-system-design.md §9`](./_docs/design/ontology-system-design.md) — target state and proposed extraction phases; context for W-0203–W-0206.

---

## Deferred

> The following phases are deferred. Their items are retained as historical record and may be revisited when priorities change.

---
## ~~Phase 2 — Fix the foundation~~ [DEFERRED — obsolete; replaced by ontology architecture]

> These items assumed a LanceDB/vector-embedding foundation. That design was replaced before implementation (see ADR-0002). Items are retained as historical record.

---

---

## W-0100

status: obsolete
created: 2026-03-13
updated: 2026-03-13
blocks: [W-0101, W-0102, W-0103, W-0104, W-0105, W-0106, W-0107, W-0108, W-0109]
blocked-by: []
research: [2026-03-08-lancedb-index-rebuild-from-git.md]
assumptions:
  - BAAI/bge-small-en-v1.5 remains the baseline [embedding model](./glossary/embedding-model.md) until W-0101 resolves the model question
  - Pre-computed JSON embeddings are safe to commit to git (they are floating-point vectors, not secrets)
  - The corpus will not exceed 10,000 items in the medium term; JSON load scales acceptably to that size
uncertainty:
  - If the embedding model is later changed (e.g. by W-0101), all stored JSON files must be regenerated; this coupling must be documented in the ADR and in `scripts/regen_embeddings.py`
  - File-watcher-triggered indexing (on modify) still needs to embed from text; this is acceptable because the watcher runs in a live server session, not at cold-start

### Outcome

The MCP server starts up in under 2 seconds with a 61-item corpus (and scales to hundreds of items without breaching the 2-second threshold), because it loads pre-computed embedding vectors from JSON files instead of re-embedding every document from text on every startup.

### Context

Cold-start latency was measured at 11.5 seconds for 61 items (per `2026-03-08-lancedb-index-rebuild-from-git.md`), well above the 5-second target and catastrophic in the GitHub Actions headless sandbox where the server is spun up fresh for every Copilot agent session. Every feature built after this point depends on the server starting reliably within the sandbox timeout. This item is a prerequisite for all subsequent work.

### Acceptance criteria

- Cold-start with 61 items completes in under 2 seconds on the target environment (GitHub Actions runner or equivalent)
- `add_memory` generates a BGE-small embedding at write time and stores it as `<filename>.embedding.json` in the same folder as the `.md` file
- `add_memory` commits both the `.md` file and its `.embedding.json` file in the same git commit
- On startup, `mcp_server.py` loads `.embedding.json` files instead of re-embedding from text
- `scripts/regen_embeddings.py` exists, re-embeds all `.md` files, writes `.embedding.json` files, and exits with a non-zero code if any file fails
- All existing tests pass
- New unit tests cover the JSON load path (file present, file missing, file malformed)
- An ADR is written documenting the pre-computed embedding architecture and the model-version coupling risk

---

## W-0101

status: obsolete
created: 2026-03-13
updated: 2026-03-13
blocks: []
blocked-by: [W-0100]
research: [2026-03-02-semantic-full-text-search.md, 2026-03-08-lancedb-index-rebuild-from-git.md]
assumptions:
  - Model2Vec potion-base-8M is available via pip without a PyTorch dependency
  - The ~200× speedup figure from MTEB benchmarks will translate to a meaningful improvement in the Memory-System context, even if not the full 200× factor
  - 30–50 MB model size is acceptable for the GitHub Actions runner environment
  - Retrieval quality at 91–93% of MiniLM MTEB accuracy is acceptable for personal knowledge base use
uncertainty:
  - The ~200× speedup figure is from MTEB benchmarking contexts; it has not been measured against this corpus and LanceDB specifically
  - Model2Vec's accuracy on short personal notes (the dominant memory type here) may differ from MTEB benchmark text
  - If Model2Vec is adopted, all `.embedding.json` files written by W-0100 must be regenerated via `regen_embeddings.py`

### Outcome

The team has a data-backed decision on whether to replace BAAI/bge-small-en-v1.5 with Model2Vec (potion-base-8M) as the production embedding model, with benchmark results for cold-start time, query quality on 10 known queries, and memory usage in a 256 MB constrained environment. If Model2Vec wins, it is deployed and the embedding JSON files are regenerated.

### Context

`2026-03-08-lancedb-index-rebuild-from-git.md` identified Model2Vec as the production embedding candidate but did not benchmark it against the actual Memory-System corpus and LanceDB. `2026-03-02-semantic-full-text-search.md` documents the ~200× MTEB speedup and the absence of a PyTorch dependency. The pre-computed path established in W-0100 makes this evaluation safe: swapping the model only requires regenerating the JSON files, not restructuring the server. This item is not blocking any other work — the system is viable with BGE-small — but it is the highest-leverage optimisation available once W-0100 lands.

### Acceptance criteria

- A benchmark script exists at `scripts/benchmark_model2vec.py` that rebuilds the LanceDB index using Model2Vec and measures: cold-start time (wall clock), query latency for 10 predefined queries, recall quality (spot-check: do expected results appear in top-5?), and peak memory usage
- The benchmark is run and results are recorded in a new file in `projects/` (YYYY-MM-DD-model2vec-benchmark-results.md)
- A recommendation (adopt or reject) is written with explicit reasoning in the same file
- If Model2Vec is adopted: it replaces BGE-small in `mcp_server.py`, `regen_embeddings.py` is run, all `.embedding.json` files are regenerated, and an ADR is written documenting the model change
- If BGE-small is retained: the decision and reasoning are recorded in the benchmark results file and no ADR is required

---

## ~~Phase 3 — Frictionless capture~~ [DEFERRED]

> Deferred. Input surfaces will be scoped after the ontology pipeline is working end-to-end.

> Make the system actually usable day-to-day. Reduce the cost of adding a memory to near zero.

---

## W-0102

status: deferred
created: 2026-03-13
updated: 2026-03-13
blocks: [W-0103]
blocked-by: [W-0100]
research: [2026-03-08-inbox-folder-capture-triage-pattern.md]
assumptions:
  - The `inbox/` folder is a valid destination for `add_memory` alongside the existing `meetings/`, `journal/`, `projects/` folders
  - No [triage](./glossary/triage.md) or classification automation is required in this item — that is W-0103
  - Files in `inbox/` follow the same YAML front-matter requirements as other memory files
  - Timestamp-precision filenames (HHmmss) are sufficient to avoid collisions for human-pace capture rates
uncertainty:
  - Whether the `?-` prefix convention for ambiguous triage items will be widely adopted; this is a convention, not an enforced constraint
  - Whether `inbox/` should be included in the default `search_brain` scope immediately, or only after triage

### Outcome

Any memory can be captured without choosing a destination folder. Calling `add_memory` with `folder="inbox"` (or omitting the folder argument) creates a timestamped file in `inbox/` and commits it — removing the structurally disproportionate folder-selection decision from the fast-capture path.

### Context

`2026-03-08-inbox-folder-capture-triage-pattern.md` identified that requiring a folder selection at capture time creates cognitive friction that discourages use. The minimum viable inbox file requires only a `captured_at` timestamp and raw content. Triage (moving files from `inbox/` to their permanent home) is a separate concern handled in W-0103. This item is a direct prerequisite for all capture-surface work (W-0104 iOS Shortcut, W-0105 CLI) because those surfaces must be able to write without prompting the user for a folder.

The human-door web interface (Phase 4, W-0114) must include a quick-capture form — minimal fields, mobile-optimised — that writes directly to `inbox/` via the GitHub Contents API, following the same write path as the iOS Shortcut and CLI. This form must not introduce a separate Supabase write path for inbox captures; all narrative input flows through the git-backed markdown layer regardless of capture surface.

### Acceptance criteria

- `inbox/` folder exists with a `.gitkeep` file committed to git
- `add_memory(title="...", content="...", folder="inbox")` creates a file at `inbox/YYYY-MM-DD-HHmmss-<slug>.md` with correct YAML front-matter including a `captured_at` timestamp field
- `inbox` is listed as a valid folder value in `MEMORY_FOLDERS` in `mcp_server.py`
- The file-watcher indexes `.md` files created in `inbox/` on creation
- `search_brain` returns results from `inbox/` alongside results from other folders
- `.github/copilot-instructions.md` is updated to document the `inbox/` folder, the `?-` prefix convention for ambiguous triage items, and the instruction to use `folder="inbox"` for fast capture
- All existing tests pass

---

## W-0103

status: deferred
created: 2026-03-13
updated: 2026-03-13
blocks: []
blocked-by: [W-0102]
research: [2026-03-08-inbox-folder-capture-triage-pattern.md]
assumptions:
  - Triage is a weekly or on-demand agent task, not a real-time automation
  - The triage agent uses `search_brain` to identify the best permanent folder for each inbox item based on semantic similarity to existing memories
  - The human retains final approval before files are moved (the agent proposes, the human confirms)
  - `refactor_memory` is sufficient for moving a file (overwrite at new path, delete old path)
uncertainty:
  - Whether a fully automated triage (no human approval) is desirable for low-stakes items; this depends on observed error rates after initial deployment
  - The definition of "stale" inbox items (e.g. older than 7 days with no triage action) is a policy decision, not a technical one

### Outcome

A Copilot agent or human can run a triage pass on `inbox/` that proposes a permanent folder and filename for each untriaged item, based on semantic similarity to existing memories. The human reviews the proposals and approves or overrides before files are moved.

### Context

Without triage, the `inbox/` folder becomes a graveyard of uncategorised notes that degrades retrieval quality over time. W-0102 establishes the inbox; this item closes the loop by ensuring captured items eventually reach their permanent home. The triage agent leverages `search_brain` — the core retrieval capability — making this a natural extension of existing functionality rather than new infrastructure.

### Acceptance criteria

- A triage prompt or agent instruction exists (either in `.github/copilot-instructions.md` or a dedicated skill file) that describes the triage workflow: list files in `inbox/`, call `search_brain` with each file's content, propose a destination folder and filename, present proposals to the human, and execute approved moves
- The triage instruction covers the `?-` prefix convention: items prefixed with `?-` are explicitly flagged as ambiguous and must always be reviewed by the human rather than auto-approved
- A `scripts/triage_inbox.py` helper script exists that lists all files in `inbox/` and outputs their titles and `captured_at` timestamps for review
- At least one inbox item is successfully triaged end-to-end as a smoke test (documented in PROGRESS.md)
- All existing tests pass

---

## W-0104

status: deferred
created: 2026-03-13
updated: 2026-03-13
blocks: []
blocked-by: [W-0102]
research: [W-0008 in BACKLOG.md — discovery not yet complete]
assumptions:
  - iOS Shortcuts can write to the GitHub API (authenticated via a Personal Access Token stored in the Shortcuts keychain)
  - The capture surface writes to `inbox/` (per W-0102) rather than requiring folder selection
  - Front-matter injection can be done in the Shortcut itself using text templating
uncertainty:
  - Whether the GitHub API write latency (create file endpoint) is acceptable for a mobile quick-capture use case
  - Whether Shortcuts can reliably handle voice dictation input and clean it up before writing
  - PAT security model for iOS Shortcuts (keychain vs hardcoded — hardcoded is unacceptable)

### Outcome

A one-tap iOS Shortcut (available in the Share Sheet and via dictation) captures a memory directly to `inbox/` in the GitHub repository without requiring the user to open any app or choose a folder. The Shortcut is installable from a shared iCloud link.

### Context

iOS is the primary mobile platform. A Share Sheet extension means any piece of content — a web article, a voice note, a text selection — can be sent to the memory system in one tap. This is the highest-leverage mobile capture surface available without a dedicated app. Depends on W-0102 (inbox/ folder) so that the Shortcut does not need to know the destination folder. Outstanding discovery from W-0008 in BACKLOG.md must be completed before implementation can begin.

### Discovery needed before starting

- Confirm that iOS Shortcuts can authenticate to the GitHub API using a PAT stored in the Shortcuts keychain (not hardcoded). Test with the `repos/{owner}/{repo}/contents/{path}` PUT endpoint.
- Determine the correct approach for injecting YAML front-matter from a Shortcut (text template vs dictionary action).
- Evaluate whether voice dictation input (via Shortcuts Dictate Text action) produces output clean enough to commit directly or requires a post-processing step.
- Confirm file naming strategy: `YYYY-MM-DD-HHmmss-<slug>.md` where slug is derived from the first 6 words of the content.
- Document findings in a new `projects/YYYY-MM-DD-ios-shortcut-design.md` file before starting implementation.

### Acceptance criteria

- An iOS Shortcut exists and is shared via an iCloud link committed to `projects/`
- The Shortcut appears in the iOS Share Sheet and accepts text, URLs, and dictated voice input
- The Shortcut writes to `inbox/` using the GitHub Contents API (PUT), authenticated via a PAT stored in the Shortcuts keychain
- The created file includes correct YAML front-matter with `captured_at` timestamp
- The Shortcut does not expose the PAT in any logged or shareable output
- End-to-end test: capture a memory via Shortcut, verify the file appears in the repository and is indexed by `search_brain`

---

## W-0105

status: deferred
created: 2026-03-13
updated: 2026-03-13
blocks: []
blocked-by: [W-0102]
research: [W-0010 in BACKLOG.md — discovery not yet complete]
assumptions:
  - The CLI is implemented in Python (consistent with `mcp_server.py`) or as a shell script
  - `remember` writes to `inbox/` (per W-0102); folder selection is not required
  - `recall` calls `search_brain` via the MCP server or directly via LanceDB
  - The CLI is installed as a local Python script or via `pip install -e .`
uncertainty:
  - Whether `recall` should call the running MCP server (requires it to be running) or query LanceDB directly (requires the index to be up to date)
  - Shell completion scope: bash, zsh, fish — which to prioritise

### Outcome

A developer at a terminal can add a memory with `remember "note text"` and retrieve related memories with `recall "search query"` — without opening an editor, choosing a folder, or interacting with git directly. Both commands complete in under 3 seconds.

### Context

The terminal is the lowest-friction environment for developers. A `remember` / `recall` CLI brings the memory system into the natural developer workflow without requiring an IDE or MCP client. Depends on W-0102 (inbox/ folder) so that `remember` does not require a folder argument. Outstanding discovery from W-0010 in BACKLOG.md must be completed before implementation can begin.

### Discovery needed before starting

- Determine whether `recall` should query LanceDB directly or call the MCP server over stdio (the latter requires the server to be running).
- Decide on the implementation language: Python script installed via `pip install -e .`, or a standalone shell script.
- Define the shell completion approach (at minimum, bash and zsh).
- Document findings and design decision in `projects/YYYY-MM-DD-cli-design.md` before starting implementation.

### Acceptance criteria

- `remember "text"` creates a file in `inbox/` with correct YAML front-matter and commits it; completes in under 3 seconds
- `remember --title "Title" "text"` overrides the auto-generated title
- `recall "query"` returns the top-5 semantically similar memories with title, file path, and a content excerpt; completes in under 3 seconds
- Both commands work from any directory (not just the repository root)
- Shell completion is available for at least bash and zsh
- The commands are documented in `README.md`
- All existing tests pass; new tests cover the CLI entry points

---

## ~~Phase 4 — Structured relational layer~~ [DEFERRED]

> Deferred. Depends on capture surfaces being defined first.

---

## W-0111

status: deferred
created: 2026-03-15
updated: 2026-03-15
blocks: [W-0112]
blocked-by: []
research: []
assumptions:
  - Supabase free tier provides sufficient Postgres capacity for a personal-scale structured record store (contacts, meetings)
  - The MCP client configuration supports multiple simultaneous MCP servers if the two-server route is chosen
  - RLS (Row Level Security) in Supabase provides sufficient access control for a single-owner personal system
uncertainty:
  - Whether two MCP servers in a single client config (e.g. `.vscode/mcp.json`) is cleanly supported by all target MCP clients (VS Code Copilot, Cursor, Claude iOS)
  - The maintenance cost difference between operating the official Supabase MCP server vs adding SQL-backed tools to `mcp_server.py`
  - Whether agent ergonomics are better with a unified tool surface (extended `mcp_server.py`) or a dedicated data-layer server

### Outcome

A documented architectural decision on how to expose Supabase Postgres to the MCP agent layer: either via the official Supabase MCP server as a second server in the client config, or by extending `mcp_server.py` with SQL-backed tools. The decision records trade-offs across maintenance cost, tool surface design, agent ergonomics, and multi-server client config cleanliness.

### Context

The markdown/LanceDB layer is optimised for unstructured, narrative knowledge — meeting notes, journal entries, project context. Structured record types (contacts with last_contact dates, recurring meetings with attendees, entities with typed fields) are a poor fit for free-text markdown: queries like "who haven't I contacted in 30 days?" require relational semantics, not semantic similarity. A Supabase Postgres layer provides SQL query capabilities, typed schemas, and RLS without adding operational burden (Supabase is managed). The question is whether to expose it via the official Supabase MCP server (a second MCP server alongside the memory MCP server) or to add SQL tools directly to `mcp_server.py`. Both approaches are viable; the trade-offs must be evaluated before any implementation begins.

### Discovery needed before starting W-0112

- Evaluate the official Supabase MCP server: what tools does it expose, what is its auth model, and how does it behave in VS Code, Cursor, and Claude iOS with multiple MCP servers configured?
- Evaluate extending `mcp_server.py` with SQL-backed tools: what is the additional dependency surface (supabase-py or psycopg2), and how does it affect the server's test and deployment footprint?
- Assess agent ergonomics: is it clearer for an agent to call `supabase.query_contacts()` via a dedicated server, or `memory.query_contacts()` via the unified server?
- Assess two-MCP-server client config cleanliness: does `.vscode/mcp.json` support multiple servers cleanly, and do all target clients honour the full config?
- Document findings and recommendation in `_docs/adr/NNNN-supabase-mcp-integration-architecture.md` before starting W-0112.

### Acceptance criteria

- An ADR exists at `_docs/adr/NNNN-supabase-mcp-integration-architecture.md` that records the chosen approach (two servers or unified server) with explicit reasoning covering: maintenance cost, tool surface design, agent ergonomics, and multi-server client config behaviour
- The ADR documents which MCP clients were tested and the result of running two simultaneous MCP servers in each
- A prototype or proof-of-concept (throwaway code, not production) was used to validate the chosen approach before the ADR was finalised — this is documented in the ADR
- W-0112 is unblocked: the implementation approach is clear enough to begin schema design

---

## W-0112

status: deferred
created: 2026-03-15
updated: 2026-03-15
blocks: [W-0113]
blocked-by: [W-0111]
research: []
assumptions:
  - Supabase free tier is sufficient for a single-user personal system (contacts, meetings at personal scale)
  - Row Level Security (RLS) is enabled on all tables; service-role key is used only server-side
  - The "one more TBD" record type beyond contacts and meetings will be identified during W-0111 discovery or early in this item
  - Typed fields are preferred over JSONB blobs for the primary structured attributes (name, email, last_contact_date, etc.)
uncertainty:
  - The exact schema for each record type will depend on real usage patterns; starting minimal and adding columns is safer than over-designing upfront
  - Whether the third structured record type (TBD) should be defined before schema migration or added in a follow-up

### Outcome

Supabase Postgres tables exist for contacts, meetings, and one additional structured record type (TBD), with typed fields and Row Level Security enabled. The integration with the MCP agent layer follows the architectural decision made in W-0111. The reasoning for why these record types live in Postgres rather than the markdown/LanceDB layer is documented.

### Context

Contacts and meetings are the canonical examples of data that does not belong in the markdown layer: a contact is a structured entity (name, email, phone, company, last_contact_date, notes) that needs to be queried relationally ("show me everyone I haven't emailed in 30 days"), not retrieved semantically. Meetings similarly have structured attributes (attendees, date, agenda, outcome) that benefit from typed queries. Storing these as markdown files produces retrieval noise (the LanceDB vector index does not understand "last_contact_date < 30 days ago") and makes updates error-prone (editing YAML front-matter in a markdown file is fragile). A Postgres layer separates the concern cleanly: structured data lives in Supabase, narrative context lives in LanceDB, and the agent can query both via the tool surface defined in W-0111.

### Acceptance criteria

- Supabase project exists and connection credentials are stored as repository secrets (not in source code)
- `contacts` table exists with at minimum: `id`, `name`, `email`, `company`, `last_contact_date`, `notes`, `created_at`, `updated_at`; RLS enabled
- `meetings` table exists with at minimum: `id`, `title`, `date`, `attendees` (array or FK), `agenda`, `outcome`, `created_at`; RLS enabled
- A third structured table (type TBD during implementation) exists with typed fields and RLS enabled; its choice and reasoning are documented in `projects/`
- An ADR or inline note explains why each of these record types belongs in Postgres rather than markdown
- MCP tools for CRUD operations on all tables are available via the integration approach chosen in W-0111
- At least one end-to-end test demonstrates: create a contact via MCP tool, query it back, update `last_contact_date`
- Database schema is documented in `docs/` or `projects/` with the rationale for field choices

---

## ~~Phase 5 — Human door~~ [DEFERRED]

> Deferred. Depends on structured relational layer.

---

## W-0113

status: deferred
created: 2026-03-15
updated: 2026-03-15
blocks: [W-0114]
blocked-by: [W-0112]
research: []
assumptions:
  - The web interface is a personal tool for a single authenticated user; multi-user support is out of scope
  - Supabase Auth (magic link or OAuth) is the authentication provider, consistent with the Supabase stack chosen in W-0111 and W-0112
  - Vercel is the deployment target (serverless, free tier for personal projects)
uncertainty:
  - Whether Supabase Auth magic link, GitHub OAuth, or a simple API key is the right auth model for a solo personal tool
  - Whether Supabase RLS can be used directly from the Next.js/Vercel frontend with the anon key, or whether a server-side proxy is required

### Outcome

The auth model for the human-door web interface is decided and documented: which provider, what flow (magic link, OAuth, API key), and how Supabase RLS integrates with the frontend. A skeleton Vercel project exists with auth wired up but no UI beyond a login screen.

### Context

The human door is a lightweight read/write web interface over the structured Supabase tables created in W-0112. Before building any views, the auth model must be resolved: a misconfigured auth layer in a personal tool is a common source of accidental data exposure. Vercel is the deployment target because it provides zero-ops deploys from a GitHub repo, integrates with Next.js, and has a generous free tier. Supabase Auth is the natural choice given the Supabase stack, but the specific flow (magic link for frictionless solo use vs GitHub OAuth for familiar UX) needs evaluation.

### Discovery needed before starting W-0114

- Evaluate Supabase Auth options for a single-user personal tool: magic link, GitHub OAuth, and simple API key (bearer token via environment variable). Score each on: setup complexity, day-to-day UX, and risk of accidental exposure.
- Confirm that Supabase RLS policies allow the frontend (using the anon key + user JWT) to read and write rows owned by the authenticated user, without needing a server-side proxy.
- Set up the Vercel project, connect it to the repository, and configure environment variables (Supabase URL, anon key, auth secret).
- Document the auth decision in `_docs/adr/NNNN-human-door-auth-model.md`.

### Acceptance criteria

- An ADR exists at `_docs/adr/NNNN-human-door-auth-model.md` documenting the chosen auth flow and the reasoning
- A Vercel project is deployed from the repository with a login screen (no content beyond auth)
- Supabase Auth is configured and a test login (magic link or OAuth) succeeds end-to-end from the Vercel deployment
- RLS policies on the tables created in W-0112 are tested from the frontend context (anon key + user JWT)
- The Vercel project URL is documented in `projects/`
- No credentials or secrets are committed to the repository

---

## W-0114

status: deferred
created: 2026-03-15
updated: 2026-03-15
blocks: [W-0115]
blocked-by: [W-0113]
research: []
assumptions:
  - The first view is a contacts list sorted by `last_contact_date` ascending (longest ago at the top) — the primary use case is surfacing who to reach out to
  - Inline editing (click to edit a field, save on blur or enter) is sufficient for the first iteration; a full edit form is not required
  - The interface is mobile-optimised (the primary use case is checking contacts on the go)
  - A quick-capture form for inbox writes is included in this view, per the capture friction requirement in W-0102: minimal fields, mobile-optimised, writes to `inbox/` via the GitHub Contents API (same path as iOS Shortcut and CLI, not a Supabase write)
uncertainty:
  - Whether a quick-capture inbox form on the same page as the contacts view is the right UX, or whether a dedicated capture tab/route is better
  - The exact fields visible in the contacts list without expanding a row

### Outcome

The human-door web interface has a contacts view that shows all contacts sorted by `last_contact_date` (ascending), supports inline field editing, and includes a mobile-optimised quick-capture form that writes directly to `inbox/` via the GitHub Contents API.

### Context

The primary job-to-be-done for the human door is: "show me who I haven't spoken to in a while, let me update the record without friction, and let me capture a quick note without switching context." The contacts-by-last-contact view directly serves the first two jobs. The quick-capture form serves the third — and it must write to `inbox/` via the GitHub Contents API (same path as the iOS Shortcut and CLI) rather than to Supabase, to preserve the principle that all narrative captures flow through the same git-backed markdown layer.

### Acceptance criteria

- The contacts view loads at the Vercel deployment URL and shows all contacts from the Supabase `contacts` table, sorted by `last_contact_date` ascending
- Clicking a field in the contacts list makes it editable inline; saving writes to Supabase via the RLS-governed frontend client
- `last_contact_date` is displayed in a human-readable relative format (e.g. "3 months ago")
- A quick-capture form is present on the page: at minimum a text area and a submit button; on submit it creates a file in `inbox/` via the GitHub Contents API (authenticated with a PAT stored server-side or in the user's session, not hardcoded)
- The quick-capture form is mobile-optimised: large tap targets, minimal fields, no folder-selection step
- The interface is responsive and usable on an iPhone screen (375px viewport)
- All acceptance criteria from W-0113 (auth, RLS) continue to pass

---

## ~~Phase 6 — Retrieval quality~~ [DEFERRED — obsolete]

> Deferred. These items assumed LanceDB/vector search, which was replaced before implementation (see ADR-0002). Retrieval quality for the ontology approach will be addressed as part of the pipeline work.

---

## W-0106

status: obsolete
created: 2026-03-13
updated: 2026-03-13
blocks: [W-0107]
blocked-by: [W-0100]
research: [2026-03-02-semantic-full-text-search.md]
assumptions:
  - LanceDB supports hybrid (vector + full-text) search via its FTS index
  - The current corpus size does not require approximate nearest-neighbour tuning (exact search is fast enough)
  - Hybrid search improves recall for short queries (single words, proper nouns) where pure vector search underperforms
uncertainty:
  - Whether LanceDB's FTS index is stable and performant enough for production use at the current corpus scale
  - The optimal weighting between vector score and BM25 score for this corpus type (personal notes, short-form)

### Outcome

`search_brain` returns better results for short, keyword-style queries (e.g. single proper nouns, project names) by combining vector similarity with BM25 full-text scoring. Queries that previously returned semantically adjacent but keyword-mismatched results now correctly surface exact-match documents.

### Context

Pure vector search is powerful for semantic queries but underperforms on short keyword queries and proper nouns (names, project titles, acronyms). Hybrid search addresses this gap without replacing vector search. `2026-03-02-semantic-full-text-search.md` documents LanceDB's hybrid search capability. This item is a prerequisite for W-0107 (related-memories linking) which relies on high-quality search to identify link targets.

### Acceptance criteria

- `mcp_server.py` builds a full-text search (FTS) index on the LanceDB table in addition to the vector index
- `search_brain` uses hybrid (reranked vector + BM25) search when LanceDB's hybrid mode is available; falls back to pure vector search if not
- A benchmark of 10 known queries (5 semantic, 5 keyword-style) is run before and after; results are documented in `projects/`
- Hybrid search does not increase cold-start time beyond the 2-second target established in W-0100
- All existing tests pass; new tests cover the hybrid search path

---

## W-0107

status: obsolete
created: 2026-03-13
updated: 2026-03-13
blocks: []
blocked-by: [W-0106]
research: []
assumptions:
  - Related-memory links are added to YAML front-matter as a `related` field (list of file paths)
  - Link generation is an agent-triggered action, not an automatic background task
  - The agent uses `search_brain` to find candidates and proposes links for human review (same pattern as W-0103 triage)
uncertainty:
  - Whether auto-generating links without human review is acceptable for low-confidence matches
  - Front-matter `related` field vs inline markdown links — which is more useful for downstream retrieval

### Outcome

Every memory file can have a `related` field in its YAML front-matter listing semantically similar memories. A Copilot agent or human can trigger a link-generation pass that calls `search_brain` for each file, proposes the top-3 related items, and updates the front-matter after human approval. `search_brain` results include related-file links in their output.

### Context

The `## Related` section requirement in `.github/copilot-instructions.md` (§ 7) mandates linking every new memory to 3 related files, but this is done manually and inconsistently. Automating the suggestion step reduces the effort to near zero while keeping the human in the loop for approval. Depends on W-0106 (hybrid search) to ensure link candidates are high quality.

### Acceptance criteria

- YAML front-matter schema is updated to include an optional `related` field (list of relative file paths)
- A link-generation agent instruction or script proposes the top-3 related files (by `search_brain` score) for each file in the corpus
- `refactor_memory` correctly updates the `related` field without corrupting other front-matter fields
- `search_brain` output includes the `related` links from each result's front-matter
- The link-generation pass is documented in `.github/copilot-instructions.md` as part of the "Every write earns its place" section
- All existing tests pass

---

## ~~Phase 7 — Async capture channels~~ [DEFERRED]

> Deferred. Input surfaces will be scoped after the ontology pipeline is working end-to-end.

---

## W-0108

status: deferred
created: 2026-03-13
updated: 2026-03-13
blocks: []
blocked-by: [W-0102]
research: [W-0011 in BACKLOG.md — discovery not yet complete]
assumptions:
  - Telegram bot can be self-hosted or run on a free cloud tier (Railway, Fly.io)
  - The bot uses the `add_memory` MCP tool (calling `mcp_server.py`) or the GitHub Contents API directly
  - Messages sent to the bot are written to `inbox/` (per W-0102) without folder selection
uncertainty:
  - Webhook vs long-polling: webhook requires a public URL; polling requires an always-on process
  - PAT / secret management for a cloud-hosted bot
  - Whether a hosted bot service (e.g. Railway free tier) is reliable enough for a personal use case

### Outcome

A Telegram message sent to a personal bot (e.g. `/remember I need to research X`) is saved as a memory in `inbox/` and committed to the repository within 5 seconds.

### Context

Telegram is available on all platforms (iOS, Android, desktop, web) and supports bot interactions in private chats. A Telegram bot provides a low-friction mobile capture channel that works without a native app or Shortcut setup. Depends on W-0102 (inbox/ folder). Outstanding discovery from W-0011 in BACKLOG.md must be completed before implementation can begin.

### Discovery needed before starting

- Evaluate webhook vs long-polling for a single-user personal bot (polling is simpler, webhook is more responsive).
- Identify a free or low-cost hosting option for an always-on Python bot (Railway, Fly.io, or GitHub Actions scheduled workflow with polling).
- Determine the secret management approach for the Telegram bot token and GitHub PAT in the hosting environment.
- Document findings in `projects/YYYY-MM-DD-telegram-bot-design.md` before starting implementation.

### Acceptance criteria

- A Telegram bot accepts `/remember <text>` commands in a private chat
- The bot writes to `inbox/` via the GitHub Contents API, authenticated securely (token not in source code)
- The memory file is committed and available in the repository within 5 seconds of sending the Telegram message
- The bot responds with a confirmation message including the created file path
- The hosting setup is documented in `projects/` including secret rotation instructions
- All existing tests pass

---

## W-0109

status: deferred
created: 2026-03-13
updated: 2026-03-13
blocks: []
blocked-by: [W-0102]
research: [W-0003 in BACKLOG.md — discovery not yet complete]
assumptions:
  - Slack bot uses a slash command `/remember` in a personal workspace or DM
  - The bot writes to `inbox/` (per W-0102) without folder selection
  - OAuth or a bot token is used for Slack authentication; PAT is used for GitHub writes
uncertainty:
  - Whether Slack's free tier retains app/bot configurations permanently
  - Slack's response URL (3-second timeout for slash commands) may be too short if GitHub API write is slow; an async response pattern may be required

### Outcome

A Slack slash command `/remember <text>` in a personal workspace saves a memory to `inbox/` within 5 seconds and posts a confirmation message with the file link.

### Context

Slack is widely used in professional contexts; a `/remember` command lets team-related thoughts be captured immediately in context. Depends on W-0102 (inbox/ folder). Outstanding discovery from W-0003 in BACKLOG.md must be completed before implementation can begin.

### Discovery needed before starting

- Confirm that Slack slash commands can trigger an async response (deferred response URL) to accommodate GitHub API write latency.
- Determine the simplest hosting option for the Slack event handler (AWS Lambda, Vercel Edge, or GitHub Actions webhook).
- Evaluate whether a Slack bot token or incoming webhook is the appropriate integration type for a personal workspace.
- Document findings in `projects/YYYY-MM-DD-slack-bot-design.md` before starting implementation.

### Acceptance criteria

- A Slack slash command `/remember <text>` is available in at least one workspace
- The command writes to `inbox/` via the GitHub Contents API, authenticated securely
- A confirmation message is posted within 5 seconds (using async/deferred response if needed)
- The bot token and GitHub PAT are stored as environment secrets in the hosting environment, not in source code
- The setup is documented in `projects/` including how to install the Slack app in a new workspace
- All existing tests pass

---

## ~~Phase 8 — Infrastructure~~ [DEFERRED]

> Deferred. Self-hosted MCP and proactive agent depend on the ontology server, which is not yet implemented.

---

## W-0110

status: deferred
created: 2026-03-13
updated: 2026-03-13
blocks: []
blocked-by: [W-0100]
research: [W-0014 in BACKLOG.md — discovery not yet complete]
assumptions:
  - A self-hosted MCP server makes the memory system accessible from iOS MCP clients (Claude iOS, etc.) that cannot run a local server
  - The server exposes the same `search_brain`, `add_memory`, and `refactor_memory` tools over a network transport (HTTP/SSE or WebSocket) rather than stdio
  - Authentication is required (the server has write access to the GitHub repository)
uncertainty:
  - Whether Claude iOS or any current iOS MCP client supports remote (non-localhost) MCP servers over HTTP/SSE
  - Whether the LanceDB index can be persisted across server restarts on a cloud host (depends on persistent storage availability)
  - Cost of always-on hosting vs cost of on-demand startup latency (cold-start at a serverless host)

### Outcome

The MCP server is accessible from any MCP client on any device (including mobile) via a stable URL, authenticated with a bearer token. The LanceDB index is persisted across server restarts so cold-start is fast without requiring a full re-index.

### Context

The current MCP server runs only over stdio and requires a local dev environment. This blocks mobile clients (Claude iOS, any future iOS MCP client) from accessing the memory system. Self-hosting on a home server (Raspberry Pi + Tailscale), Railway, or a Cloudflare Worker is the path to universal access. Depends on W-0100 (pre-computed embeddings) to ensure the server starts fast enough for cloud/serverless deployment. Outstanding discovery from W-0014 in BACKLOG.md must be completed before implementation can begin.

### Discovery needed before starting

- Evaluate and compare: home server + Tailscale, Railway (persistent process), Cloudflare Worker (serverless, stateless) — for cost, reliability, and LanceDB compatibility.
- Determine whether LanceDB can run on Cloudflare Workers (WASM support required) or whether a persistent process host is mandatory.
- Identify the authentication model: bearer token, GitHub OAuth, or mTLS.
- Confirm whether Claude iOS (or other target MCP clients) support remote HTTP/SSE MCP servers at time of implementation.
- Document findings in `projects/YYYY-MM-DD-self-hosted-mcp-design.md` before starting implementation.

### Acceptance criteria

- `mcp_server.py` supports an HTTP/SSE (or WebSocket) transport mode in addition to stdio (selected via a `--transport` flag or environment variable)
- The server requires bearer-token authentication for all tool calls
- The LanceDB index is persisted to a mounted volume (not ephemeral storage) so cold-start loads from JSON files rather than rebuilding from scratch
- The server is deployed to a chosen host and accessible via a stable URL
- End-to-end test: call `search_brain` and `add_memory` from a remote MCP client (not localhost)
- The deployment setup (host, secrets, domain) is documented in `projects/` with rotation instructions
- An ADR is written documenting the network transport choice and the authentication model

---

## W-0115

status: deferred
created: 2026-03-15
updated: 2026-03-15
blocks: []
blocked-by: [W-0114]
research: []
assumptions:
  - The scheduled agent queries the Supabase structured tables (not LanceDB) for its flags — "contacts not reached in X days" is a SQL query, not a semantic search
  - The agent surfaces flags via a familiar channel (GitHub issue, Telegram message, or email) — the delivery channel is a discovery decision
  - The blocking dependency on W-0114 (human door in daily use) is intentional: a proactive monitor over a table that isn't being maintained is noise, not signal
uncertainty:
  - Whether Supabase Edge Functions cron, GitHub Actions scheduled workflow, or a separate always-on process is the right hosting approach
  - The delivery channel (GitHub issue creation vs Telegram vs email) depends on which channel is actually checked daily; this is a usage pattern question
  - Defining "actionable flag" thresholds (e.g. "hasn't contacted in 30 days") without real usage data risks producing too many or too few alerts

### Outcome

A scheduled agent runs on a defined cadence (daily or weekly), queries the Supabase structured tables for configurable flag conditions (e.g. contacts not reached in N days, upcoming meeting follow-ups overdue), and surfaces the flags via a chosen delivery channel — without requiring the human to ask first.

### Context

The human door (W-0113, W-0114) makes structured data maintainable. This item makes it proactive: instead of waiting to be asked, the agent monitors the data and pushes relevant flags to the human. The blocker (W-0114 in real daily use) is explicit and intentional — building a scheduler over data that isn't being maintained produces noise that trains the user to ignore it. Hosting options under consideration are Supabase Edge Functions cron (co-located with the data, no extra infrastructure) and GitHub Actions scheduled workflow (already-used infrastructure, familiar, but adds a workflow file). The delivery channel decision is deferred to discovery.

### Discovery needed before starting implementation

- Determine whether Supabase Edge Functions cron or a GitHub Actions scheduled workflow is the better host for a personal-scale daily check.
- Identify the delivery channel: GitHub issue creation (visible in the repo), Telegram bot message (real-time on phone), or email. Score each on: daily visibility, friction to dismiss, and setup cost.
- Define the initial set of flag conditions and their thresholds (e.g. last_contact_date > 30 days, meeting without outcome > 7 days old).
- Document the design in `projects/YYYY-MM-DD-proactive-agent-design.md` before implementation.

### Acceptance criteria

- A scheduled process (Supabase Edge Function cron or GitHub Actions schedule) runs at a configured cadence (at minimum weekly)
- The process queries the Supabase `contacts` table and identifies contacts whose `last_contact_date` is older than a configurable threshold
- Flags are delivered via the chosen channel (GitHub issue, Telegram, or email) with enough context to act without opening a separate app
- The flag threshold is configurable (environment variable or config file) without code changes
- The agent does not fire if no flags meet the threshold — silence means all clear
- The scheduling config and delivery channel are documented in `projects/` with rotation/update instructions
- This item must not be started until W-0114 has been in daily use for at least two weeks (enforced by convention, documented here)

---

## Historical Discovery Items

> Items W-0001 through W-0015 are the original research and discovery backlog that preceded this implementation roadmap. They are preserved here for reference. Active build work starts at W-0200.

---

## W-0001

status: done
created: 2026-03-07
updated: 2026-03-07

### Outcome

Repository structure is standardised: single `.github/copilot-instructions.md` source of truth, `.github/skills` submodule, `sync-skills.yml` workflow, `BACKLOG.md`, `PROGRESS.md`, `CHANGELOG.md`, and `_docs/adr/` all present and consistent.

### Context

Standardisation pass to remove AGENTS.md and align with all other repos in the davidamitchell organisation.

## W-0002

status: done
created: 2026-03-07
updated: 2026-03-08

### Outcome

All open PR branches were verified against `main`. No conflicts found. Only one open PR existed (PR #7) and it was cleanly rebased on `main`.

### Context

When multiple Copilot feature branches are open simultaneously they may diverge from a main that has received merged PRs. On 2026-03-08 a full audit confirmed no concurrent conflicts.

### Notes

Consider adding a scheduled workflow or PR check that detects when a Copilot branch is more than N commits behind main and posts a comment prompting a rebase.

---

## W-0003

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research whether a Slack bot can receive messages and write them directly to the repo as `.md` files via the GitHub API. Determine: (a) whether a free Slack workspace plus incoming webhook or Slash command is sufficient, (b) whether a hosted bot is needed, (c) latency from message to committed file, (d) whether the bot can respond to a query by calling search results back into the Slack thread. Key unknown: does the hosted component requirement kill the zero-infrastructure design goal?

### Context

Slack is already open on most people's phones all day. Sending a message to a dedicated `#brain` channel is 2 taps. This is potentially the lowest-friction mobile capture path that does not require a new app.

---

## W-0004

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research whether Claude for iOS supports MCP connections to a locally-running `mcp_server.py`, or whether there is a cloud-hosted MCP option. Determine: (a) current state of MCP support in the Claude mobile app, (b) whether a self-hosted MCP server accessible over HTTPS would be recognised by the Claude iOS app, (c) the security model.

### Context

Claude Desktop already works with the local MCP server. If the iOS app supports the same MCP config, this is a zero-new-code path. The blocker is that `mcp_server.py` must be reachable from the internet, not just localhost.

---

## W-0005

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research whether ChatGPT for iOS supports any mechanism to connect to an external memory system: (a) OpenAI Actions / plugin architecture, (b) ChatGPT native Memory feature export hook, (c) custom GPT configured to call search via an HTTP Action. Determine the hosting requirement and auth model.

### Context

ChatGPT is the most widely used AI app on iOS. If a custom GPT can be pointed at a simple HTTP wrapper around the MCP tools, the retrieval and capture path becomes: open ChatGPT, speak or type, memory is stored or searched.

---

## W-0006

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research Google's equivalent of MCP/Actions for mobile: (a) Gemini Extensions and whether they support custom external tools, (b) Google AppSheet or Workspace Apps as a lightweight form-based capture interface that writes to Google Drive and syncs to GitHub, (c) Google Assistant routines for capture, (d) Gemini for Workspace memory or note-taking integration.

### Context

Lower priority than Claude/ChatGPT given the owner's tool stack, but worth scanning.

---

## W-0007

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research whether Grok on iOS has any plugin, MCP, or external tool integration for an external memory system. Also: could the X/Twitter API be used as a capture channel via DM to a bot account that triggers a GitHub API write?

### Context

Speculative but low-effort to evaluate. If the owner is already in the X app, a DM-based capture bot is a 2-tap flow.

---

## W-0008

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Build and document an iOS Shortcut that: (a) accepts text from the Share Sheet, dictation, or a manual text field, (b) calls the GitHub Contents API to write a new `.md` file directly to the `journal/` or `inbox/` folder, (c) requires zero running infrastructure.

### Context

This is the highest-confidence, lowest-infrastructure option for mobile capture. No server, no bot, no subscription. The GitHub API supports file creation directly.

---

## W-0009

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Build a Raycast extension or Alfred workflow that: (a) opens a floating text input on a global keyboard shortcut, (b) sends the text to `mcp_server.py` via stdin/stdout or directly calls the underlying Python function, (c) dismisses immediately.

### Context

On the desktop side, this is the equivalent of the iOS Shortcut. Raycast already has MCP support in its AI features as of 2025.

---

## W-0010

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Add a `remember` CLI script to the repo that: (a) accepts a string argument, (b) writes a timestamped `.md` file to `journal/`, (c) commits and pushes, (d) optionally accepts `--folder` to target `meetings/` or `projects/`. Also add a `recall` command that searches and prints results to stdout.

### Context

Engineers live in the terminal. `remember "decided X because Y"` is lower-friction than any GUI for capture during a coding session.

---

## W-0011

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research and prototype a Telegram bot that: (a) accepts any message and stores it, (b) responds to messages starting with `?` by searching and replying with top results, (c) runs as a long-polling or webhook Python process, (d) can be hosted on a Raspberry Pi, home server, or cheap VPS.

### Context

Telegram bots are trivial to create and the bot API is free. The hosted component is unavoidable here, unlike iOS Shortcuts (W-0008).

---

## W-0012

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Add an `inbox/` folder to the repo as a frictionless drop zone: (a) any capture tool can write unstructured notes here without requiring a title, tags, or folder decision, (b) a periodic agent task reads the inbox, classifies each item, and moves it to the appropriate folder with proper front-matter.

### Context

Forcing a folder decision at capture time is friction. The inbox pattern removes that decision from the capture path and defers it to a low-urgency triage step.

---

## W-0013

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research whether an Apple Watch complication or Shortcut can: (a) accept voice dictation, (b) send the transcribed text to the iOS Shortcut from W-0008 or directly to the GitHub API. Determine latency and reliability.

### Context

A Watch tap and dictate is potentially the fastest possible capture path. No phone unlock required.

---

## W-0014

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Research the minimum viable self-hosted deployment of `mcp_server.py` reachable from Claude iOS or ChatGPT Actions: (a) home server / Raspberry Pi with Tailscale, (b) fly.io / Railway free tier, (c) Cloudflare Worker wrapping the GitHub API, (d) GitHub Actions as a compute backend via `repository_dispatch`.

### Context

Most AI app integrations require the MCP server or an HTTP endpoint reachable over the internet. This item determines whether self-hosting is feasible within the design constraints of this repo.

---

## W-0015

status: open
created: 2026-03-08
updated: 2026-03-08

### Outcome

Determine whether `mcp_server.py` can rebuild the full LanceDB index from the `.md` files in the repo on startup, making the index fully recoverable from git. Measure rebuild time at current, 100-file, and 500-file corpus sizes.

### Context

Currently `.lancedb` is excluded from git and must persist locally. If the index can be rebuilt in under 5 seconds for a typical corpus, any stateless compute becomes viable.

---
