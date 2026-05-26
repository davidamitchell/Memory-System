#!/usr/bin/env python3
"""pipeline/run_pipeline.py — Ontology pipeline entry point.

Processes one document (or a directory of documents) through all 12
processors and writes the versioned Turtle output to data/ontology/.

Usage:
    python pipeline/run_pipeline.py <path> [--strategy llm|rule-based] [--skip-errors]

    <path> may be a single .md file or a directory (processes all .md files).

Examples:
    python pipeline/run_pipeline.py foundational_concepts/concept.md
    python pipeline/run_pipeline.py foundational_concepts/ --strategy llm
    python pipeline/run_pipeline.py raw_document_corpus/ --strategy llm
    python pipeline/run_pipeline.py raw_document_corpus/ --strategy llm --skip-errors

Additive behaviour:
    Batch runs load the latest existing ontology as their starting graph, so
    each run *adds* to the accumulated knowledge rather than replacing it.
    Running multiple source directories in sequence therefore composes
    correctly — the second run builds on the first's output automatically.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root is two levels up from this file (pipeline/run_pipeline.py)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add repo root to sys.path so processors can be imported regardless of cwd
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.processors import (  # noqa: E402
    p01_sourcing,
    p02_preparation,
    p03_segmentation,
    p04_metadata,
    p05_domain_classification,
    p06_domain_matching,
    p07_concept_extraction,
    p08_ontology_build,
    p09_consistency_validation,
    p10_reconciliation,
    p11_version_commit,
    p12_export,
)

PROCESSORS = [
    p01_sourcing,
    p02_preparation,
    p03_segmentation,
    p04_metadata,
    p05_domain_classification,
    p06_domain_matching,
    p07_concept_extraction,
    p08_ontology_build,
    p09_consistency_validation,
    p10_reconciliation,
    p11_version_commit,
    p12_export,
]

# Split processors into extraction (per-file) and commit (once per batch)
_EXTRACT_PROCESSORS = PROCESSORS[:8]   # p01–p08
_COMMIT_PROCESSORS = PROCESSORS[8:]    # p09–p12


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        level=level,
    )


def collect_sources(path: Path) -> list[Path]:
    """Return a list of .md files to process."""
    if path.is_file():
        return [path]
    return sorted(p for p in path.rglob("*.md") if not p.name.startswith("README"))


def run_pipeline(source_path: str, strategy: str = "llm") -> dict:
    """Run the full 12-processor pipeline for a single document.

    Args:
        source_path: Path to the source file, relative to REPO_ROOT.
        strategy: Extraction strategy — ``"llm"`` (default) or ``"rule-based"``.

    Returns:
        Final pipeline state dict.
    """
    state: dict = {"source_path": source_path, "strategy": strategy}

    for processor in PROCESSORS:
        state = processor.run(state, REPO_ROOT)

    return state


def _load_latest_graph(repo_root: Path):
    """Load the latest versioned Turtle ontology, or return None if none exists.

    Used to prime the batch pipeline with the existing accumulated knowledge so
    that each new run *adds* to the graph rather than replacing it.
    """
    from rdflib import Graph  # noqa: PLC0415

    ontology_dir = repo_root / "data" / "ontology"
    ttl_files = sorted(ontology_dir.glob("v*.ttl")) if ontology_dir.exists() else []
    if not ttl_files:
        return None
    g = Graph()
    g.parse(str(ttl_files[-1]), format="turtle")
    logging.info(
        "  additive mode: loaded %d existing triples from %s",
        len(g),
        ttl_files[-1].name,
    )
    return g


def run_pipeline_batch(
    source_paths: list[str],
    strategy: str = "llm",
    skip_errors: bool = False,
) -> dict:
    """Run p01–p08 for each source (accumulating one graph), then p09–p12 once.

    Processing all files into a single ontology version rather than
    creating one version per file.

    Args:
        source_paths: Ordered list of source file paths relative to REPO_ROOT.
        strategy: Extraction strategy — ``"llm"`` (default) or ``"rule-based"``.
        skip_errors: When ``True``, log per-file failures and continue rather
            than aborting the whole batch.  Errors are collected in
            ``state["extraction_errors"]`` and the function still returns
            normally so p09–p12 run on the successfully processed files.
            When ``False`` (the default), any per-file exception propagates
            immediately and halts the batch.

    Returns:
        Final pipeline state dict after version commit and export.
        When *skip_errors* is True the dict may contain an
        ``"extraction_errors"`` key listing per-file failures.
    """
    batch_state: dict = {}  # carries accumulated graph across files

    # Prime with the existing ontology so this run *adds* to accumulated knowledge
    existing_graph = _load_latest_graph(REPO_ROOT)
    if existing_graph is not None:
        batch_state["graph"] = existing_graph

    extraction_errors: list[dict] = []
    total = len(source_paths)

    for idx, source_path in enumerate(source_paths, 1):
        logging.info("  [%d/%d] extracting: %s", idx, total, source_path)
        state: dict = {"source_path": source_path, "strategy": strategy}
        if "graph" in batch_state:
            state["graph"] = batch_state["graph"]

        try:
            for processor in _EXTRACT_PROCESSORS:
                state = processor.run(state, REPO_ROOT)
            batch_state["graph"] = state["graph"]
        except Exception as exc:  # noqa: BLE001
            logging.error(
                "  [%d/%d] ERROR — %s: %s: %s",
                idx, total, source_path, type(exc).__name__, exc,
            )
            if not skip_errors:
                raise
            extraction_errors.append({"path": source_path, "error": str(exc)})

    if extraction_errors:
        logging.warning(
            "  %d/%d file(s) failed during extraction (graph built from %d file(s)):",
            len(extraction_errors), total, total - len(extraction_errors),
        )
        for err in extraction_errors:
            logging.warning("    FAILED %s — %s", err["path"], err["error"])
        batch_state["extraction_errors"] = extraction_errors

    # Commit the accumulated graph as a single new version
    for processor in _COMMIT_PROCESSORS:
        batch_state = processor.run(batch_state, REPO_ROOT)

    return batch_state


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the ontology pipeline on one or more .md files.",
    )
    parser.add_argument(
        "path",
        help="Path to a .md file or a directory of .md files (relative to repo root or absolute).",
    )
    parser.add_argument(
        "--strategy",
        default="llm",
        choices=["llm", "rule-based"],
        help=(
            "Extraction strategy: 'llm' (default, for prose) or 'rule-based' "
            "(for structured front-matter corpora)."
        ),
    )
    parser.add_argument(
        "--skip-errors",
        action="store_true",
        help=(
            "In batch mode: log per-file failures and continue rather than "
            "aborting the whole run.  The process exits non-zero if any file "
            "failed.  Has no effect on single-file runs."
        ),
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging."
    )
    args = parser.parse_args()

    setup_logging(args.verbose)

    input_path = Path(args.path)
    if not input_path.is_absolute():
        input_path = REPO_ROOT / input_path

    sources = collect_sources(input_path)
    if not sources:
        logging.error("No .md files found at %s", args.path)
        sys.exit(1)

    logging.info("Processing %d file(s) from %s", len(sources), args.path)

    rel_paths = [str(s.relative_to(REPO_ROOT)) for s in sources]

    if len(rel_paths) == 1:
        # Single file: full 12-processor run
        final_state = run_pipeline(rel_paths[0], strategy=args.strategy)
    else:
        # Directory / multi-file: batch mode — accumulate all into one version
        logging.info("Batch mode: extracting all files, then committing once")
        final_state = run_pipeline_batch(
            rel_paths, strategy=args.strategy, skip_errors=args.skip_errors
        )

    diff = final_state.get("diff", {})
    if diff:
        prev = diff.get("prev_tag", "initial")
        next_ = diff.get("next_tag", "?")
        added = diff.get("triples_added", 0)
        removed = diff.get("triples_removed", 0)
        print(f"\n{prev} → {next_}: +{added} triples, {removed} removed")

    print(f"Output: {final_state.get('output_path')}")

    # --- Exit non-zero on any errors or validation conflicts ---
    exit_code = 0

    extraction_errors = final_state.get("extraction_errors", [])
    if extraction_errors:
        print(
            f"\nERROR: {len(extraction_errors)} file(s) failed during extraction:",
            file=sys.stderr,
        )
        for err in extraction_errors:
            print(f"  {err['path']}: {err['error']}", file=sys.stderr)
        exit_code = 1

    validation_report = final_state.get("validation_report", {})
    conflict_count = validation_report.get("conflict_count", 0)
    if conflict_count:
        version_tag = validation_report.get("version_tag", "?")
        print(
            f"\nWARNING: {conflict_count} conflict(s) found — "
            f"see data/reports/validation-{version_tag}.json",
            file=sys.stderr,
        )
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
