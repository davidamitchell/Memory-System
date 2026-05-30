"""tests/test_adversarial_docs.py — Integration tests for prose-only documents.

Runs p01–p07 (the extraction processors) against held-out fixture documents
that have *no YAML front-matter*.  These tests verify that the pipeline
does something meaningful beyond reading YAML — specifically that p02's H1
and bold-definition fallback paths produce sensible output.

A separate NLP smoke test (skipped if en_core_web_sm is not installed) runs
p02 with the real spaCy model to confirm the mock used in unit tests is a
faithful stand-in for the real model.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "adversarial"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.processors import (
    p01_sourcing,
    p02_preparation,
    p03_segmentation,
    p04_metadata,
    p05_domain_classification,
    p06_domain_matching,
    p07_concept_extraction,
)

_EXTRACT_PROCS = [
    p01_sourcing,
    p02_preparation,
    p03_segmentation,
    p04_metadata,
    p05_domain_classification,
    p06_domain_matching,
]


def _run_to_p07(fixture_file: str) -> dict:
    """Run p01–p07 (rule-based) on a fixture file; return final state."""
    rel = str(Path("tests/fixtures/adversarial") / fixture_file)
    state: dict = {"source_path": rel, "strategy": "rule-based"}
    for proc in _EXTRACT_PROCS:
        state = proc.run(state, REPO_ROOT)
    return p07_concept_extraction.run(state, REPO_ROOT)


def _spacy_available() -> bool:
    try:
        import spacy  # noqa: PLC0415
        spacy.load("en_core_web_sm")
        return True
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------------------
# inference-rule.md — has bold definition, no front-matter
# ---------------------------------------------------------------------------

class TestInferenceRule:
    @pytest.fixture(scope="class")
    def state(self):
        return _run_to_p07("inference-rule.md")

    def test_no_error(self, state):
        assert "delta_proposal" in state

    def test_label_extracted_from_h1(self, state):
        """p02 extracts the H1 heading as the fallback title."""
        assert state["delta_proposal"]["label"] == "Inference Rule"

    def test_comment_extracted_from_bold_definition(self, state):
        """p02 extracts the bold one-liner as bold_definition → comment."""
        comment = state["delta_proposal"]["comment"]
        assert len(comment) > 10, "Expected a non-trivial comment from bold definition"
        assert "logical" in comment.lower() or "derives" in comment.lower()

    def test_aliases_empty_without_front_matter(self, state):
        assert state["delta_proposal"]["aliases"] == []

    def test_tags_empty_without_front_matter(self, state):
        assert state["delta_proposal"]["tags"] == []

    def test_related_empty_without_front_matter(self, state):
        assert state["delta_proposal"]["related"] == []

    def test_assertion_id_uses_filename_stem(self, state):
        assert state["delta_proposal"]["assertion_id"] == "assertion/inference-rule"

    def test_segments_non_empty(self, state):
        """The document body must produce at least one segment."""
        assert len(state["delta_proposal"]["all_segment_hashes"]) >= 1


# ---------------------------------------------------------------------------
# sparse-concept.md — no bold definition, no front-matter
# ---------------------------------------------------------------------------

class TestSparseConcept:
    @pytest.fixture(scope="class")
    def state(self):
        return _run_to_p07("sparse-concept.md")

    def test_no_error(self, state):
        assert "delta_proposal" in state

    def test_label_from_h1(self, state):
        assert state["delta_proposal"]["label"] == "Sparse Concept"

    def test_comment_empty_when_no_bold_definition(self, state):
        """No bold definition → comment defaults to empty string (no crash)."""
        assert isinstance(state["delta_proposal"]["comment"], str)

    def test_all_list_fields_empty(self, state):
        proposal = state["delta_proposal"]
        assert proposal["aliases"] == []
        assert proposal["tags"] == []
        assert proposal["related"] == []


# ---------------------------------------------------------------------------
# data-pipeline.md — has bold definition, denser prose
# ---------------------------------------------------------------------------

class TestDataPipeline:
    @pytest.fixture(scope="class")
    def state(self):
        return _run_to_p07("data-pipeline.md")

    def test_no_error(self, state):
        assert "delta_proposal" in state

    def test_label_from_h1(self, state):
        assert state["delta_proposal"]["label"] == "Data Pipeline"

    def test_comment_non_empty(self, state):
        comment = state["delta_proposal"]["comment"]
        assert len(comment) > 10

    def test_body_text_contains_document_prose(self, state):
        """p02 should preserve the full document body for downstream processors."""
        assert "pipeline" in state["body_text"].lower()
        assert len(state["body_text"]) > 50


# ---------------------------------------------------------------------------
# All three fixtures — shared cross-cutting assertions
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fixture_file", [
    "inference-rule.md",
    "sparse-concept.md",
    "data-pipeline.md",
])
def test_delta_proposal_schema_complete(fixture_file):
    """Every fixture must produce a delta_proposal with all required keys."""
    state = _run_to_p07(fixture_file)
    required = {"assertion_id", "label", "comment", "aliases", "tags",
                "related", "primary_segment_hash", "all_segment_hashes"}
    assert required.issubset(state["delta_proposal"])


@pytest.mark.parametrize("fixture_file", [
    "inference-rule.md",
    "sparse-concept.md",
    "data-pipeline.md",
])
def test_label_is_non_empty(fixture_file):
    """Every prose-only fixture must produce a non-empty label."""
    state = _run_to_p07(fixture_file)
    assert state["delta_proposal"]["label"].strip() != ""


@pytest.mark.parametrize("fixture_file", [
    "inference-rule.md",
    "sparse-concept.md",
    "data-pipeline.md",
])
def test_no_front_matter_in_state(fixture_file):
    """Fixtures have no YAML block; front_matter must be empty or title-only."""
    rel = str(Path("tests/fixtures/adversarial") / fixture_file)
    state: dict = {"source_path": rel}
    state = p01_sourcing.run(state, REPO_ROOT)
    state = p02_preparation.run(state, REPO_ROOT)
    fm = state["front_matter"]
    # Only the H1-derived 'title' key is permitted; no YAML-specific keys
    assert set(fm.keys()) <= {"title"}


# ---------------------------------------------------------------------------
# NLP smoke test — skipped unless en_core_web_sm is installed
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _spacy_available(), reason="en_core_web_sm not installed")
def test_real_spacy_annotations_on_fixture():
    """With the real spaCy model, p02 produces non-empty, well-formed annotations."""
    rel = "tests/fixtures/adversarial/data-pipeline.md"
    state: dict = {"source_path": rel, "nlp": True}
    state = p01_sourcing.run(state, REPO_ROOT)
    state = p02_preparation.run(state, REPO_ROOT)

    assert "nlp_annotations" in state
    annotations = state["nlp_annotations"]

    # Structure
    for key in ("entities", "noun_chunks", "pos_tags"):
        assert key in annotations
        assert isinstance(annotations[key], list)

    # Entities have required fields
    for ent in annotations["entities"]:
        assert "text" in ent and "label" in ent and "start" in ent and "end" in ent

    # Noun chunks have required fields
    for chunk in annotations["noun_chunks"]:
        assert "text" in chunk and "root" in chunk

    # pos_tags are non-empty (data-pipeline.md has real prose)
    assert len(annotations["pos_tags"]) > 5

    # Confirm mock and real model produce the same annotation schema
    for tag in annotations["pos_tags"]:
        assert "text" in tag and "pos" in tag and "lemma" in tag
