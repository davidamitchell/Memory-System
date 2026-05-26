"""tests/test_nlp_enrichment_w0205.py — Acceptance tests for W-0205.

Tests NLP enrichment in p02 and its integration with the p07 LLM strategy.
A mock spaCy model is used so that the tests pass without requiring the
``en_core_web_sm`` model to be downloaded (though it is used when
running the full eval harness).

A mock gh-models caller is used for p07 tests so no ``gh`` CLI is required.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Helpers — mock spaCy model
# ---------------------------------------------------------------------------

def _make_mock_spacy_doc(entities=(), noun_chunks=(), tokens=()):
    """Return a minimal mock spaCy Doc object."""
    ent_objs = [
        SimpleNamespace(text=e[0], label_=e[1], start_char=0, end_char=len(e[0]))
        for e in entities
    ]
    chunk_objs = [SimpleNamespace(text=c, root=SimpleNamespace(text=c.split()[-1])) for c in noun_chunks]
    token_objs = [
        SimpleNamespace(text=t, pos_="NOUN", lemma_=t.lower())
        for t in tokens
    ]

    # Use MagicMock so that iteration (__iter__) works correctly
    doc = MagicMock()
    doc.ents = ent_objs
    doc.noun_chunks = chunk_objs
    doc.__iter__ = MagicMock(return_value=iter(token_objs))
    return doc


def _make_mock_nlp(entities=(), noun_chunks=(), tokens=()):
    """Return a callable mock spaCy nlp object."""
    mock = MagicMock()
    mock.return_value = _make_mock_spacy_doc(entities, noun_chunks, tokens)
    return mock


# ---------------------------------------------------------------------------
# Helpers — mock gh models caller (replaces W-0204 OpenAI client pattern)
# ---------------------------------------------------------------------------

def _make_mock_llm_caller(response_json: dict):
    """Return a callable that mimics _gh_models_caller with a fixed response."""
    content = json.dumps(response_json)

    def _mock(model: str, system_prompt: str, user_prompt: str) -> str:  # noqa: ARG001
        return content

    return _mock


_MOCK_LLM_RESPONSE = {
    "label": "AI Agent",
    "comment": "An autonomous software entity that perceives and acts.",
    "aliases": ["agent", "autonomous agent"],
    "tags": ["ai", "agent", "autonomy"],
    "related": [{"id": "knowledge-graph", "rel": "relatedTerm"}],
}

_TEST_FILE = "glossary/ai-agent.md"
_RESEARCH_FILE = "raw_document_corpus/2026-05-12-data-product-ontology.md"


# ---------------------------------------------------------------------------
# Helper — run p02 with mock spaCy model
# ---------------------------------------------------------------------------

def _run_p02_with_mock_nlp(source_path: str, nlp_enabled: bool, mock_nlp=None) -> dict:
    from pipeline.processors import p01_sourcing, p02_preparation

    state: dict = {"source_path": source_path, "nlp": nlp_enabled}
    state = p01_sourcing.run(state, REPO_ROOT)

    if mock_nlp is not None:
        with patch.object(p02_preparation, "_nlp_model", mock_nlp):
            state = p02_preparation.run(state, REPO_ROOT)
    else:
        state = p02_preparation.run(state, REPO_ROOT)

    return state


# ---------------------------------------------------------------------------
# AC1: when nlp=False, output is identical to pre-W-0205 state
# ---------------------------------------------------------------------------

def test_nlp_disabled_output_unchanged() -> None:
    """p02 with nlp=False must not add nlp_annotations to state."""
    state = _run_p02_with_mock_nlp(_TEST_FILE, nlp_enabled=False)
    assert "front_matter" in state
    assert "body_text" in state
    assert "bold_definition" in state
    assert "nlp_annotations" not in state


def test_nlp_disabled_does_not_call_spacy() -> None:
    """spaCy model must not be loaded when nlp=False."""
    from pipeline.processors import p02_preparation

    mock_model = MagicMock()
    with patch.object(p02_preparation, "_nlp_model", mock_model):
        _run_p02_with_mock_nlp(_TEST_FILE, nlp_enabled=False)

    mock_model.assert_not_called()


# ---------------------------------------------------------------------------
# AC2: when nlp=True, nlp_annotations is present with correct structure
# ---------------------------------------------------------------------------

def test_nlp_enabled_adds_annotations_key() -> None:
    mock_nlp = _make_mock_nlp(
        entities=[("AI agent", "ORG")],
        noun_chunks=["autonomous agent", "software system"],
        tokens=["AI", "agent"],
    )
    state = _run_p02_with_mock_nlp(_TEST_FILE, nlp_enabled=True, mock_nlp=mock_nlp)
    assert "nlp_annotations" in state


def test_nlp_annotations_has_required_keys() -> None:
    mock_nlp = _make_mock_nlp(
        entities=[("AI agent", "ORG")],
        noun_chunks=["autonomous agent"],
        tokens=["AI", "agent"],
    )
    state = _run_p02_with_mock_nlp(_TEST_FILE, nlp_enabled=True, mock_nlp=mock_nlp)
    annotations = state["nlp_annotations"]
    assert "entities" in annotations
    assert "noun_chunks" in annotations
    assert "pos_tags" in annotations


def test_nlp_entities_have_required_fields() -> None:
    mock_nlp = _make_mock_nlp(entities=[("Knowledge Graph", "ORG"), ("Python", "PRODUCT")])
    state = _run_p02_with_mock_nlp(_TEST_FILE, nlp_enabled=True, mock_nlp=mock_nlp)
    for ent in state["nlp_annotations"]["entities"]:
        assert "text" in ent
        assert "label" in ent
        assert "start" in ent
        assert "end" in ent


def test_nlp_noun_chunks_have_required_fields() -> None:
    mock_nlp = _make_mock_nlp(noun_chunks=["knowledge graph", "language model"])
    state = _run_p02_with_mock_nlp(_TEST_FILE, nlp_enabled=True, mock_nlp=mock_nlp)
    for chunk in state["nlp_annotations"]["noun_chunks"]:
        assert "text" in chunk
        assert "root" in chunk


def test_nlp_pos_tags_have_required_fields() -> None:
    mock_nlp = _make_mock_nlp(tokens=["agent", "graph"])
    state = _run_p02_with_mock_nlp(_TEST_FILE, nlp_enabled=True, mock_nlp=mock_nlp)
    for tag in state["nlp_annotations"]["pos_tags"]:
        assert "text" in tag
        assert "pos" in tag
        assert "lemma" in tag


# ---------------------------------------------------------------------------
# AC3: nlp_annotations flow through to p07 LLM prompt
# ---------------------------------------------------------------------------

def test_nlp_annotations_passed_to_llm_prompt() -> None:
    """When nlp=True, p07 LLM strategy includes NLP annotations in the prompt."""
    from pipeline.processors import (
        p01_sourcing, p02_preparation,
        p03_segmentation, p04_metadata,
        p05_domain_classification, p06_domain_matching,
        p07_concept_extraction,
    )

    mock_nlp = _make_mock_nlp(
        entities=[("Knowledge Graph", "ORG")],
        noun_chunks=["autonomous agent", "knowledge graph"],
        tokens=["agent"],
    )

    captured_prompts: list[dict] = []

    def _capturing_caller(model: str, system_prompt: str, user_prompt: str) -> str:
        captured_prompts.append({"model": model, "system": system_prompt, "user": user_prompt})
        return json.dumps(_MOCK_LLM_RESPONSE)

    state: dict = {"source_path": _TEST_FILE, "strategy": "llm", "nlp": True}
    state = p01_sourcing.run(state, REPO_ROOT)
    with patch.object(p02_preparation, "_nlp_model", mock_nlp):
        state = p02_preparation.run(state, REPO_ROOT)
    for proc in [p03_segmentation, p04_metadata, p05_domain_classification, p06_domain_matching]:
        state = proc.run(state, REPO_ROOT)

    with patch.object(p07_concept_extraction, "_gh_models_caller", _capturing_caller):
        state = p07_concept_extraction.run(state, REPO_ROOT)

    assert len(captured_prompts) == 1
    user_message = captured_prompts[0]["user"]

    # The NLP section must appear in the prompt with all expected headers
    assert "NLP pre-analysis" in user_message
    assert "Named entities" in user_message
    assert "noun phrases" in user_message


def test_llm_with_nlp_produces_valid_delta_proposal() -> None:
    """p07 with nlp=True still produces a delta_proposal with correct schema."""
    from pipeline.processors import (
        p01_sourcing, p02_preparation,
        p03_segmentation, p04_metadata,
        p05_domain_classification, p06_domain_matching,
        p07_concept_extraction,
    )

    mock_nlp = _make_mock_nlp(
        entities=[("AI", "ORG")],
        noun_chunks=["ai agent"],
        tokens=["AI", "agent"],
    )
    mock_llm = _make_mock_llm_caller(_MOCK_LLM_RESPONSE)

    state: dict = {"source_path": _TEST_FILE, "strategy": "llm", "nlp": True}
    state = p01_sourcing.run(state, REPO_ROOT)
    with patch.object(p02_preparation, "_nlp_model", mock_nlp):
        state = p02_preparation.run(state, REPO_ROOT)
    for proc in [p03_segmentation, p04_metadata, p05_domain_classification, p06_domain_matching]:
        state = proc.run(state, REPO_ROOT)
    with patch.object(p07_concept_extraction, "_gh_models_caller", mock_llm):
        state = p07_concept_extraction.run(state, REPO_ROOT)

    proposal = state["delta_proposal"]
    required = {"assertion_id", "label", "comment", "aliases", "tags",
                "related", "primary_segment_hash", "all_segment_hashes"}
    assert required.issubset(set(proposal))


# ---------------------------------------------------------------------------
# AC4: rule-based strategy is unaffected by nlp flag
# ---------------------------------------------------------------------------

def test_rule_based_unaffected_by_nlp_flag() -> None:
    """nlp=True must not change rule-based extractor output schema."""
    from pipeline.processors import (
        p01_sourcing, p02_preparation,
        p03_segmentation, p04_metadata,
        p05_domain_classification, p06_domain_matching,
        p07_concept_extraction,
    )

    mock_nlp = _make_mock_nlp(entities=[("test", "ORG")])

    state: dict = {"source_path": _TEST_FILE, "strategy": "rule-based", "nlp": True}
    state = p01_sourcing.run(state, REPO_ROOT)
    with patch.object(p02_preparation, "_nlp_model", mock_nlp):
        state = p02_preparation.run(state, REPO_ROOT)
    for proc in [p03_segmentation, p04_metadata, p05_domain_classification, p06_domain_matching]:
        state = proc.run(state, REPO_ROOT)
    state = p07_concept_extraction.run(state, REPO_ROOT)

    proposal = state["delta_proposal"]
    required = {"assertion_id", "label", "comment", "aliases", "tags",
                "related", "primary_segment_hash", "all_segment_hashes"}
    assert required.issubset(set(proposal))


# ---------------------------------------------------------------------------
# AC5: nlp=True works on a research document (no crash)
# ---------------------------------------------------------------------------

def test_nlp_enabled_on_research_doc() -> None:
    mock_nlp = _make_mock_nlp(
        entities=[("data product", "ORG")],
        noun_chunks=["data product", "ontology layer"],
        tokens=["data", "product"],
    )
    state = _run_p02_with_mock_nlp(_RESEARCH_FILE, nlp_enabled=True, mock_nlp=mock_nlp)
    assert "nlp_annotations" in state
    assert isinstance(state["nlp_annotations"]["entities"], list)
    assert isinstance(state["nlp_annotations"]["noun_chunks"], list)


# ---------------------------------------------------------------------------
# AC6: existing tests still pass (smoke-test p02 without nlp flag)
# ---------------------------------------------------------------------------

def test_p02_backward_compatible_no_nlp_key_in_state() -> None:
    """p02 must work when 'nlp' key is absent from state (pre-W-0205 callers)."""
    from pipeline.processors import p01_sourcing, p02_preparation

    state: dict = {"source_path": _TEST_FILE}  # no "nlp" key
    state = p01_sourcing.run(state, REPO_ROOT)
    state = p02_preparation.run(state, REPO_ROOT)

    assert "front_matter" in state
    assert "body_text" in state
    assert "nlp_annotations" not in state
