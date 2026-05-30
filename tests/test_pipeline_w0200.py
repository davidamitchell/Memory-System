"""tests/test_pipeline_w0200.py — Acceptance tests for W-0200.

Runs the full 12-processor pipeline against foundational_concepts/concept.md
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
TARGET = "foundational_concepts/concept.md"
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
    """Spot-check: at least one AssertionNode with label, comment, and prov:wasGeneratedBy."""
    from rdflib import Graph, Namespace, RDFS  # noqa: PLC0415
    from rdflib.namespace import PROV, RDF  # noqa: PLC0415

    MS = Namespace("https://memory.example.org/ms/")
    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    g = Graph()
    g.parse(str(ttl_files[-1]), format="turtle")

    node = next(g.subjects(RDF.type, MS.AssertionNode), None)
    assert node is not None, "No ms:AssertionNode found in graph"

    # label
    labels = list(g.objects(node, RDFS.label))
    assert len(labels) >= 1, "rdfs:label missing"

    # comment
    comments = list(g.objects(node, RDFS.comment))
    assert len(comments) >= 1, "rdfs:comment missing"

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
    """query.py 'concept' exits 0 and prints a concept label."""
    result = _run(QUERY_SCRIPT, "concept")
    assert result.returncode == 0, f"query.py failed:\n{result.stderr}"
    assert len(result.stdout.strip()) > 0, "Expected non-empty output from query.py"


def test_query_json_output():
    """query.py --format json 'concept' returns valid JSON with expected keys."""
    result = _run(QUERY_SCRIPT, "--format", "json", "concept")
    assert result.returncode == 0, f"query.py --format json failed:\n{result.stderr}"
    data = json.loads(result.stdout)
    assert "label" in data, "Expected 'label' key in JSON output"
    assert len(data["label"]) > 0, "Expected non-empty label"


def test_query_no_match():
    """query.py exits non-zero when term does not match any concept."""
    result = _run(QUERY_SCRIPT, "xyzzy-does-not-exist-99")
    assert result.returncode != 0
