"""tests/test_pipeline_w0200.py — Acceptance tests for W-0200.

Runs the full 12-processor pipeline against glossary/vector-embedding.md
and verifies all acceptance criteria specified in BACKLOG.md W-0200.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_SCRIPT = REPO_ROOT / "pipeline" / "run_pipeline.py"
QUERY_SCRIPT = REPO_ROOT / "pipeline" / "query.py"
TARGET = "glossary/vector-embedding.md"
ONTOLOGY_DIR = REPO_ROOT / "data" / "ontology"


def _run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


@pytest.fixture(scope="module", autouse=True)
def pipeline_output():
    """Ensure the pipeline has produced at least v0001.ttl before tests run."""
    # If no versioned file exists, run the pipeline once
    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    if not ttl_files:
        result = _run(PIPELINE_SCRIPT, TARGET, "--strategy", "rule-based")
        assert result.returncode == 0, f"Pipeline failed:\n{result.stderr}"


# ---------------------------------------------------------------------------
# W-0200 acceptance tests
# ---------------------------------------------------------------------------

def test_pipeline_runs():
    """Pipeline exits 0 for the target file."""
    result = _run(PIPELINE_SCRIPT, TARGET, "--strategy", "rule-based")
    assert result.returncode == 0, f"stderr:\n{result.stderr}"


def test_output_ttl_exists():
    """data/ontology/v0001.ttl (or later) must exist after the pipeline."""
    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    assert len(ttl_files) >= 1, "No versioned .ttl file found in data/ontology/"


def test_output_valid_turtle():
    """The most recent .ttl file must be parseable by rdflib without error."""
    from rdflib import Graph  # noqa: PLC0415
    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    g = Graph()
    g.parse(str(ttl_files[-1]), format="turtle")  # raises on invalid Turtle


def test_triple_count():
    """The graph must contain at least 12 triples."""
    from rdflib import Graph  # noqa: PLC0415
    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    g = Graph()
    g.parse(str(ttl_files[-1]), format="turtle")
    assert len(g) >= 12, f"Only {len(g)} triples found — expected ≥12"


def test_required_triples_present():
    """Spot-check: label, comment, aliases, tags, related, prov:wasGeneratedBy."""
    from rdflib import Graph, Literal, Namespace, RDFS  # noqa: PLC0415
    from rdflib.namespace import PROV, RDF  # noqa: PLC0415

    MS = Namespace("https://memory.example.org/ms/")
    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    g = Graph()
    g.parse(str(ttl_files[-1]), format="turtle")

    node = next(g.subjects(RDF.type, MS.AssertionNode), None)
    assert node is not None, "No ms:AssertionNode found in graph"

    # label
    labels = list(g.objects(node, RDFS.label))
    assert any("Vector Embedding" in str(l) for l in labels), "rdfs:label missing"

    # comment
    comments = list(g.objects(node, RDFS.comment))
    assert len(comments) >= 1, "rdfs:comment missing"

    # aliases (expect 3)
    aliases = list(g.objects(node, MS.aliases))
    assert len(aliases) >= 3, f"Expected ≥3 aliases, got {len(aliases)}"

    # tags (expect 4)
    tags = list(g.objects(node, MS.hasTag))
    assert len(tags) >= 4, f"Expected ≥4 tags, got {len(tags)}"

    # related (expect 4 across all relationship predicates)
    from rdflib import URIRef
    RELATIONSHIP_PREDICATES = [
        "relatedTerm", "implements", "instanceOf", "partOf", "contrasts", "uses",
    ]
    related = []
    for pred_name in RELATIONSHIP_PREDICATES:
        pred_uri = URIRef(f"https://memory.example.org/ms/{pred_name}")
        related.extend(g.objects(node, pred_uri))
    assert len(related) >= 4, f"Expected ≥4 related terms, got {len(related)}"

    # provenance
    activities = list(g.objects(node, PROV.wasGeneratedBy))
    assert len(activities) >= 1, "prov:wasGeneratedBy missing"


def test_validation_report_written():
    """data/reports/validation-v0001.json (or similar) must exist and be valid JSON."""
    reports_dir = REPO_ROOT / "data" / "reports"
    report_files = sorted(reports_dir.glob("validation-v*.json"))
    assert len(report_files) >= 1, "No validation report found in data/reports/"

    report = json.loads(report_files[0].read_text())
    assert "conflict_count" in report
    assert report["conflict_count"] == 0


def test_query_runs():
    """query.py 'vector embedding' exits 0 and prints the concept label."""
    result = _run(QUERY_SCRIPT, "vector embedding")
    assert result.returncode == 0, f"query.py failed:\n{result.stderr}"
    assert "Vector Embedding" in result.stdout, (
        f"Expected 'Vector Embedding' in stdout:\n{result.stdout}"
    )


def test_query_json_output():
    """query.py --format json 'vector embedding' returns valid JSON with expected keys."""
    result = _run(QUERY_SCRIPT, "--format", "json", "vector embedding")
    assert result.returncode == 0, f"query.py --format json failed:\n{result.stderr}"
    data = json.loads(result.stdout)
    assert data["label"] == "Vector Embedding"
    assert len(data["aliases"]) >= 3
    assert len(data["tags"]) >= 4
    assert len(data["related"]) >= 4


def test_query_no_match():
    """query.py exits non-zero when term does not match any concept."""
    result = _run(QUERY_SCRIPT, "xyzzy-does-not-exist-99")
    assert result.returncode != 0
