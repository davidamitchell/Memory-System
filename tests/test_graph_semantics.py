"""tests/test_graph_semantics.py — Integration tests for ontology graph semantics.

Loads the latest versioned Turtle file and asserts structural and semantic
properties that a valid, well-formed knowledge graph must satisfy.  These
tests catch pipeline bugs that produce syntactically valid Turtle but
semantically broken graphs (dangling references, missing labels, etc.).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY_DIR = REPO_ROOT / "data" / "ontology"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rdflib import Graph, Namespace, RDF, RDFS

MS = Namespace("https://memory.example.org/ms/")

_RELATIONSHIP_PREDICATES = [
    MS.relatedTerm, MS.implements, MS.instanceOf,
    MS.partOf, MS.contrasts, MS.uses,
]


@pytest.fixture(scope="module")
def graph() -> Graph:
    """Load the latest versioned ontology Turtle file."""
    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    assert ttl_files, "No versioned .ttl file found in data/ontology/ — run the pipeline first"
    g = Graph()
    g.parse(str(ttl_files[-1]), format="turtle")
    return g


@pytest.fixture(scope="module")
def assertion_nodes(graph):
    return list(graph.subjects(RDF.type, MS.AssertionNode))


# ---------------------------------------------------------------------------
# Completeness — every node has the required core triples
# ---------------------------------------------------------------------------

def test_all_nodes_have_label(graph, assertion_nodes):
    """Every AssertionNode must carry an rdfs:label triple (non-empty)."""
    missing = [
        str(n) for n in assertion_nodes
        if not any(True for _ in graph.objects(n, RDFS.label))
    ]
    assert missing == [], f"AssertionNodes missing rdfs:label: {missing}"


def test_all_labels_non_empty(graph, assertion_nodes):
    """rdfs:label values must be non-empty strings."""
    empty = [
        str(n) for n in assertion_nodes
        if any(str(lbl).strip() == "" for lbl in graph.objects(n, RDFS.label))
    ]
    assert empty == [], f"AssertionNodes with empty rdfs:label: {empty}"


def test_all_nodes_have_domain(graph, assertion_nodes):
    """Every AssertionNode must have an ms:inDomain triple."""
    missing = [
        str(n) for n in assertion_nodes
        if not any(True for _ in graph.objects(n, MS.inDomain))
    ]
    assert missing == [], f"AssertionNodes missing ms:inDomain: {missing}"


# ---------------------------------------------------------------------------
# Referential integrity — no dangling relation targets
# ---------------------------------------------------------------------------

def test_no_dangling_relation_targets(graph, assertion_nodes):
    """Every target of a typed relationship predicate must itself be an AssertionNode.

    A dangling reference (target URI that has no ms:AssertionNode type triple)
    indicates that the pipeline added a relation edge to a concept that was
    never properly extracted.
    """
    node_uris = {str(n) for n in assertion_nodes}
    dangling = []

    for node in assertion_nodes:
        for pred in _RELATIONSHIP_PREDICATES:
            for target in graph.objects(node, pred):
                if str(target) not in node_uris:
                    dangling.append(
                        f"{str(node).rsplit('/', 1)[-1]} "
                        f"--{str(pred).rsplit('/', 1)[-1]}--> "
                        f"{str(target).rsplit('/', 1)[-1]}"
                    )

    assert dangling == [], (
        f"Dangling relation targets (target not an AssertionNode):\n  "
        + "\n  ".join(dangling)
    )


# ---------------------------------------------------------------------------
# Domain distribution — not degenerate
# ---------------------------------------------------------------------------

def test_at_least_one_domain_assigned(graph, assertion_nodes):
    """The graph must assign at least one distinct domain across all nodes."""
    domains = set()
    for node in assertion_nodes:
        for d in graph.objects(node, MS.inDomain):
            domains.add(str(d))
    assert len(domains) >= 1, "No domain assignments found in graph"


# ---------------------------------------------------------------------------
# Provenance — extraction activities recorded
# ---------------------------------------------------------------------------

def test_extraction_activities_present(graph):
    """The graph must contain at least one ExtractionActivity provenance node."""
    from rdflib.namespace import PROV  # noqa: PLC0415

    activities = list(graph.subjects(RDF.type, MS.ExtractionActivity))
    assert len(activities) >= 1, "No ExtractionActivity nodes found — provenance missing"
