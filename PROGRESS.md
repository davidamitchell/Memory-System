# Progress

---

## 2026-05-23 — W-0200: 12-processor ontology pipeline (first slice)

Built the full end-to-end ontology pipeline for a single glossary file (`glossary/vector-embedding.md`).

**Changes:**
- `pipeline/processors/p01_sourcing.py` – p12_export.py: all 12 processors
- `pipeline/run_pipeline.py`: CLI orchestrator (single file and directory mode)
- `pipeline/query.py`: concept card CLI (`text` and `json` formats, `--related` flag)
- `pipeline/queries/concept_card.rq`: portable SPARQL SELECT query
- `pipeline/README.md`: processor table, namespace prefix table, output locations
- `tests/test_pipeline_w0200.py`: 9 acceptance tests (all passing)
- `data/ontology/v0001.ttl`: 35-triple Turtle snapshot
- `data/reports/validation-v0001.json`: 0 conflicts
- `data/reports/diff-initial-v0001.json`: +35 triples from baseline

**Acceptance criteria met:**
- `python pipeline/run_pipeline.py glossary/vector-embedding.md` → `data/ontology/v0001.ttl` ✓
- ≥12 triples (actual: 35) ✓
- `data/reports/validation-v0001.json` written, 0 conflicts ✓
- `python pipeline/query.py "vector embedding"` prints concept card ✓
- All 9 pytest tests pass ✓

**Mini-Retro**
1. Did the process work? Yes — 12 processors in sequence, each returning `{**state, new_keys}`, made the orchestrator trivial. The hardest part was getting the namespace URI consistent across all processors (solved by defining `_ms()` once per processor file).
2. What slowed down or went wrong? The `rdflib` `PROV` import path changed between versions (`from rdflib.namespace import PROV` is correct for 7.x). Small friction but worth noting for future rdflib updates.
3. What single change would prevent this next time? A shared `pipeline/namespaces.py` exporting `MS`, `PROV`, and `_ms()` would eliminate the per-file boilerplate and prevent any namespace drift. That belongs in W-0201 prep.
4. Is this a pattern? Yes — the "define constants locally per processor" pattern scales badly. Shared namespace module should be the first thing created when expanding to W-0201.

---

## 2026-05-23 — Consolidated two backlog files into BACKLOG.md

Rewrote `BACKLOG-v2.md` to reflect the actual system direction: ontology-based knowledge graph, inputs starting with Research repository documents.

**Changes:**
- Vision and Architecture sections replaced entirely (removed LanceDB/vector/capture-surface framing)
- W-0100, W-0101, W-0106, W-0107 marked `obsolete` (LanceDB-era, superseded by ADR-0002)
- All surface capture items (W-0102–W-0105, W-0108–W-0115) marked `deferred`
- Active Phase 1 (W-0200, W-0201, W-0202) promoted to top of file
- Deferred phases consolidated under a `## Deferred` section
- Research Cross-Reference and Outstanding Discovery tables updated
- LanceDB and Model2Vec entries removed from References

**Mini-Retro**
1. Did the process work? Yes — the scope was clear: defer capture surfaces, correct the vision, promote the active items. Python rewrites for bulk status changes and block reordering were faster and less error-prone than multiple individual edits.
2. What slowed down or went wrong? Nothing significant. The phase-reordering step required a Python extract-and-reassemble rather than a simple text replacement because the active block was at the end of a 68 KB file.
3. What single change would prevent this next time? A "phase order" index at the top of the backlog file would make it obvious when phases are out of priority order.
4. Is this a pattern? Yes — when a large architectural pivot happens, the backlog accumulates stale framing that compounds over sessions. The earlier the realignment, the less debt accumulates. Backlog coherence should be part of the self-improve step.



Three targeted corrections from the current session:

