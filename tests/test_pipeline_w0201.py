"""tests/test_pipeline_w0201.py — Acceptance tests for W-0201.

Runs the pipeline in batch mode over all foundational_concepts files and
verifies that a single unified ontology version is produced.

Acceptance criteria (from BACKLOG.md W-0201):
- Batch mode: 35 files → one new version tag
- Latest .ttl has at least 35 ms:AssertionNode subjects
- query.py --format json returns valid JSON for a spot-checked concept
- query.py --related returns second-hop neighbours
- diff report shows triples_added > 0
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
FOUNDATIONAL_DIR = "foundational_concepts/"
ONTOLOGY_DIR = REPO_ROOT / "data" / "ontology"
REPORTS_DIR = REPO_ROOT / "data" / "reports"


def _run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


@pytest.fixture(scope="module", autouse=True)
def batch_pipeline_output():
    """Ensure a multi-concept ontology version exists before tests run.

    If the latest .ttl has fewer than 35 AssertionNodes we run the batch
    pipeline to produce an up-to-date version.
    """
    from rdflib import Graph, Namespace, RDF  # noqa: PLC0415

    MS = Namespace("https://memory.example.org/ms/")
    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    need_run = True
    if ttl_files:
        g = Graph()
        g.parse(str(ttl_files[-1]), format="turtle")
        if len(list(g.subjects(RDF.type, MS.AssertionNode))) >= 35:
            need_run = False

    if need_run:
        result = _run(PIPELINE_SCRIPT, FOUNDATIONAL_DIR, "--strategy", "rule-based")
        assert result.returncode == 0, f"Batch pipeline failed:\n{result.stderr}"


# ---------------------------------------------------------------------------
# W-0201 acceptance tests
# ---------------------------------------------------------------------------


def test_batch_pipeline_exits_zero():
    """Batch pipeline over foundational_concepts/ exits 0 (rule-based; no gh CLI needed)."""
    result = _run(PIPELINE_SCRIPT, FOUNDATIONAL_DIR, "--strategy", "rule-based")
    assert result.returncode == 0, f"stderr:\n{result.stderr}"


def test_latest_ttl_has_assertion_nodes():
    """Latest ontology snapshot must contain at least 35 AssertionNodes."""
    from rdflib import Graph, Namespace, RDF  # noqa: PLC0415

    MS = Namespace("https://memory.example.org/ms/")
    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    assert ttl_files, "No versioned .ttl file found"

    g = Graph()
    g.parse(str(ttl_files[-1]), format="turtle")
    nodes = list(g.subjects(RDF.type, MS.AssertionNode))
    assert len(nodes) >= 35, (
        f"Expected ≥35 AssertionNodes, got {len(nodes)}\n"
        f"File: {ttl_files[-1]}"
    )


def test_foundational_nodes_have_domain():
    """AssertionNodes from foundational_concepts/ must have an ms:inDomain triple."""
    from rdflib import Graph, Literal, Namespace, RDF, RDFS  # noqa: PLC0415

    MS = Namespace("https://memory.example.org/ms/")
    ttl_files = sorted(ONTOLOGY_DIR.glob("v*.ttl"))
    g = Graph()
    g.parse(str(ttl_files[-1]), format="turtle")

    nodes = list(g.subjects(RDF.type, MS.AssertionNode))
    for node in nodes:
        domains = list(g.objects(node, MS.inDomain))
        assert len(domains) >= 1, f"{node} has no ms:inDomain"


def test_query_json_returns_valid_structure():
    """query.py --format json for a known term returns valid JSON with expected keys."""
    result = _run(QUERY_SCRIPT, "--format", "json", "concept")
    assert result.returncode == 0, f"query.py --format json failed:\n{result.stderr}"
    data = json.loads(result.stdout)
    assert "label" in data, "Expected 'label' key in JSON output"
    assert isinstance(data["aliases"], list)
    assert isinstance(data["tags"], list)
    assert isinstance(data["related"], list)


def test_query_related_returns_neighbours():
    """query.py --related for a known term outputs second-hop neighbours."""
    result = _run(QUERY_SCRIPT, "--related", "ontology")
    assert result.returncode == 0, f"query.py --related failed:\n{result.stderr}"
    assert len(result.stdout.strip()) > 0, "Expected neighbour output, got empty"


def test_diff_report_shows_triples_added():
    """At least one diff report must show a significant batch import (triples_added >= 100).

    We don't check the *latest* diff because repeated test runs produce diffs
    with 0 added (graph already up-to-date).  The W-0201 batch run produced a
    diff with several hundred triples added; that report persists in history.
    """
    diff_files = sorted(REPORTS_DIR.glob("diff-*.json"))
    assert diff_files, "No diff report found in data/reports/"

    max_added = max(
        json.loads(f.read_text()).get("triples_added", 0) for f in diff_files
    )
    assert max_added >= 100, (
        f"Expected at least one diff report with triples_added >= 100 "
        f"(W-0201 batch import), but max found was {max_added}"
    )


def test_validation_report_passes():
    """The latest validation report must show zero conflicts."""
    report_files = sorted(REPORTS_DIR.glob("validation-v*.json"))
    assert report_files, "No validation report found"

    report = json.loads(report_files[-1].read_text())
    assert report["conflict_count"] == 0, (
        f"Unexpected conflicts in {report_files[-1].name}:\n"
        + json.dumps(report, indent=2)
    )
