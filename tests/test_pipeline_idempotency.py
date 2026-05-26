"""tests/test_pipeline_idempotency.py — E2E idempotency tests.

Runs the full pipeline on a single document twice in sequence and verifies
that the second run does not duplicate AssertionNodes.

Because the pipeline is additive (each run loads the previous TTL as the
starting graph), the same source document re-processed must not create a
second AssertionNode for the same concept — the URI is deterministic (derived
from the filename stem), and rdflib Graph deduplicates identical triples.

These are the fewest, slowest tests.  They are placed last in the test suite.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_SCRIPT = REPO_ROOT / "pipeline" / "run_pipeline.py"
ONTOLOGY_DIR = REPO_ROOT / "data" / "ontology"

# Use a single well-known file so we test idempotency for one concept.
_TARGET = "foundational_concepts/concept.md"
_CONCEPT_URI = "https://memory.example.org/ms/assertion/concept"


def _run_pipeline() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PIPELINE_SCRIPT), _TARGET, "--strategy", "rule-based"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


def _load_latest_graph():
    from rdflib import Graph  # noqa: PLC0415

    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    assert ttl_files, "No TTL file found"
    g = Graph()
    g.parse(str(ttl_files[-1]), format="turtle")
    return g


def _count_assertion_nodes(g) -> int:
    from rdflib import Namespace, RDF  # noqa: PLC0415

    MS = Namespace("https://memory.example.org/ms/")
    return sum(1 for _ in g.subjects(RDF.type, MS.AssertionNode))


# ---------------------------------------------------------------------------
# Idempotency tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def after_two_runs():
    """Run the pipeline on the same file twice; return (count_run1, count_run2)."""
    r1 = _run_pipeline()
    assert r1.returncode == 0, f"First pipeline run failed:\n{r1.stderr}"
    count1 = _count_assertion_nodes(_load_latest_graph())

    r2 = _run_pipeline()
    assert r2.returncode == 0, f"Second pipeline run failed:\n{r2.stderr}"
    count2 = _count_assertion_nodes(_load_latest_graph())

    return count1, count2


def test_assertion_node_count_stable(after_two_runs):
    """Running the same document twice must not add new AssertionNodes.

    The second run loads the graph produced by the first (additive mode)
    and re-processes the same file.  Because node URIs are derived from the
    filename stem, adding the same triples to an RDF graph is a no-op.
    """
    count1, count2 = after_two_runs
    assert count2 == count1, (
        f"AssertionNode count grew from {count1} to {count2} on second run "
        f"— the pipeline is not idempotent for repeated processing of the same file"
    )


def test_concept_node_has_unique_uri(after_two_runs):
    """The target concept must appear exactly once in the graph after two runs."""
    from rdflib import Graph, Namespace, RDF, URIRef  # noqa: PLC0415

    MS = Namespace("https://memory.example.org/ms/")
    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    g = Graph()
    g.parse(str(ttl_files[-1]), format="turtle")

    concept_node = URIRef(_CONCEPT_URI)
    type_triples = list(g.triples((concept_node, RDF.type, MS.AssertionNode)))
    assert len(type_triples) == 1, (
        f"Expected exactly 1 ms:AssertionNode triple for {_CONCEPT_URI}, "
        f"found {len(type_triples)}"
    )
