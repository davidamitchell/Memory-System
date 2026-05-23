#!/usr/bin/env python3
"""pipeline/query.py — Concept card query CLI.

Loads the latest versioned Turtle file from data/ontology/ and queries
it for a concept by label or alias match.

Usage:
    python pipeline/query.py <search term>
    python pipeline/query.py --format json <search term>
    python pipeline/query.py --related <search term>
    python pipeline/query.py --format json --related <search term>

Examples:
    python pipeline/query.py "vector embedding"
    python pipeline/query.py --format json "mcp"
    python pipeline/query.py --related "vector embedding"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rdflib import Graph, Namespace, RDFS  # noqa: E402
from rdflib.namespace import PROV  # noqa: E402

MS = Namespace("https://memory.example.org/ms/")

CONCEPT_CARD_QUERY_FILE = REPO_ROOT / "pipeline" / "queries" / "concept_card.rq"


def load_latest_graph() -> Graph:
    """Load the most recent versioned Turtle file from data/ontology/."""
    ontology_dir = REPO_ROOT / "data" / "ontology"
    ttl_files = sorted(ontology_dir.glob("v*.ttl"))
    if not ttl_files:
        print("No ontology files found in data/ontology/. Run run_pipeline.py first.", file=sys.stderr)
        sys.exit(1)
    latest = ttl_files[-1]
    g = Graph()
    g.parse(str(latest), format="turtle")
    return g


def _ms(local: str):
    from rdflib import URIRef
    return URIRef(f"https://memory.example.org/ms/{local}")


def find_concept(g: Graph, search_term: str):
    """Return the URI of the first AssertionNode matching *search_term* by label or alias."""
    term_lower = search_term.lower()
    for node in g.subjects(predicate=None, object=_ms("AssertionNode")):
        # Check rdfs:label
        for label_obj in g.objects(node, RDFS.label):
            if term_lower in str(label_obj).lower():
                return node
        # Check ms:aliases
        for alias_obj in g.objects(node, _ms("aliases")):
            if term_lower in str(alias_obj).lower():
                return node
    return None


def get_concept_data(g: Graph, node) -> dict:
    """Collect all data for an AssertionNode into a dict."""
    label = str(next(g.objects(node, RDFS.label), ""))
    comment = str(next(g.objects(node, RDFS.comment), ""))
    aliases = sorted(str(o) for o in g.objects(node, _ms("aliases")))
    tags = sorted(str(o) for o in g.objects(node, _ms("hasTag")))

    # Related term labels (may not exist in graph for W-0200 single-file slice)
    related = []
    for rel_node in g.objects(node, _ms("relatedTerm")):
        rel_label = next(g.objects(rel_node, RDFS.label), None)
        if rel_label:
            related.append(str(rel_label))
        else:
            # Fall back to the local part of the URI
            uri = str(rel_node)
            local = uri.rsplit("/", 1)[-1]
            # Convert slug to title case
            related.append(local.replace("-", " ").title())

    # Evidence
    content_hash = ""
    source_doc = ""
    activity = next(g.objects(node, PROV.wasGeneratedBy), None)
    if activity:
        for seg in g.objects(activity, PROV.used):
            content_hash = str(next(g.objects(seg, _ms("contentHash")), ""))
            source_doc = str(next(g.objects(seg, _ms("sourceDocument")), ""))
            break  # use first segment

    return {
        "label": label,
        "definition": comment,
        "aliases": aliases,
        "tags": tags,
        "related": related,
        "evidence": {
            "hash": content_hash,
            "source": source_doc,
        },
    }


def get_neighbours(g: Graph, node, hops: int = 2) -> dict:
    """Traverse ms:relatedTerm edges up to *hops* hops."""
    visited = set()
    direct_nodes = list(g.objects(node, _ms("relatedTerm")))
    direct_labels = []

    second_hop: dict[str, list[str]] = {}

    for rel_node in direct_nodes:
        if rel_node in visited:
            continue
        visited.add(rel_node)
        rel_label = next(g.objects(rel_node, RDFS.label), None)
        if rel_label:
            label = str(rel_label)
        else:
            uri = str(rel_node)
            label = uri.rsplit("/", 1)[-1].replace("-", " ").title()
        direct_labels.append(label)

        if hops >= 2:
            hop2 = []
            for n2 in g.objects(rel_node, _ms("relatedTerm")):
                if n2 not in visited:
                    n2_label = next(g.objects(n2, RDFS.label), None)
                    if n2_label:
                        hop2.append(str(n2_label))
                    else:
                        uri2 = str(n2)
                        hop2.append(uri2.rsplit("/", 1)[-1].replace("-", " ").title())
            if hop2:
                second_hop[label] = hop2

    return {"direct": direct_labels, "second_hop": second_hop}


def print_concept_card(data: dict) -> None:
    width = 57
    bar = "─" * width
    title = data["label"]
    print(f"── {title} {'─' * max(0, width - len(title) - 4)}")
    print(f"Definition : {data['definition']}")
    if data["aliases"]:
        print(f"Aliases    : {', '.join(data['aliases'])}")
    if data["tags"]:
        print(f"Tags       : {', '.join(data['tags'])}")
    if data["related"]:
        print(f"Related    : {' · '.join(data['related'])}")
    h = data["evidence"]["hash"]
    s = data["evidence"]["source"]
    if h and s:
        short_hash = h.replace("sha256:", "")[:12]
        print(f"Evidence   : data/segments/{short_hash}….txt ({h[:20]}…)")
        print(f"Source     : {s}")
    print(bar)


def print_neighbours_card(root_label: str, neighbours: dict) -> None:
    width = 57
    bar = "─" * width
    print(f"── {root_label} (neighbours) {'─' * max(0, width - len(root_label) - 15)}")
    if neighbours["direct"]:
        print(f"Direct   : {' · '.join(neighbours['direct'])}")
    for via_label, hop2_labels in neighbours["second_hop"].items():
        print(f"Via {via_label} : {' · '.join(hop2_labels)}")
    print(bar)


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the ontology for a concept card.")
    parser.add_argument("term", help="Search term (label or alias, partial match)")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--related",
        action="store_true",
        help="Show two-hop concept neighbourhood instead of concept card",
    )
    args = parser.parse_args()

    g = load_latest_graph()
    node = find_concept(g, args.term)

    if node is None:
        print(f"No concept found matching '{args.term}'.", file=sys.stderr)
        sys.exit(1)

    if args.related:
        neighbours = get_neighbours(g, node)
        root_label = str(next(g.objects(node, RDFS.label), args.term))
        if args.format == "json":
            concept_data = get_concept_data(g, node)
            output = {
                "label": root_label,
                "neighbours": {
                    "direct": [
                        {"label": lbl} for lbl in neighbours["direct"]
                    ],
                    "second_hop": neighbours["second_hop"],
                },
            }
            print(json.dumps(output, indent=2))
        else:
            print_neighbours_card(root_label, neighbours)
    else:
        data = get_concept_data(g, node)
        if args.format == "json":
            print(json.dumps(data, indent=2))
        else:
            print_concept_card(data)


if __name__ == "__main__":
    main()
