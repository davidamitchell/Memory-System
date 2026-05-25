#!/usr/bin/env python3
"""pipeline/run_pipeline.py — Ontology pipeline entry point.

Processes one document (or a directory of documents) through all 12
processors and writes the versioned Turtle output to data/ontology/.

Usage:
    python pipeline/run_pipeline.py <path>

    <path> may be a single .md file or a directory (processes all .md files).

Examples:
    python pipeline/run_pipeline.py glossary/vector-embedding.md
    python pipeline/run_pipeline.py glossary/
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


def run_pipeline(source_path: str) -> dict:
    """Run the full 12-processor pipeline for a single document.

    Args:
        source_path: Path to the source file, relative to REPO_ROOT.

    Returns:
        Final pipeline state dict.
    """
    state: dict = {"source_path": source_path}

    for processor in PROCESSORS:
        state = processor.run(state, REPO_ROOT)

    return state


def run_pipeline_batch(source_paths: list[str]) -> dict:
    """Run p01–p08 for each source (accumulating one graph), then p09–p12 once.

    Processing all files into a single ontology version rather than
    creating one version per file.

    Args:
        source_paths: Ordered list of source file paths relative to REPO_ROOT.

    Returns:
        Final pipeline state dict after version commit and export.
    """
    batch_state: dict = {}  # carries accumulated graph across files

    for source_path in source_paths:
        logging.info("  extracting: %s", source_path)
        state: dict = {"source_path": source_path}
        if "graph" in batch_state:
            state["graph"] = batch_state["graph"]

        for processor in _EXTRACT_PROCESSORS:
            state = processor.run(state, REPO_ROOT)

        batch_state["graph"] = state["graph"]

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
        final_state = run_pipeline(rel_paths[0])
    else:
        # Directory / multi-file: batch mode — accumulate all into one version
        logging.info("Batch mode: extracting all files, then committing once")
        final_state = run_pipeline_batch(rel_paths)

    diff = final_state.get("diff", {})
    if diff:
        prev = diff.get("prev_tag", "initial")
        next_ = diff.get("next_tag", "?")
        added = diff.get("triples_added", 0)
        removed = diff.get("triples_removed", 0)
        print(f"\n{prev} → {next_}: +{added} triples, {removed} removed")

    print(f"Output: {final_state.get('output_path')}")


if __name__ == "__main__":
    main()