1. **"Search the repository" explained** — clarified that Phase 1 Entry step 4 means running 2–3 grep/glob queries before writing anything, to find existing work and surface retrieval-quality signals.
2. **Glossary links removed from build-loop-harness.md** — design/protocol documents should use plain prose; the Wikipedia-style cross-linking rule applies only to memory files.
3. **Self-Improve now mandates making changes** — Phase 7 of `build-loop-harness.md` and §17 of `copilot-instructions.md` both previously said "raise a backlog item" for harness changes, contradicting §7's "do not just answer — make the change." Both updated: small improvements ship in the same session; structural changes require an ADR first.

**Files updated:** `_docs/design/build-loop-harness.md`, `.github/copilot-instructions.md`, `CHANGELOG.md`, `learnings.md`

**Mini-Retro**
1. Did the process work? Yes — all three issues were small, well-scoped corrections. No ambiguity about intent.
2. What slowed down or went wrong? A missing heading in `learnings.md` was left by a prior edit that matched only the paragraph text; required a follow-up fix. Pattern: always view the file after editing to catch broken formatting.
3. What single change would prevent this next time? View the edited file immediately after every `edit` call to catch structural breakage before the next step.
4. Is this a pattern? Yes — the broken heading is a repeat of the earlier duplicate-content issue (see ADR-0004 retro). Add "view file after edit" to the validation checklist or as a standing rule.



Completed a full documentation coherence pass to align all docs with the definitive architecture: ontology-based knowledge store (Open-Brain). The original vector/LanceDB design was replaced before implementation; all documentation now reflects this as a full pivot with no dual-track framing.

**Files updated:**
- `README.md` — Rewritten as single-architecture doc. Removed dual-track "current vector / target ontology" structure, Quick Start, LanceDB cost line, embedding model references.
- `.github/copilot-instructions.md` — §1 (architecture), §11 (MCP tools), §12 (git), §13 (chain-of-thought), §15 (headless mode), §17 (Build Loop Harness entry), References.
- `.github/copilot-setup-steps.yml` — Removed embedding model pre-warm step (LanceDB-era artefact).
- `glossary/open-brain.md` — Definition now describes ontology-based knowledge graph.
- `glossary/lancedb.md` — Superseded notice added; reframed as a design concept replaced before implementation.
- `glossary/retrieval.md` — Rewritten around ontology traversal and graph queries.
- `glossary/semantic-search.md` — Superseded notice added; reframed as the replaced approach.
- `glossary/mcp-server.md` — Legacy prototype notice added; removed LanceDB references.
- `glossary/knowledge-graph.md` — Rewritten to describe the ontology as the knowledge graph implementation.
- `glossary/memory-file.md` — Removed "LanceDB vector index is a derived artefact" sentence; source document framing added.
- `glossary/embedding-model.md` — Superseded notice added; current production model framing removed.
- `_docs/design/build-loop-harness.md` — Phase 1 step 4 changed from "Call `search_brain`" to "Search the repository."

**Mini-Retro**
1. Did the process work? Yes — a systematic file-by-file pass with explicit superseded notices is the right approach for this kind of architectural pivot.
2. What slowed down or went wrong? Context compaction mid-session meant the four completed changes (README, copilot-instructions, copilot-setup-steps, open-brain glossary) were not committed; all work had to be resumed from the summary.
3. What single change would prevent this next time? Call `report_progress` after every 2–3 file edits, not at the end of a session. Mid-session commits prevent work loss on compaction.
4. Is this a pattern? Yes — any large documentation pass should be chunked into 2–3 file commits to keep state recoverable.

---

## 2026-05-23 — Build Loop Harness

Defined the Build Loop Harness: a seven-phase protocol (Entry, Plan, Execute, Validate, Correct, Close, Self-Improve) that keeps agents focused, reduces drift, manages context, leverages skills, and produces a self-correcting and self-improving workflow. Created `_docs/design/build-loop-harness.md` with the full protocol including a Mermaid flowchart, validation checklist, focus rules, and open questions. Added §17 to `.github/copilot-instructions.md` as a condensed always-on reference. Updated `_docs/design/README.md` index and `CHANGELOG.md`.

