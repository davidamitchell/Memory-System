# Pipeline

12-processor ontology pipeline for the Open-Brain knowledge store.

Processes Markdown documents into versioned RDF/Turtle knowledge graphs, with
full PROV-O provenance tracing from raw source to stored assertion.

---

## Quick Start

```bash
# Process a single file (LLM strategy — default)
python pipeline/run_pipeline.py glossary/vector-embedding.md

# Process all files in a directory with the LLM strategy (default)
python pipeline/run_pipeline.py raw_document_corpus/

# Process the structured glossary corpus with rule-based extraction
python pipeline/run_pipeline.py glossary/ --strategy rule-based

# Query a concept card
python pipeline/query.py "vector embedding"

# Query as JSON
python pipeline/query.py --format json "vector embedding"

# Show the two-hop neighbourhood
python pipeline/query.py --related "vector embedding"
```

---

## Extraction Strategies

P-07 (Concept Extraction) supports two pluggable extraction strategies selected
via the `--strategy` CLI flag or `state["strategy"]` in programmatic use:

| Strategy | Default? | Best for | Notes |
|----------|----------|----------|-------|
| `llm` | ✓ Yes | Unstructured prose (`raw_document_corpus/`) | Calls `gh models run` via the `gh` CLI; requires `gh auth` |
| `rule-based` | No | Structured glossary corpus (`glossary/`) | Reads YAML front-matter directly; near-perfect F1; no LLM calls |

**Why `llm` is the default:** The primary production corpus (`raw_document_corpus/`) is
unstructured prose with no YAML front-matter.  Running `rule-based` on prose silently
produces sparse extractions (title only, no relations).  Making `llm` the default ensures
the correct strategy fires without requiring an explicit flag.

**When to use `rule-based`:** Use `--strategy rule-based` explicitly for the glossary
corpus and for the W-0203 eval harness, where deterministic front-matter fidelity is the
measurement target and LLM calls are neither needed nor desirable.

```bash
# Eval harness — always uses rule-based or llm explicitly
python pipeline/eval.py --corpus glossary/ --extractor rule-based
python pipeline/eval.py --corpus glossary/ --extractor llm
```

---

## Processor Table

| # | Name | Input keys | Output keys |
|---|------|-----------|------------|
| P-01 | **Sourcing** | `source_path` | `raw_content` |
| P-02 | **Preparation** | `raw_content` | `front_matter`, `bold_definition`, `body_text` |
| P-03 | **Segmentation** | `body_text`, `bold_definition` | `segments` (list of `{hash, text, index}`) |
| P-04 | **Metadata** | `front_matter`, `source_path` | `metadata` |
| P-05 | **Domain Classification** | `source_path`, `front_matter` | `domain_signals` |
| P-06 | **Domain Matching** | `domain_signals` | `domain`, `domain_tie_break_applied` |
| P-07 | **Concept Extraction** | `front_matter`, `bold_definition`, `segments` | `delta_proposal`, `extraction_activity` |
| P-08 | **Ontology Build** | `delta_proposal`, `extraction_activity`, `segments`, `domain`, `source_path` | `graph` (merged into existing graph if present in state) |
| P-09 | **Consistency Validation** | `graph` | `validation_report`, `version_tag` |
| P-10 | **Reconciliation** | `validation_report` | *(state unchanged if no conflicts)* |
| P-11 | **Version Commit** | `graph`, `version_tag` | `version_number`, `diff` |
| P-12 | **Export** | `graph`, `version_tag` | `output_path` |

**Domain tie-break rule:** when a document emits multiple domain signals (e.g.
both `Vocabulary` and `Architecture`), the *first signal wins*.  The pipeline
records `domain_tie_break_applied: true` in the state when more than one signal
is present.

---

## Namespace Prefix Table

| Prefix | URI |
|--------|-----|
| `ms:` | `https://memory.example.org/ms/` |
| `prov:` | `http://www.w3.org/ns/prov#` |
| `rdfs:` | `http://www.w3.org/2000/01/rdf-schema#` |
| `xsd:` | `http://www.w3.org/2001/XMLSchema#` |

### Key `ms:` classes

| Term | Description |
|------|-------------|
| `ms:AssertionNode` | A single named concept / knowledge claim |
| `ms:ExtractionActivity` | PROV activity that produced the assertion |
| `ms:PreparedSegment` | A hashed body paragraph used as evidence |
| `ms:VocabularyDomain` | Upper-ontology domain for glossary terms |
| `ms:ArchitectureDomain` | Upper-ontology domain for architecture ADRs |

### Key `ms:` properties

| Property | Domain → Range | Description |
|----------|---------------|-------------|
| `ms:aliases` | `AssertionNode` → `xsd:string` | Alternative labels |
| `ms:hasTag` | `AssertionNode` → `xsd:string` | Taxonomy tags |
| `ms:relatedTerm` | `AssertionNode` → `AssertionNode` | Related concept link |
| `ms:inDomain` | `AssertionNode` → `*Domain` | Assigned upper-ontology domain |
| `ms:contentHash` | `PreparedSegment` → `xsd:string` | `sha256:<hex>` hash |
| `ms:sourceDocument` | `PreparedSegment` → `xsd:string` | Source file path |

---

## Output Locations

| Path | Contents |
|------|----------|
| `data/ontology/v<NNNN>.ttl` | Versioned Turtle snapshot (append-only) |
| `data/segments/<sha256>.txt` | Raw paragraph segments (content-addressed) |
| `data/reports/validation-v<NNNN>.json` | Validation gate results |
| `data/reports/diff-<prev>-<next>.json` | Triple diff between versions |

---

## Running Tests

```bash
python -m pytest tests/test_pipeline_w0200.py -v
```

---

## SPARQL Queries

Portable `.rq` query files live in `pipeline/queries/`.

| File | Description |
|------|-------------|
| `concept_card.rq` | Retrieve all concept-card fields for an `AssertionNode` |
| `neighbours.rq` | Two-hop neighbourhood traversal via `ms:relatedTerm` |
| `concept_json.rq` | Concept-card fields structured for JSON serialisation |
