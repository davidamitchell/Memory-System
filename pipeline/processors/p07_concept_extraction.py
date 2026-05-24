"""Processor 7 — Concept Extraction Processor.

Extracts candidate assertions from the document's front matter and
bold definition.  Produces a delta proposal and records the
Extraction Activity (with processor version and evidence segments).

Extraction sources:
  - ``rdfs:label``    ← front_matter.title
  - ``rdfs:comment``  ← bold_definition
  - ``ms:aliases``    ← front_matter.aliases
  - ``ms:hasTag``     ← front_matter.tags
  - ``ms:relatedTerm`` ← front_matter.related[].file (slug-based assertion IDs)
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

PROCESSOR_VERSION = "concept-extractor-v1.0.0"


def _slug(filename: str) -> str:
    """Convert a filename (with or without .md) to a URI-safe slug."""
    return re.sub(r"\.md$", "", filename.lower().strip())


def run(state: dict, repo_root: Path) -> dict:  # noqa: ARG001
    """Extract concept assertions and record the Extraction Activity.

    Adds to state:
    - ``delta_proposal``: dict describing the candidate assertions
    - ``extraction_activity``: dict recording this extraction run
    """
    logger.info("[7/12] Concept Extraction Processor — extracting assertions")

    fm = state["front_matter"]
    segments: list[dict] = state["segments"]

    # Build assertion ID from the source filename slug
    source_slug = _slug(Path(state["source_path"]).name)
    assertion_id = f"assertion/{source_slug}"

    # Related term assertion IDs derived from related[].file, with optional rel type
    related_assertions = [
        {
            "id": f"assertion/{_slug(r['file'])}",
            "rel": r.get("rel", "relatedTerm"),
        }
        for r in fm.get("related", [])
    ]

    delta_proposal = {
        "assertion_id": assertion_id,
        "label": fm.get("title", ""),
        "comment": state.get("bold_definition", ""),
        "aliases": fm.get("aliases", []),
        "tags": fm.get("tags", []),
        "related": related_assertions,
        "primary_segment_hash": segments[0]["hash"] if segments else "",
        "all_segment_hashes": [s["hash"] for s in segments],
    }

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    safe_ts = re.sub(r"[:\-]", "", timestamp).rstrip("Z")
    activity_id = f"activity/extract-{safe_ts}"

    extraction_activity = {
        "activity_id": activity_id,
        "processor_version": PROCESSOR_VERSION,
        "timestamp": timestamp,
        "used_segments": delta_proposal["all_segment_hashes"],
        "source_path": state["source_path"],
    }

    logger.info("  assertion: %s", assertion_id)
    logger.info(
        "  extracted: label=%r  aliases=%d  tags=%d  related=%d  segments=%d",
        delta_proposal["label"],
        len(delta_proposal["aliases"]),
        len(delta_proposal["tags"]),
        len(delta_proposal["related"]),
        len(segments),
    )

    return {**state, "delta_proposal": delta_proposal, "extraction_activity": extraction_activity}
