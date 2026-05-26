"""Processor 1 — Sourcing Processor.

Captures the source document verbatim. The raw content is never modified
after this stage (Immutable Source Fidelity principle, ADR-0004).
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def run(state: dict, repo_root: Path) -> dict:
    """Read the source file verbatim and record its path.

    Args:
        state: Pipeline state dict (must contain ``source_path`` as a str
               relative to *repo_root*).
        repo_root: Absolute path to the repository root.

    Returns:
        Updated state with ``raw_content`` (verbatim file text) added.
    """
    logger.info("[1/12] Sourcing Processor — reading source document")

    source_path = state["source_path"]
    full_path = repo_root / source_path

    if not full_path.exists():
        raise FileNotFoundError(f"Source document not found: {full_path}")

    raw_content = full_path.read_text(encoding="utf-8")
    logger.debug("  source: %s (%d bytes)", source_path, len(raw_content))

    return {**state, "raw_content": raw_content}
