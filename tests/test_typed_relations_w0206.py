"""tests/test_typed_relations_w0206.py — Acceptance tests for W-0206.

Tests typed relation extraction and evaluation:
  AC1 — Ground truth JSON loads and has expected structure
  AC2 — score_typed_relations() function correctness with mock data
  AC3 — --typed-relations CLI flag runs without error
  AC4 — p07 with mocked LLM returning typed relations populates delta_proposal correctly
  AC5 — p08 writes typed predicates to the Turtle graph
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_GT_PATH = REPO_ROOT / "data" / "eval" / "typed-relations-ground-truth.json"
_TEST_FILE = "foundational_concepts/concept.md"

# ---------------------------------------------------------------------------
# Helpers (mirrors test_llm_extraction_w0204.py pattern)
# ---------------------------------------------------------------------------

def _make_mock_caller(response_json: dict):
    content = json.dumps(response_json)

    def _mock(model: str, system_prompt: str, user_prompt: str) -> str:  # noqa: ARG001
        return content

    return _mock


def _run_p07_with_mock_caller(source_path: str, mock_response: dict) -> dict:
    from pipeline.processors import (
        p01_sourcing, p02_preparation, p03_segmentation,
        p04_metadata, p05_domain_classification, p06_domain_matching,
        p07_concept_extraction,
    )

    state: dict = {"source_path": source_path, "strategy": "llm"}
    for proc in [p01_sourcing, p02_preparation, p03_segmentation,
                 p04_metadata, p05_domain_classification, p06_domain_matching]:
        state = proc.run(state, REPO_ROOT)

    mock_caller = _make_mock_caller(mock_response)
    with patch.object(p07_concept_extraction, "_gh_models_caller", mock_caller):
        state = p07_concept_extraction.run(state, REPO_ROOT)
    return state


# ---------------------------------------------------------------------------
# AC1 — Ground truth JSON structure
# ---------------------------------------------------------------------------

def test_ground_truth_file_exists() -> None:
    assert _GT_PATH.exists(), f"Ground truth file not found: {_GT_PATH}"


def test_ground_truth_top_level_keys() -> None:
    data = json.loads(_GT_PATH.read_text())
    assert "version" in data
    assert "annotated_files" in data
    assert "relation_types" in data


def test_ground_truth_has_ten_files() -> None:
    data = json.loads(_GT_PATH.read_text())
    assert len(data["annotated_files"]) == 10


def test_ground_truth_entries_have_required_keys() -> None:
    data = json.loads(_GT_PATH.read_text())
    for entry in data["annotated_files"]:
        assert "source" in entry, f"Missing 'source' in {entry}"
        assert "slug" in entry, f"Missing 'slug' in {entry}"
        assert "typed_relations" in entry, f"Missing 'typed_relations' in {entry}"


def test_ground_truth_typed_relations_have_target_and_rel() -> None:
    data = json.loads(_GT_PATH.read_text())
    valid_types = set(data["relation_types"])
    for entry in data["annotated_files"]:
        for rel in entry["typed_relations"]:
            assert "target" in rel, f"Missing 'target': {rel}"
            assert "rel" in rel, f"Missing 'rel': {rel}"
            assert rel["rel"] in valid_types, (
                f"Unknown rel type '{rel['rel']}' in {entry['slug']}"
            )


def test_ground_truth_targets_exist_in_corpus() -> None:
    """Every target slug should correspond to a file in foundational_concepts/."""
    data = json.loads(_GT_PATH.read_text())
    corpus = REPO_ROOT / "foundational_concepts"
    for entry in data["annotated_files"]:
        for rel in entry["typed_relations"]:
            target = rel["target"]
            assert (corpus / f"{target}.md").exists(), (
                f"Target '{target}' referenced in {entry['slug']} not found in corpus"
            )


# ---------------------------------------------------------------------------
# AC2 — score_typed_relations() correctness
# ---------------------------------------------------------------------------

def test_score_typed_relations_perfect_match() -> None:
    from pipeline.eval import score_typed_relations

    predicted = [
        {"id": "assertion/term", "rel": "contrasts"},
        {"id": "assertion/class", "rel": "contrasts"},
    ]
    ground_truth = [
        {"target": "term", "rel": "contrasts"},
        {"target": "class", "rel": "contrasts"},
    ]
    scores = score_typed_relations(predicted, ground_truth)
    assert scores["exact"]["f1"] == pytest.approx(1.0)
    assert scores["target_only"]["f1"] == pytest.approx(1.0)


def test_score_typed_relations_wrong_type_penalises_exact() -> None:
    """Predicting the right target but wrong rel type hurts exact but not target-only."""
    from pipeline.eval import score_typed_relations

    predicted = [{"id": "assertion/term", "rel": "relatedTerm"}]  # wrong type
    ground_truth = [{"target": "term", "rel": "contrasts"}]
    scores = score_typed_relations(predicted, ground_truth)
    assert scores["exact"]["f1"] == pytest.approx(0.0)
    assert scores["target_only"]["f1"] == pytest.approx(1.0)


def test_score_typed_relations_empty_prediction() -> None:
    from pipeline.eval import score_typed_relations

    scores = score_typed_relations([], [{"target": "term", "rel": "contrasts"}])
    assert scores["exact"]["f1"] == pytest.approx(0.0)
    assert scores["target_only"]["f1"] == pytest.approx(0.0)


def test_score_typed_relations_both_empty() -> None:
    from pipeline.eval import score_typed_relations

    scores = score_typed_relations([], [])
    assert scores["exact"]["f1"] == pytest.approx(1.0)
    assert scores["target_only"]["f1"] == pytest.approx(1.0)


def test_score_typed_relations_by_type_breakdown() -> None:
    from pipeline.eval import score_typed_relations

    predicted = [
        {"id": "assertion/term", "rel": "contrasts"},
        {"id": "assertion/class", "rel": "uses"},  # wrong type for class
    ]
    ground_truth = [
        {"target": "term", "rel": "contrasts"},
        {"target": "class", "rel": "contrasts"},  # class should be contrasts
    ]
    scores = score_typed_relations(predicted, ground_truth)
    # contrasts: predicted={term}, gt={term, class} → P=1.0 R=0.5 F1=0.667
    assert scores["by_type"]["contrasts"]["f1"] == pytest.approx(2/3, rel=1e-3)
    # uses: predicted={class}, gt={} → P=0 R=1 F1=0
    assert scores["by_type"]["uses"]["f1"] == pytest.approx(0.0)


def test_score_typed_relations_partial_match() -> None:
    from pipeline.eval import score_typed_relations

    predicted = [
        {"id": "assertion/term", "rel": "contrasts"},
        {"id": "assertion/class", "rel": "contrasts"},
    ]
    ground_truth = [
        {"target": "term", "rel": "contrasts"},
        {"target": "class", "rel": "contrasts"},
        {"target": "individual", "rel": "contrasts"},
    ]
    scores = score_typed_relations(predicted, ground_truth)
    # P=1.0, R=2/3, F1=0.8
    assert scores["exact"]["f1"] == pytest.approx(0.8, rel=1e-3)


# ---------------------------------------------------------------------------
# AC3 — --typed-relations CLI flag
# ---------------------------------------------------------------------------

def test_typed_relations_cli_flag_runs() -> None:
    result = subprocess.run(
        [sys.executable, "pipeline/eval.py", "--typed-relations"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"eval.py --typed-relations failed:\n{result.stderr}"
    assert "Typed Relation Eval" in result.stdout


def test_typed_relations_cli_json_flag() -> None:
    result = subprocess.run(
        [sys.executable, "pipeline/eval.py", "--typed-relations", "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"eval.py --typed-relations --json failed:\n{result.stderr}"
    data = json.loads(result.stdout)
    assert "results" in data
    assert "aggregate" in data
    assert len(data["results"]) == 10


def test_typed_relations_rule_based_is_zero() -> None:
    """Rule-based on prose files should return 0.0 F1 (no YAML relations)."""
    result = subprocess.run(
        [sys.executable, "pipeline/eval.py", "--typed-relations", "--extractor", "rule-based", "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["aggregate"]["exact"]["f1"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# AC4 — p07 with mocked LLM returns typed relations in delta_proposal
# ---------------------------------------------------------------------------

_TYPED_MOCK_RESPONSE = {
    "label": "Concept",
    "comment": "An abstract unit of meaning.",
    "aliases": [],
    "tags": ["knowledge-representation"],
    "related": [
        {"id": "term",       "rel": "contrasts"},
        {"id": "class",      "rel": "contrasts"},
        {"id": "individual", "rel": "contrasts"},
    ],
}


def test_llm_typed_relations_in_delta_proposal() -> None:
    state = _run_p07_with_mock_caller(_TEST_FILE, _TYPED_MOCK_RESPONSE)
    proposal = state["delta_proposal"]
    assert "related" in proposal
    for r in proposal["related"]:
        assert "id" in r
        assert "rel" in r
        assert r["id"].startswith("assertion/")


def test_llm_typed_contrasts_relation_preserved() -> None:
    state = _run_p07_with_mock_caller(_TEST_FILE, _TYPED_MOCK_RESPONSE)
    related = state["delta_proposal"]["related"]
    rel_types = {r["rel"] for r in related}
    assert "contrasts" in rel_types


def test_llm_typed_relations_all_valid_predicates() -> None:
    valid = {"relatedTerm", "contrasts", "uses", "partOf", "instanceOf", "implements"}
    state = _run_p07_with_mock_caller(_TEST_FILE, _TYPED_MOCK_RESPONSE)
    for r in state["delta_proposal"]["related"]:
        assert r["rel"] in valid, f"Unexpected rel type: {r['rel']}"


# ---------------------------------------------------------------------------
# AC5 — p08 writes typed predicates to the Turtle graph
# ---------------------------------------------------------------------------

def test_p08_writes_typed_predicate_to_graph() -> None:
    """p08 should write ms:contrasts (or the rel value) as the predicate IRI."""
    from rdflib import Graph, URIRef
    from pipeline.processors import p08_ontology_build

    state = _run_p07_with_mock_caller(_TEST_FILE, _TYPED_MOCK_RESPONSE)
    state["graph"] = Graph()
    state = p08_ontology_build.run(state, REPO_ROOT)

    g: Graph = state["graph"]

    # The ms: namespace predicate for "contrasts" should appear in the graph
    ms_contrasts = URIRef("https://memory.example.org/ms/contrasts")
    typed_preds = list(g.predicates())
    assert ms_contrasts in typed_preds, (
        f"ms:contrasts not found in graph predicates. Predicates present: "
        + str([str(p) for p in typed_preds if "contrasts" in str(p) or "related" in str(p)])
    )


def test_p08_fallback_untyped_relation_uses_relatedTerm() -> None:
    """An 'id' with no 'rel' key (or rel=relatedTerm) should produce ms:relatedTerm."""
    from rdflib import Graph, URIRef
    from pipeline.processors import p08_ontology_build

    mock_no_rel = {
        **_TYPED_MOCK_RESPONSE,
        "related": [{"id": "term", "rel": "relatedTerm"}],
    }
    state = _run_p07_with_mock_caller(_TEST_FILE, mock_no_rel)
    state["graph"] = Graph()
    state = p08_ontology_build.run(state, REPO_ROOT)

    g: Graph = state["graph"]
    ms_related = URIRef("https://memory.example.org/ms/relatedTerm")
    assert ms_related in list(g.predicates()), "ms:relatedTerm not found in graph"
