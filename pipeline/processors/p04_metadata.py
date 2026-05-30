"""Processor 4 — Metadata Processor.

Attaches retrieval, lineage, and trust metadata to the pipeline state.
Trust metadata fields follow ADR-0004: source_authority, freshness_date,
approval_state.

Confidence weighting is deferred (ADR-0004 Open Question Q1).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def run(state: dict, repo_root: Path) -> dict:  # noqa: ARG001
    """Attach metadata envelope to the pipeline state.

    Adds to state:
    - ``metadata``: dict with source_authority, freshness_date,
      approval_state, retrieval_time
    """
    logger.info("[4/12] Metadata Processor — attaching trust and lineage metadata")

    front_matter = state["front_matter"]
    retrieval_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Rule: files from the foundational_concepts/ path are authoritative (curated, hand-authored)
    source_path: str = state["source_path"]
    if source_path.startswith("foundational_concepts/"):
        source_authority = "authoritative"
    else:
        source_authority = "secondary"

    metadata = {
        "source_authority": source_authority,
        "freshness_date": front_matter.get("date", ""),
        "approval_state": "accepted",
        "retrieval_time": retrieval_time,
    }

    logger.debug("  metadata: %s", metadata)
    return {**state, "metadata": metadata}
