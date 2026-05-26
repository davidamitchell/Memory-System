"""tests/test_eval_regression.py — Integration regression gate for the eval harness.

Runs eval.py against foundational_concepts/ and asserts that aggregate F1
scores remain at or above the committed baselines in tests/eval_baseline.json.
A drop of more than `tolerance` below the baseline is treated as a regression.

To update the baseline after an intentional extractor change:
    python pipeline/eval.py --corpus foundational_concepts/ --json
then update tests/eval_baseline.json with the new f1 values.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EVAL_SCRIPT = REPO_ROOT / "pipeline" / "eval.py"
BASELINE_FILE = REPO_ROOT / "tests" / "eval_baseline.json"
FOUNDATIONAL_DIR = "foundational_concepts/"


def _run_eval_json(corpus: str = FOUNDATIONAL_DIR) -> dict:
    result = subprocess.run(
        [sys.executable, str(EVAL_SCRIPT), "--corpus", corpus, "--extractor", "rule-based", "--json"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"eval.py failed:\n{result.stderr}"
    return json.loads(result.stdout)


@pytest.fixture(scope="module")
def eval_output():
    return _run_eval_json()


@pytest.fixture(scope="module")
def baseline():
    return json.loads(BASELINE_FILE.read_text())


# ---------------------------------------------------------------------------
# Field-level F1 regression gates
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("field", ["label", "aliases", "tags", "related"])
def test_f1_above_baseline(eval_output, baseline, field):
    """Aggregate F1 for each field must not drop more than `tolerance` below baseline."""
    actual_f1 = eval_output["aggregate"][field]["f1"]
    threshold = baseline["f1"][field] - baseline["tolerance"]
    assert actual_f1 >= threshold, (
        f"{field} F1 regression: actual={actual_f1:.3f}, "
        f"baseline={baseline['f1'][field]:.3f}, "
        f"min_allowed={threshold:.3f}"
    )


# ---------------------------------------------------------------------------
# Sanity checks on eval output structure
# ---------------------------------------------------------------------------

def test_eval_covers_all_foundational_docs(eval_output):
    """eval.py must process every document in foundational_concepts/ (35 files)."""
    assert len(eval_output["results"]) == 35, (
        f"Expected 35 results, got {len(eval_output['results'])}"
    )


def test_aggregate_has_all_fields(eval_output):
    for field in ("label", "aliases", "tags", "related"):
        assert field in eval_output["aggregate"]
        for metric in ("precision", "recall", "f1"):
            assert metric in eval_output["aggregate"][field]


def test_no_file_produces_empty_label(eval_output):
    """Every individual file must produce a non-empty extracted label.

    An empty label means the extractor completely failed to identify the
    concept name — distinct from a label mismatch against ground truth,
    which can legitimately occur when the H1 heading uses spaces where the
    filename stem uses hyphens (e.g. 'Knowledge Extraction' vs 'knowledge-extraction').
    """
    empty_label = [
        r["file"] for r in eval_output["results"]
        if not r["label"].get("predicted", "").strip()
    ]
    assert empty_label == [], f"Files with empty extracted label: {empty_label}"
