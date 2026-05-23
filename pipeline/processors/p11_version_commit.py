"""Processor 11 — Version Commit Processor.

Tags the validated graph state as a new immutable snapshot, computes a
diff against the previous version, and writes structured diff metadata
to ``data/reports/diff-<prev>-<next>.json``.

Versioning is sequential (v0001, v0002, …).  The previous version's
triple count is used to compute added/removed counts.  History is
append-only; old snapshots are never deleted.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def run(state: dict, repo_root: Path) -> dict:
    """Compute diff, record version metadata, and update the pipeline state.

    Adds to state:
    - ``version_number``: int (e.g. 1 for v0001)
    - ``diff``: dict with triples_added, triples_removed, prev_tag, next_tag
    """
    logger.info("[11/12] Version Commit Processor — tagging version snapshot")

    version_tag: str = state["version_tag"]
    version_number = int(version_tag[1:])

    # Compute diff against previous version
    reports_dir = repo_root / "data" / "reports"
    ontology_dir = repo_root / "data" / "ontology"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Previous version tag (if any)
    prev_tag = f"v{(version_number - 1):04d}" if version_number > 1 else None
    prev_triple_count = 0

    if prev_tag:
        prev_ttl = ontology_dir / f"{prev_tag}.ttl"
        if prev_ttl.exists():
            from rdflib import Graph as _Graph  # local import to avoid cycle
            prev_g = _Graph()
            prev_g.parse(str(prev_ttl), format="turtle")
            prev_triple_count = len(prev_g)

    current_triple_count = len(state["graph"])
    triples_added = max(0, current_triple_count - prev_triple_count)
    triples_removed = max(0, prev_triple_count - current_triple_count)

    diff = {
        "prev_tag": prev_tag,
        "next_tag": version_tag,
        "triples_added": triples_added,
        "triples_removed": triples_removed,
        "prev_triple_count": prev_triple_count,
        "next_triple_count": current_triple_count,
    }

    if prev_tag:
        diff_filename = f"diff-{prev_tag}-{version_tag}.json"
    else:
        diff_filename = f"diff-initial-{version_tag}.json"

    diff_path = reports_dir / diff_filename
    diff_path.write_text(json.dumps(diff, indent=2), encoding="utf-8")

    diff_summary = (
        f"{prev_tag or 'initial'} → {version_tag}: "
        f"+{triples_added} triples, {triples_removed} removed"
    )
    logger.info("  version diff: %s", diff_summary)
    logger.info(diff_summary)

    return {
        **state,
        "version_number": version_number,
        "diff": diff,
    }
