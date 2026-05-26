"""Processor 12 — Export Processor.

Serialises the validated, versioned graph to RDF Turtle format and
writes it to ``data/ontology/v<NNNN>.ttl``.

The same graph can be serialised to JSON-LD or OWL with a single
``rdflib.Graph().serialize(format=...)`` call — no structural changes
needed.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def run(state: dict, repo_root: Path) -> dict:
    """Serialise the graph to Turtle and write the versioned .ttl file.

    Adds to state:
    - ``output_path``: str, path to the written .ttl file (relative to repo root)
    """
    logger.info("[12/12] Export Processor — serialising to Turtle")

    ontology_dir = repo_root / "data" / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)

    version_tag: str = state["version_tag"]
    output_file = ontology_dir / f"{version_tag}.ttl"

    g = state["graph"]
    turtle_str = g.serialize(format="turtle")
    output_file.write_text(turtle_str, encoding="utf-8")

    output_path = str(output_file.relative_to(repo_root))
    triple_count = len(g)

    logger.info(
        "  exported: %s (%d triples, %d bytes)",
        output_path,
        triple_count,
        len(turtle_str),
    )

    return {**state, "output_path": output_path}
