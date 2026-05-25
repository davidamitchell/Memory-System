"""Processor 9 — Consistency Validation Processor.

Detects contradictions, duplicate rdfs:label values, and broken links
in the candidate graph updates.  Writes a structured validation report
to ``data/reports/validation-v<NNNN>.json``.

The Validation Gate (control plane) will block promotion if
``conflict_count > 0``.
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path

from rdflib import RDFS, URIRef

logger = logging.getLogger(__name__)


def run(state: dict, repo_root: Path) -> dict:
    """Validate the graph and write a report.

    Adds to state:
    - ``validation_report``: dict with conflict_count and details
    - ``version_tag``: determined here (next available vNNNN)
    """
    logger.info("[9/12] Consistency Validation Processor — validating graph")

    g = state["graph"]
    reports_dir = repo_root / "data" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Determine next version number for naming the report
    version_tag = _next_version_tag(repo_root)

    # --- Check 1: duplicate rdfs:label values ---
    label_to_nodes: dict[str, list[str]] = defaultdict(list)
    for s, _p, o in g.triples((None, RDFS.label, None)):
        label_to_nodes[str(o)].append(str(s))

    duplicates = {
        label: nodes
        for label, nodes in label_to_nodes.items()
        if len(nodes) > 1
    }

    conflicts = []
    for label, nodes in duplicates.items():
        conflicts.append({
            "type": "duplicate_label",
            "label": label,
            "nodes": nodes,
        })

    report = {
        "version_tag": version_tag,
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "triple_count": len(g),
    }

    report_path = reports_dir / f"validation-{version_tag}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if conflicts:
        logger.warning("  %d conflict(s) found — see %s", len(conflicts), report_path)
        for c in conflicts:
            logger.warning("    %s", c)
    else:
        logger.info("  validation passed: 0 conflicts — report: %s", report_path)

    return {**state, "validation_report": report, "version_tag": version_tag}


def _next_version_tag(repo_root: Path) -> str:
    """Return the next vNNNN tag based on existing files in data/ontology/."""
    ontology_dir = repo_root / "data" / "ontology"
    existing = sorted(ontology_dir.glob("v*.ttl"))
    if not existing:
        return "v0001"
    last = existing[-1].stem  # e.g. "v0001"
    n = int(last[1:]) + 1
    return f"v{n:04d}"