**Mini-Retro**
1. Did the process work? Yes — the existing repo conventions (§7 mini-retro, §13 chain-of-thought, skills protocol, backlog) gave clear anchoring points for each phase of the harness, so the design was coherent with no contradictions.
2. What slowed down or went wrong? Nothing significant. The main design decision was whether to embed the full harness in `copilot-instructions.md` or split it into a design document with a summary in instructions; the split approach keeps instructions scannable while preserving full detail.
3. What single change would prevent friction next time? The harness itself is now the answer — Entry's "state intent in one sentence" gate would have caught any ambiguity at the start.
4. Is this a pattern? Yes — structural meta-work (defining how to do work) benefits from the same loop as object-level work. The harness is now self-referential: it was produced using the conventions it encodes.

---

## 2026-05-23 — ADR-0004: provenance model and control plane

Reviewed ADR-0004 draft. Applied feedback: added standard MADR sections (Context, Decision, Consequences, References), made ADR-0004 supersede ADR-0003 explicitly, completed the PROV-O Turtle provenance example, defined Trust Metadata fields (source_authority, freshness_date, approval_state) with confidence weighting deferred to Open Questions, added Resolver Service identifier scheme (SHA-256 content URIs), added Prepared Segment to the document model. Updated design document to v2 with the full provenance and control plane architecture, 12-processor pipeline, new component diagram, updated sequence diagram. Marked ADR-0003 superseded.

**Mini-Retro**
1. Did the process work? Yes — the review identified the exact gaps (no MADR structure, incomplete Turtle example, undefined Trust Metadata) and each was addressed directly.
2. What slowed down or went wrong? The design document edit left duplicate content because the old_str matched only the header. Caught and fixed with a truncation.
3. What single change would prevent this next time? When replacing an entire file's content, use bash truncation rather than the edit tool to avoid partial-match issues.
4. Is this a pattern? Yes — replacing large documents via edit is error-prone. Add this to the agent instructions or use a bash write pattern for full-file replacements.

---

## 2026-05-23 — Ontology architecture design and setup

Updated the skills submodule to the latest commit. Created `_docs/design/` as the new conceptual design space, with a full ontology-system-design document covering all architectural components, the 11-processor pipeline, a component diagram, and a sequence diagram. Wrote ADR-0002 (move from vector storage to ontology) and ADR-0003 (upper/lower ontology architecture and processing pipeline). Updated README.md and `.github/copilot-instructions.md` to reflect the direction change. Updated CHANGELOG.md and `_docs/adr/README.md` index.

**Mini-Retro**
1. Did the process work? Yes — the design questions in the problem statement mapped cleanly onto ADRs and a design document.
2. What slowed down or went wrong? The problem statement raised an open question about additional processors needed beyond the obvious ones. These were answered (Consistency Validation, Merge/Reconciliation, Export/Serialisation) and added to both ADR-0003 and the design document.
3. What single change would prevent this next time? The open questions section in the design document is the right place to surface unresolved design choices. Future design sessions should start by reviewing and closing those questions.
4. Is this a pattern? Yes — design documents without an explicit "Open Questions" section tend to bury uncertainty in prose. The `_docs/design/` convention now includes this section by default.

---

## 2026-03-07 — Copilot headless-mode setup

Added `.github/copilot-setup-steps.yml` and `.vscode/mcp.json` so GitHub Copilot's coding agent can operate on this memory system from the GitHub web UI or mobile app with no local IDE. Added Section 15 (headless mode) to `.github/copilot-instructions.md`. Rebased PR onto main after main introduced `.github/copilot-instructions.md` (superseding `AGENTS.md`); moved the headless-mode section from the old AGENTS.md addition into copilot-instructions.md accordingly.

