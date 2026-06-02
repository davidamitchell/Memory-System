"""tests/test_eval_w0203.py — Acceptance tests for W-0203.

Verifies the eval harness (pipeline/eval.py) against the foundational_concepts
corpus using the rule-based extractor, and checks the --extractor flag interface.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EVAL_SCRIPT = REPO_ROOT / "pipeline" / "eval.py"
FOUNDATIONAL_DIR = REPO_ROOT / "foundational_concepts"

EXPECTED_FILES = 35


def _run_eval(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(EVAL_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


# ---------------------------------------------------------------------------
# W-0203 AC1: eval.py runs without error against foundational_concepts/
# ---------------------------------------------------------------------------

def test_eval_runs_without_error() -> None:
    result = _run_eval("--corpus", "foundational_concepts/")
    assert result.returncode == 0, f"eval.py exited {result.returncode}:\n{result.stderr}"


# ---------------------------------------------------------------------------
# W-0203 AC2: report includes per-file and aggregate metrics for 35 files
# ---------------------------------------------------------------------------

def test_eval_json_contains_all_files() -> None:
    result = _run_eval("--corpus", "foundational_concepts/", "--json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert "results" in data
    assert len(data["results"]) == EXPECTED_FILES, (
        f"Expected {EXPECTED_FILES} results, got {len(data['results'])}"
    )


def test_eval_json_contains_four_field_metrics() -> None:
    result = _run_eval("--corpus", "foundational_concepts/", "--json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    per_file = data["results"][0]
    for field in ("label", "aliases", "related"):
        assert field in per_file, f"Missing field '{field}' in per-file result"
        for metric in ("precision", "recall", "f1"):
            assert metric in per_file[field], f"Missing metric '{metric}' in field '{field}'"


def test_eval_json_has_aggregate() -> None:
    result = _run_eval("--corpus", "foundational_concepts/", "--json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert "aggregate" in data
    for field in ("label", "aliases", "related"):
        assert field in data["aggregate"]


# ---------------------------------------------------------------------------
# W-0203 AC3: --extractor flag is accepted and selects the strategy
# ---------------------------------------------------------------------------

def test_extractor_flag_rule_based() -> None:
    result = _run_eval("--corpus", "foundational_concepts/", "--extractor", "rule-based", "--json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["extractor"] == "rule-based"


def test_extractor_flag_unknown_rejected() -> None:
    """An unknown extractor name must cause a non-zero exit."""
    result = _run_eval("--corpus", "foundational_concepts/", "--extractor", "nonexistent")
    assert result.returncode != 0
