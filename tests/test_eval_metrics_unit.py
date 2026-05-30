"""tests/test_eval_metrics_unit.py — Unit tests for eval.py metric helpers.

These tests cover the pure-math functions _prf, _label_f1, and _avg.
They require no file I/O, no pipeline execution, and no subprocess calls.
"""
from __future__ import annotations

import pytest

from pipeline.eval import _avg, _label_f1, _prf


# ---------------------------------------------------------------------------
# _prf — set-based precision / recall / F1
# ---------------------------------------------------------------------------

class TestPrf:
    def test_exact_match_single(self):
        p, r, f = _prf(["a"], ["a"])
        assert p == 1.0
        assert r == 1.0
        assert f == 1.0

    def test_exact_match_multiple(self):
        p, r, f = _prf(["a", "b", "c"], ["a", "b", "c"])
        assert p == 1.0 and r == 1.0 and f == 1.0

    def test_case_insensitive(self):
        p, r, f = _prf(["Graph"], ["graph"])
        assert f == 1.0

    def test_partial_overlap(self):
        p, r, f = _prf(["a", "b", "c"], ["a", "b"])
        # predicted 3, truth 2, overlap 2
        assert p == pytest.approx(2 / 3)
        assert r == pytest.approx(1.0)
        assert f == pytest.approx(4 / 5)

    def test_no_overlap(self):
        p, r, f = _prf(["x", "y"], ["a", "b"])
        assert p == 0.0
        assert r == 0.0
        assert f == 0.0

    def test_both_empty(self):
        """When both sets are empty the score is 1.0 (nothing to predict, nothing expected)."""
        p, r, f = _prf([], [])
        assert p == 1.0 and r == 1.0 and f == 1.0

    def test_predicted_empty_gt_non_empty(self):
        """Zero recall when extractor predicts nothing."""
        p, r, f = _prf([], ["a", "b"])
        assert p == 0.0 and r == 0.0 and f == 0.0

    def test_predicted_non_empty_gt_empty(self):
        """No ground truth — precision is 0, recall is 1 (vacuously)."""
        p, r, f = _prf(["a"], [])
        assert p == 0.0
        assert r == 1.0
        assert f == 0.0

    def test_duplicates_in_predicted_treated_as_set(self):
        """Duplicate predictions should not inflate precision."""
        p, r, f = _prf(["a", "a", "b"], ["a", "b"])
        assert p == 1.0
        assert r == 1.0
        assert f == 1.0

    def test_f1_harmonic_mean(self):
        """F1 is the harmonic mean of precision and recall."""
        p, r, f = _prf(["a", "b", "c", "d"], ["a", "b"])
        # tp=2, pred=4, gt=2 → p=0.5, r=1.0 → F1 = 2*0.5*1.0/(0.5+1.0) = 2/3
        assert f == pytest.approx(2 / 3)


# ---------------------------------------------------------------------------
# _label_f1 — exact case-insensitive label matching
# ---------------------------------------------------------------------------

class TestLabelF1:
    def test_exact_match(self):
        p, r, f = _label_f1("Knowledge Graph", "Knowledge Graph")
        assert f == 1.0

    def test_case_insensitive_match(self):
        p, r, f = _label_f1("knowledge graph", "Knowledge Graph")
        assert f == 1.0

    def test_mismatch(self):
        p, r, f = _label_f1("Knowledge Graph", "Ontology")
        assert f == 0.0

    def test_hyphen_vs_space_mismatch(self):
        """Hyphen and space are different characters — no match expected."""
        p, r, f = _label_f1("knowledge-extraction", "knowledge extraction")
        assert f == 0.0

    def test_trailing_whitespace_ignored(self):
        """Leading/trailing whitespace is stripped before comparison."""
        p, r, f = _label_f1("  Graph  ", "Graph")
        assert f == 1.0

    def test_precision_recall_equal_to_f1(self):
        """For label matching, precision == recall == f1 (binary score)."""
        p, r, f = _label_f1("concept", "concept")
        assert p == r == f == 1.0

        p2, r2, f2 = _label_f1("concept", "domain")
        assert p2 == r2 == f2 == 0.0


# ---------------------------------------------------------------------------
# _avg — arithmetic mean over a list of floats
# ---------------------------------------------------------------------------

class TestAvg:
    def test_empty_list(self):
        assert _avg([]) == 0.0

    def test_single_value(self):
        assert _avg([0.75]) == 0.75

    def test_uniform_values(self):
        assert _avg([1.0, 1.0, 1.0]) == 1.0

    def test_mixed_values(self):
        assert _avg([0.0, 1.0]) == pytest.approx(0.5)

    def test_non_trivial_average(self):
        assert _avg([0.6, 0.8, 1.0]) == pytest.approx(0.8)