**Mini-Retro**
1. Did the process work? Yes — the files are straightforward; the main complexity was the rebase against a diverged main that had replaced AGENTS.md.
2. What slowed down or went wrong? The PR branch diverged from a main that had already removed AGENTS.md. Manual rebase was needed because the branch's base pre-dated PR #3 and #4.
3. What single change would prevent this next time? Merging main into feature branches earlier (before they diverge significantly) would prevent this class of conflict.
4. Is this a pattern? Potentially — if multiple Copilot branches run against the same repo simultaneously they will each diverge from main. Worth raising in the backlog.

---

## 2026-03-07 — Standardise agent instructions
## 2026-03-07

Standardisation pass: replaced `## 7. Mandatory System Self-Improvement` in `.github/copilot-instructions.md` with the unified **Continuous Improvement & Learning** framework (section 7). Added new `## 13. Chain-of-Thought Reasoning` section tailored to this repo's memory workflows; renumbered Privacy to section 14. Updated CHANGELOG.md under [Unreleased].

**Mini-Retro**
1. Did the process work? Yes — the instruction file was well-structured and the targeted replacement was straightforward.
2. What slowed down or went wrong? Nothing significant; the only ambiguity was whether the new Chain-of-Thought section should be numbered 13 or 14 (resolved by inserting before Privacy and bumping Privacy to 14).
3. What single change would prevent this next time? Keeping section numbers stable in the instructions document would remove renumbering ambiguity on future insertions.
4. Is this a pattern? No — first occurrence. Worth watching if further sections are added in future standardisation passes.

---

## 2026-03-07 — Align copilot-instructions with owner's personal Copilot instructions

Applied six targeted updates to `.github/copilot-instructions.md` to remove contradictions with the owner's personal Copilot instructions, without touching any repo-specific content (memory system constitution, LanceDB, MCP, folder structure, file naming, front matter, privacy, headless mode, chain-of-thought):

1. **§2 Skills** — Added `git submodule update --init --recursive` setup note and a "no synthesising substitutes" fallback rule.
2. **§7 Identity as Architect** — Replaced hollow "You are a collaborator that learns" blockquote with direct "Complete the work. Improve the system." wording.
3. **§7 Mini-Retro** — Added mandate-action note after the four questions: "Do not just answer — make the change."
4. **§7 Signal table** — Added missing `Missing skill` row.
5. **§7 "Done" checklist** — Added `CHANGELOG.md updated if behaviour changed` and `remove-ai-slop run on committed prose`.

**Mini-Retro**
1. Did the process work? Yes — all changes were surgical text replacements with no structural side effects.
2. What slowed down or went wrong? Nothing significant; the changes were clearly specified in the issue.
3. What single change would prevent this next time? Nothing to improve — the issue was well-specified and straightforward.
4. Is this a pattern? This is a recurring "sync personal instructions → repo instructions" task. Could add a periodic review backlog item.

---

## 2026-03-08 — Merge-conflict audit and branch hygiene (W-0002)

