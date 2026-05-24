#!/usr/bin/env python3
"""pipeline/export_json.py — Ontology → JSON exporter.

Reads the latest versioned Turtle file from ``data/ontology/`` and emits
a self-contained JSON snapshot to ``docs/data/ontology.json``.

Schema
------
{
  "meta": {
    "version": "v0011",
    "generated": "<ISO-8601 UTC>",
    "counts": { "concepts": N, "relations": N, "documents": N }
  },
  "concepts": [
    {
      "id": "adr",
      "label": "Architecture Decision Record",
      "comment": "…",
      "aliases": ["ADR", "decision record"],
      "tags": ["adr", "architecture"],
      "domain": "VocabularyDomain",
      "related": ["madr", "open-brain"]
    }
  ],
  "relations": [
    { "from_id": "adr", "from_label": "Architecture Decision Record",
      "to_id": "madr",  "to_label":   "MADR" }
  ],
  "documents": [
    { "file": "glossary/adr.md", "segment_count": 4, "concept_ids": ["adr"] }
  ]
}

Usage
-----
    python pipeline/export_json.py
    python pipeline/export_json.py --out path/to/output.json
    python pipeline/export_json.py --ttl path/to/ontology.ttl
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rdflib import Graph, Namespace, RDF, RDFS  # noqa: E402

MS = Namespace("https://memory.example.org/ms/")


def _local(uri: str) -> str:
    """Return the local part of a URI (after last '/')."""
    return str(uri).rsplit("/", 1)[-1]


def load_latest_ttl(ontology_dir: Path) -> tuple[Graph, str]:
    """Load the most recent v*.ttl and return (graph, version_label)."""
    files = sorted(ontology_dir.glob("v*.ttl"))
    if not files:
        print("No ontology files found in data/ontology/. Run run_pipeline.py first.", file=sys.stderr)
        sys.exit(1)
    latest = files[-1]
    g = Graph()
    g.parse(str(latest), format="turtle")
    return g, latest.stem  # e.g. "v0011"


def export_ontology(g: Graph, version: str) -> dict:
    """Convert an rdflib Graph into the documented JSON schema."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # --- Concepts ---
    concepts: list[dict] = []
    concept_by_uri: dict[str, str] = {}  # full URI → id

    for node in g.subjects(RDF.type, MS.AssertionNode):
        node_str = str(node)
        cid = _local(node_str)
        concept_by_uri[node_str] = cid

        label = str(next(g.objects(node, RDFS.label), ""))
        comment = str(next(g.objects(node, RDFS.comment), ""))
        aliases = sorted(str(o) for o in g.objects(node, MS.aliases))
        tags = sorted(str(o) for o in g.objects(node, MS.hasTag))
        domain_uri = next(g.objects(node, MS.inDomain), None)
        domain = _local(str(domain_uri)) if domain_uri else ""
        related_ids = sorted(_local(str(r)) for r in g.objects(node, MS.relatedTerm))

        concepts.append(
            {
                "id": cid,
                "label": label,
                "comment": comment,
                "aliases": aliases,
                "tags": tags,
                "domain": domain,
                "related": related_ids,
            }
        )

    concepts.sort(key=lambda c: c["label"].lower())

    # Build a label lookup keyed by URIRef for fast access
    label_by_node: dict = {}
    for node in g.subjects(RDF.type, MS.AssertionNode):
        lbl = next(g.objects(node, RDFS.label), None)
        label_by_node[node] = str(lbl) if lbl else _local(str(node)).replace("-", " ").title()

    # --- Relations ---
    relations: list[dict] = []

    for node in g.subjects(RDF.type, MS.AssertionNode):
        from_label = label_by_node.get(node, _local(str(node)).replace("-", " ").title())
        for rel in g.objects(node, MS.relatedTerm):
            to_label = label_by_node.get(rel, _local(str(rel)).replace("-", " ").title())
            relations.append(
                {
                    "from_id": _local(str(node)),
                    "from_label": from_label,
                    "to_id": _local(str(rel)),
                    "to_label": to_label,
                }
            )

    relations.sort(key=lambda r: (r["from_label"].lower(), r["to_label"].lower()))

    # --- Documents (from PreparedSegment triples) ---
    # Concept IDs match their glossary filename (e.g. "adr" → "glossary/adr.md").
    # Batch mode records a single shared activity for all docs, so we derive the
    # document←→concept mapping from segment sourceDocument triples instead.
    doc_segments: dict[str, int] = defaultdict(int)

    for seg in g.subjects(RDF.type, MS.PreparedSegment):
        source = str(next(g.objects(seg, MS.sourceDocument), ""))
        if source:
            doc_segments[source] += 1

    # Derive per-document concept list: concept id == stem of sourceDocument filename
    doc_concepts: dict[str, list[str]] = {}
    for f in doc_segments:
        stem = Path(f).stem  # "glossary/adr.md" → "adr"
        # Only add if a matching concept exists
        if stem in {c["id"] for c in concepts}:
            doc_concepts[f] = [stem]
        else:
            doc_concepts[f] = []

    documents = [
        {
            "file": f,
            "segment_count": doc_segments[f],
            "concept_ids": doc_concepts.get(f, []),
        }
        for f in sorted(doc_segments)
    ]

    return {
        "meta": {
            "version": version,
            "generated": now,
            "counts": {
                "concepts": len(concepts),
                "relations": len(relations),
                "documents": len(documents),
            },
        },
        "concepts": concepts,
        "relations": relations,
        "documents": documents,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export ontology TTL to JSON for GitHub Pages.")
    parser.add_argument(
        "--ttl",
        type=Path,
        default=None,
        help="Path to a specific .ttl file (default: latest in data/ontology/)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "docs" / "data" / "ontology.json",
        help="Output path (default: docs/data/ontology.json)",
    )
    args = parser.parse_args()

    if args.ttl:
        g = Graph()
        g.parse(str(args.ttl), format="turtle")
        version = args.ttl.stem
    else:
        g, version = load_latest_ttl(REPO_ROOT / "data" / "ontology")

    data = export_ontology(g, version)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(
        f"Exported {data['meta']['counts']['concepts']} concepts, "
        f"{data['meta']['counts']['relations']} relations, "
        f"{data['meta']['counts']['documents']} documents → {args.out}"
    )


if __name__ == "__main__":
    main()
