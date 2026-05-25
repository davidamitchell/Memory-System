"""tests/test_llm_extraction_w0204.py — Acceptance tests for W-0204.

Tests the LLM extraction strategy in p07 using a mock LLM client so that
no API key or network access is required.  The mock returns a deterministic
JSON response that exercises the full extraction→delta_proposal path.
"""
from __future__ import annotations

import importlib
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
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_client(response_json: dict):
    """Return an object that mimics openai.OpenAI with a fixed chat response."""
    content = json.dumps(response_json)
    message = SimpleNamespace(content=content)
    choice = SimpleNamespace(message=message)
    completion = SimpleNamespace(choices=[choice])
    client = MagicMock()
    client.chat.completions.create.return_value = completion
    return client


def _run_p07_with_mock_llm(source_path: str, mock_response: dict) -> dict:
    """Run p07 with strategy=llm and a mock client; return the full state."""
    from pipeline.processors import (
        p01_sourcing,
        p02_preparation,
        p03_segmentation,
        p04_metadata,
        p05_domain_classification,
        p06_domain_matching,
        p07_concept_extraction,
    )

    state: dict = {"source_path": source_path, "strategy": "llm"}
    for proc in [p01_sourcing, p02_preparation, p03_segmentation,
                 p04_metadata, p05_domain_classification, p06_domain_matching]:
        state = proc.run(state, REPO_ROOT)

    # Inject the mock client into p07 before running
    mock_client = _make_mock_client(mock_response)
    with patch.object(p07_concept_extraction, "_llm_client", mock_client):
        state = p07_concept_extraction.run(state, REPO_ROOT)

    return state


_MOCK_RESPONSE = {
    "label": "AI Strategy",
    "comment": "A policy framework for artificial intelligence adoption.",
    "aliases": ["artificial intelligence strategy", "AI policy"],
    "tags": ["ai", "strategy", "governance", "policy"],
    "related": [
        {"id": "knowledge-graph", "rel": "relatedTerm"},
        {"id": "agent-first", "rel": "relatedTerm"},
    ],
}

# Use a glossary file for consistency with W-0203 baseline testing
_TEST_FILE = "glossary/ai-agent.md"


# ---------------------------------------------------------------------------
# W-0204 AC1: strategy=llm produces delta_proposal with correct schema
# ---------------------------------------------------------------------------

def test_llm_strategy_produces_delta_proposal() -> None:
    state = _run_p07_with_mock_llm(_TEST_FILE, _MOCK_RESPONSE)
    assert "delta_proposal" in state


@pytest.mark.parametrize("field", ["assertion_id", "label", "comment", "aliases", "tags",
                                    "related", "primary_segment_hash", "all_segment_hashes"])
def test_llm_delta_proposal_has_required_fields(field: str) -> None:
    state = _run_p07_with_mock_llm(_TEST_FILE, _MOCK_RESPONSE)
    assert field in state["delta_proposal"], f"Missing field '{field}' in delta_proposal"


def test_llm_delta_proposal_label_is_string() -> None:
    state = _run_p07_with_mock_llm(_TEST_FILE, _MOCK_RESPONSE)
    assert isinstance(state["delta_proposal"]["label"], str)
    assert state["delta_proposal"]["label"] == "AI Strategy"


def test_llm_delta_proposal_tags_are_lowercase_list() -> None:
    state = _run_p07_with_mock_llm(_TEST_FILE, _MOCK_RESPONSE)
    tags = state["delta_proposal"]["tags"]
    assert isinstance(tags, list)
    assert all(t == t.lower() for t in tags)


def test_llm_delta_proposal_related_have_id_and_rel() -> None:
    state = _run_p07_with_mock_llm(_TEST_FILE, _MOCK_RESPONSE)
    for r in state["delta_proposal"]["related"]:
        assert "id" in r
        assert "rel" in r
        assert r["id"].startswith("assertion/")


# ---------------------------------------------------------------------------
# W-0204 AC2: strategy=llm also works on a research document (no crash)
# ---------------------------------------------------------------------------

def test_llm_strategy_on_research_doc() -> None:
    research_file = "raw_document_corpus/2026-05-12-data-product-ontology.md"
    state = _run_p07_with_mock_llm(research_file, _MOCK_RESPONSE)
    proposal = state["delta_proposal"]
    assert proposal["label"]          # non-empty
    assert isinstance(proposal["tags"], list)
    assert isinstance(proposal["related"], list)
    assert isinstance(proposal["all_segment_hashes"], list)
    assert len(proposal["all_segment_hashes"]) > 0


# ---------------------------------------------------------------------------
# W-0204 AC3: activity record includes strategy field
# ---------------------------------------------------------------------------

def test_extraction_activity_records_strategy() -> None:
    state = _run_p07_with_mock_llm(_TEST_FILE, _MOCK_RESPONSE)
    assert "extraction_activity" in state
    assert state["extraction_activity"]["strategy"] == "llm"


# ---------------------------------------------------------------------------
# W-0204 AC4: rule-based strategy still produces identical output shape
# ---------------------------------------------------------------------------

def test_rule_based_strategy_output_schema_unchanged() -> None:
    """Ensure the rule-based path produces the same delta_proposal keys as llm."""
    from pipeline.processors import (
        p01_sourcing, p02_preparation, p03_segmentation,
        p04_metadata, p05_domain_classification, p06_domain_matching,
        p07_concept_extraction,
    )
    state: dict = {"source_path": _TEST_FILE, "strategy": "rule-based"}
    for proc in [p01_sourcing, p02_preparation, p03_segmentation,
                 p04_metadata, p05_domain_classification, p06_domain_matching]:
        state = proc.run(state, REPO_ROOT)
    state = p07_concept_extraction.run(state, REPO_ROOT)

    required_keys = {"assertion_id", "label", "comment", "aliases", "tags",
                     "related", "primary_segment_hash", "all_segment_hashes"}
    assert required_keys.issubset(set(state["delta_proposal"]))


# ---------------------------------------------------------------------------
# W-0204 AC5: graceful fallback when LLM returns malformed JSON
# ---------------------------------------------------------------------------

def test_llm_graceful_fallback_on_bad_json() -> None:
    """When the LLM returns non-JSON, p07 falls back to front-matter values."""
    from pipeline.processors import (
        p01_sourcing, p02_preparation, p03_segmentation,
        p04_metadata, p05_domain_classification, p06_domain_matching,
        p07_concept_extraction,
    )

    bad_content = "Sorry, I cannot help with that."
    message = SimpleNamespace(content=bad_content)
    choice = SimpleNamespace(message=message)
    completion = SimpleNamespace(choices=[choice])
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = completion

    state: dict = {"source_path": _TEST_FILE, "strategy": "llm"}
    for proc in [p01_sourcing, p02_preparation, p03_segmentation,
                 p04_metadata, p05_domain_classification, p06_domain_matching]:
        state = proc.run(state, REPO_ROOT)

    with patch.object(p07_concept_extraction, "_llm_client", mock_client):
        state = p07_concept_extraction.run(state, REPO_ROOT)

    # Should not raise; label should fall back to front-matter title
    proposal = state["delta_proposal"]
    assert proposal["label"]  # non-empty fallback
    assert isinstance(proposal["related"], list)