Audited all open pull requests against `main`. Only one open PR existed at the time of this session (PR #7 — this branch). All earlier PRs (#1–#6) had already been merged or closed. The current branch (`copilot/clean-up-merge-conflicts`) is a single clean commit ahead of `main` with no conflicts. No rebases or fixup commits were needed. Marked W-0002 as done in `BACKLOG.md`.

**Mini-Retro**
1. Did the process work? Yes — systematic enumeration of open PRs via GitHub MCP confirmed there was nothing to resolve.
2. What slowed down or went wrong? The shallow clone meant `git fetch --unshallow` was needed before seeing full branch history; this is minor but worth noting.
3. What single change would prevent this next time? Nothing actionable — the task is complete. The scheduled-workflow idea (W-0002 notes) is still worth exploring for future prevention.
4. Is this a pattern? Yes — same pattern observed in the headless-mode PR (see 2026-03-07 retro). W-0002 now closed.

---

## 2026-03-08 — Mobile capture discovery backlog (W-0003–W-0015) and doc validation

Added 13 discovery backlog items (W-0003 through W-0015) covering all viable mobile capture and retrieval paths: Slack bot, Claude iOS MCP, ChatGPT Actions, Gemini/Google ecosystem, Grok/X DM bot, iOS Shortcuts + GitHub API, Raycast/Alfred, `remember` CLI, Telegram bot, `inbox/` folder, Apple Watch dictation, self-hosted MCP server options, and LanceDB index rebuild evaluation. Fixed W-0002 duplicate `### Notes` / `---` formatting artifact. Fixed CHANGELOG.md duplicate [Unreleased] entries and added mobile capture changelog entry. Fixed stale `AGENTS.md` link in `projects/2026-03-07-copilot-headless-mode.md`. Added ADR index table to `_docs/adr/README.md`. Strengthened archived header in `getting-started-prompt.md`.

**Mini-Retro**
1. Did the process work? Yes — the issue was fully specified with exact content for each backlog item, making this a clean writing task.
2. What slowed down or went wrong? CHANGELOG.md had duplicate [Unreleased] entries from a prior session; required careful deduplication to avoid losing content.
3. What single change would prevent this next time? A lint check or note in the CHANGELOG template reminding to deduplicate before adding new entries would prevent accumulation of duplicate blocks.
4. Is this a pattern? The duplicate CHANGELOG entries appear to be a one-off from a previous PR merge. Watch for it on future PRs that touch CHANGELOG.md.

---

## 2026-03-13 — BACKLOG-v2.md — implementation-ready roadmap

Created `BACKLOG-v2.md` as a complete, shaped build plan for the future of the memory system. The file contains a Vision section, an Architecture section (with plain-text layered diagram), a Research Cross-Reference table, an Outstanding Discovery section, and 11 atomic work items (W-0100–W-0110) across 5 phases:

- Phase 1 — Fix the foundation: W-0100 (pre-computed embeddings, cold-start fix) and W-0101 (Model2Vec evaluation)
- Phase 2 — Frictionless capture: W-0102 (inbox/ folder), W-0103 (triage automation), W-0104 (iOS Shortcut), W-0105 (CLI remember/recall)
- Phase 3 — Retrieval quality: W-0106 (hybrid search), W-0107 (related-memories linking)
- Phase 4 — Async capture channels: W-0108 (Telegram bot), W-0109 (Slack bot)
- Phase 5 — Infrastructure: W-0110 (self-hosted MCP server)

`BACKLOG.md` was left untouched as the historical record of the discovery agenda. Updated CHANGELOG.md under [Unreleased].

**Mini-Retro**
1. Did the process work? Yes — the issue was well-specified with phases, format requirements, and partial content for the first two items. The structure from `BACKLOG.md` provided a clear format template.
2. What slowed down or went wrong? The problem statement was truncated mid-W-0102, requiring extrapolation of the acceptance criteria and all subsequent items. The extrapolation was grounded in the existing BACKLOG.md discovery items (W-0008 through W-0015) and the stated system goals.
3. What single change would prevent this next time? Providing the full content of W-0102 and a list of intended subsequent item IDs in the issue would have removed all ambiguity about scope.
4. Is this a pattern? Truncated issue descriptions have appeared before. Worth noting in the backlog that issue specifications should be written to fit within the issue body limit or split across comments.

---

## 2026-03-15 — BACKLOG-v2.md — structured relational layer, human door, proactive agent

Extended `BACKLOG-v2.md` with 5 new work items and 2 new phases, per issue "New items in backlog":

- Phase 3 (NEW) — Structured relational layer: W-0111 (discovery: Supabase MCP architecture — two-server vs unified), W-0112 (implementation: Supabase Postgres tables for contacts, meetings, TBD)
- Phase 4 (NEW) — Human door: W-0113 (auth model + Vercel skeleton), W-0114 (contacts view, inline editing, quick-capture form)
- Phase 7 (was Phase 5) — Infrastructure: W-0115 added (proactive/scheduled agent, blocked by W-0114 in daily use)
- Previous Phase 3–5 renumbered to Phase 5–7
- W-0102 context updated: capture friction note requiring the human-door quick-capture form to use the GitHub Contents API write path (same as iOS Shortcut and CLI), not a Supabase write path
- Research Cross-Reference and Outstanding Discovery tables updated

**Mini-Retro**
1. Did the process work? Yes — the issue was precisely specified with item content, format, and dependency rules. The existing item format in BACKLOG-v2.md provided a reliable template.
2. What slowed down or went wrong? Phase renumbering required careful edits in multiple places (phase headers, Outstanding Discovery, Research Cross-Reference). No errors, but this is mechanical work that is easy to miss.
3. What single change would prevent this next time? A script or table of contents in BACKLOG-v2.md that maps phase numbers to phase names would make renumbering visible at a glance — worth raising as a backlog item.
4. Is this a pattern? Phase renumbering has now happened once. If it happens again, a structured phase index or YAML front-matter list of phases would eliminate the manual touch points.

---

## References

1. [`.github/copilot-instructions.md` §5 and §7](../.github/copilot-instructions.md) — the mandate for PROGRESS.md and the Mini-Retro format.
2. [`BACKLOG.md`](./BACKLOG.md) — discovery-phase work items referenced in this history.
3. [`BACKLOG-v2.md`](./BACKLOG-v2.md) — implementation-ready roadmap updated during these sessions.

---

## 2026-05-24 — W-0207: GitHub Pages ontology browser

Added a progressively-enhanced static site on GitHub Pages for browsing the ontology without local tooling.

**Changes:**
- `pipeline/export_json.py`: reads latest `data/ontology/v*.ttl`, emits `docs/data/ontology.json` (26 concepts, 83 relations, 26 documents for W-0201 corpus)
- `pipeline/export_html.py`: stamps JSON data into `docs/index.html` — pre-rendered tables work with JS disabled
- `docs/data/ontology.json`: pre-committed export of v0011 ontology
- `docs/index.html`: four-section static page (Overview, Concepts, Relations, Documents)
- `docs/style.css`: minimal monospace-light theme, no external fonts or CDN dependencies
- `docs/app.js`: tab switcher, live search, concept detail panel — all progressive enhancement
- `.github/workflows/pages.yml`: runs exporters on push to `main`, deploys to GitHub Pages
- `BACKLOG.md`: W-0202 deferred, W-0207 added (status: ready, blocks W-0203), W-0203 updated (blocked-by adds W-0207)

**Acceptance criteria met:**
- `python pipeline/export_json.py` produces `docs/data/ontology.json` with counts {concepts: 26, relations: 83, documents: 26}
- `python pipeline/export_html.py` produces `docs/index.html` with all four sections as plain HTML tables
- `docs/style.css` and `docs/app.js` present; progressive enhancement layers: tabs, search, detail panel
- `.github/workflows/pages.yml` deploys on push to `main`
- All existing tests pass unchanged

**Mini-Retro**
1. Did the process work? Yes — the plan was well-specified with clear file outputs, a defined JSON schema, and an explicit render order. The batch-mode prov issue (single shared activity for all 26 docs) was discovered during implementation and resolved cleanly by using the concept-id-to-filename mapping instead.
2. What slowed down or went wrong? The `prov:used` triples in the current ontology all reference a single batch activity, so the document→concept link via prov didn't work. Resolved by matching concept id to stem of `ms:sourceDocument`.
3. What single change would prevent this next time? Per-document activities (one activity per pipeline run, not one per batch) would make prov-based document→concept mapping work directly. Worth noting for W-0200 refinement.
4. Is this a pattern? Yes — batch mode collapsed provenance. Future exporters or tools that need per-document attribution should plan for this in the pipeline architecture.

---

## 2026-05-24 — Corpus correction: raw_document_corpus/ brought to main branch

Discovered that the 50-file research document corpus intended as the primary prose extraction target was committed on the `copilot/ontology-experiment` branch under `raw_document_corpus/`, not on the main development branch. All pipeline development (W-0200–W-0207) had proceeded without these files available locally.

**Changes:**
- `raw_document_corpus/` (50 files): checked out from `copilot/ontology-experiment` and committed to the working branch. Documents are dated `2026-02-27` through `2026-05-20` and cover AI strategy, knowledge graphs, agentic systems, governance, and related research.
- `_docs/adr/0005-raw-document-corpus-primary-testing-corpus.md`: ADR recording the decision to canonise `raw_document_corpus/` as the latent-extraction corpus and clarifying its schema differences from `glossary/`.
- `learnings.md`: new entry — test corpus must be committed to the working branch before the work item that depends on it is started.

**Front-matter schema differences (glossary vs raw_document_corpus):**
- `tags` (glossary) → `themes` (raw_document_corpus)
- `aliases` (glossary) → absent in raw_document_corpus
- `related: [{file, rel}]` (glossary) → `cites: [slug]` + `related: [slug]` (raw_document_corpus)

**Mini-Retro**
1. Did the process work? Yes — the corpus was identified by inspecting the other branch and is now in the right place.
2. What slowed down or went wrong? The corpus was on the wrong branch and wasn't referenced in BACKLOG.md's W-0204 entry, so it wasn't obvious until inspecting branches directly.
3. What single change would prevent this next time? Any file a work item depends on must be committed to the canonical branch before the item is listed as "ready".
4. Is this a pattern? Yes — see learnings.md entry added this session.

---

## 2026-05-24 — W-0203 Eval Harness + W-0204 LLM Extractor

**What was done**

W-0203 and W-0204 implemented and all tests passing.

**W-0203 — Eval Harness**
- Created `pipeline/eval.py`: CLI that runs any extractor against a corpus directory and prints per-file + aggregate P/R/F1 for label, aliases, tags, related fields
- `--extractor rule-based|llm`, `--json`, `--corpus` flags
- Created `tests/test_eval_w0203.py` (10 tests — all pass)
- Baseline scores (rule-based, glossary corpus, 26 files): **label 1.000 / aliases 1.000 / tags 1.000 / related 1.000**

**W-0204 — LLM Extraction Strategy**
- Extended `pipeline/processors/p07_concept_extraction.py` with `strategy=llm` branch
- LLM extractor: structured system prompt → JSON `delta_proposal`; uses `openai>=1.0`; reads `OPENAI_API_KEY` and optional `OPENAI_BASE_URL` / `OPENAI_MODEL`; graceful fallback to front-matter on malformed JSON response
- `_llm_client` module-level variable is swappable seam for tests
- Created `tests/test_llm_extraction_w0204.py` (16 tests — all pass, mock client used)
- Added `openai>=1.0` to `requirements.txt`

**Full corpus batch**
- Fixed malformed YAML front-matter in `raw_document_corpus/2026-05-19-align-strategic-relevance-with-low-effort-knowledge-pathways.md` (stray inline list after `blocks:`)
- Ran batch over 86 files (glossary/ + _docs/adr/ + _docs/design/ + raw_document_corpus/)
- Result: v0038.ttl — **84 concepts, 83 relations, 86 documents**
- Rebuilt site: `docs/data/ontology.json` + `docs/index.html`

**Test results**: 42 passed, 0 failed

**Mini-Retro**
1. Did the process work? Yes — both eval harness and LLM strategy are working and tested.
2. What slowed down? One corpus file had malformed YAML (stray inline list). Fixed directly in source.
3. What single change would prevent this next time? Validate YAML front-matter at corpus ingestion time and report bad files upfront before running the full batch.
4. Is this a pattern? Latent data quality issues in corpus files will surface as pipeline exceptions — worth adding a pre-flight YAML validation step before W-0205.
