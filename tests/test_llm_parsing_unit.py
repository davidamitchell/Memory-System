"""tests/test_llm_parsing_unit.py — Unit tests for p07 LLM response parsing.

Tests that _extract_llm (called via run()) correctly parses a wide range of
realistic raw string responses from `gh models run`, including edge cases
around markdown fences, Unicode labels, missing keys, extra fields, and
various fallback scenarios.

All tests replace _gh_models_caller with a synchronous in-process mock;
no subprocess, file system, or network access is required.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.processors import p07_concept_extraction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_state(raw_llm_response: str, title: str = "Test Concept") -> dict:
    """Return minimal pipeline state needed by p07 with a fixed mock LLM reply."""
    return {
        "source_path": "tests/fixtures/adversarial/inference-rule.md",
        "strategy": "llm",
        "front_matter": {"title": title},
        "bold_definition": "A bold definition from front matter.",
        "body_text": "Some document body text for testing.",
        "segments": [{"hash": "deadbeef01", "text": "body text"}],
    }


def _run_with_response(raw: str, title: str = "Test Concept") -> dict:
    state = _minimal_state(raw, title)
    with patch.object(p07_concept_extraction, "_gh_models_caller", return_value=raw):
        return p07_concept_extraction.run(state, REPO_ROOT)


# ---------------------------------------------------------------------------
# Happy-path parsing
# ---------------------------------------------------------------------------

class TestHappyPath:
    def test_clean_json_response(self):
        """Standard well-formed JSON is parsed correctly."""
        payload = {
            "label": "Inference Rule",
            "comment": "A logical statement that derives new facts.",
            "aliases": ["derivation rule", "logical rule"],
            "tags": ["logic", "reasoning", "inference"],
            "related": [{"id": "knowledge-base", "rel": "relatedTerm"}],
        }
        state = _run_with_response(json.dumps(payload))
        proposal = state["delta_proposal"]
        assert proposal["label"] == "Inference Rule"
        assert proposal["aliases"] == ["derivation rule", "logical rule"]
        assert "logic" in proposal["tags"]
        assert proposal["related"][0]["id"] == "assertion/knowledge-base"

    def test_markdown_fenced_json_backtick(self):
        """JSON wrapped in ```json ... ``` fences is stripped before parsing."""
        payload = {"label": "Data Pipeline", "comment": "A sequence of stages.", "aliases": [], "tags": ["etl"], "related": []}
        raw = f"```json\n{json.dumps(payload)}\n```"
        state = _run_with_response(raw)
        assert state["delta_proposal"]["label"] == "Data Pipeline"

    def test_markdown_fenced_json_no_lang(self):
        """JSON wrapped in plain ``` ... ``` fences is also stripped."""
        payload = {"label": "Graph", "comment": "A node-edge structure.", "aliases": [], "tags": [], "related": []}
        raw = f"```\n{json.dumps(payload)}\n```"
        state = _run_with_response(raw)
        assert state["delta_proposal"]["label"] == "Graph"

    def test_unicode_label_preserved(self):
        """Non-ASCII characters in labels survive the round-trip."""
        payload = {"label": "Réseaux de neurones", "comment": "Neural networks in French.", "aliases": [], "tags": [], "related": []}
        state = _run_with_response(json.dumps(payload))
        assert state["delta_proposal"]["label"] == "Réseaux de neurones"

    def test_extra_fields_ignored(self):
        """Unknown fields in the LLM response are silently discarded."""
        payload = {
            "label": "Ontology",
            "comment": "A formal representation.",
            "aliases": [],
            "tags": ["ontology"],
            "related": [],
            "_reasoning": "I chose this label because…",
            "_confidence": 0.95,
        }
        state = _run_with_response(json.dumps(payload))
        proposal = state["delta_proposal"]
        assert proposal["label"] == "Ontology"
        assert "_reasoning" not in proposal
        assert "_confidence" not in proposal

    def test_tags_are_lowercased(self):
        """Tags in mixed case are normalised to lowercase."""
        payload = {"label": "Concept", "comment": "", "aliases": [], "tags": ["AI", "Knowledge-Graph", "LLM"], "related": []}
        state = _run_with_response(json.dumps(payload))
        assert state["delta_proposal"]["tags"] == ["ai", "knowledge-graph", "llm"]

    def test_related_as_list_of_strings(self):
        """When related is a list of plain strings each becomes a relatedTerm entry."""
        payload = {"label": "Graph", "comment": "", "aliases": [], "tags": [], "related": ["ontology", "node"]}
        state = _run_with_response(json.dumps(payload))
        ids = {r["id"] for r in state["delta_proposal"]["related"]}
        assert "assertion/ontology" in ids
        assert "assertion/node" in ids
        assert all(r["rel"] == "relatedTerm" for r in state["delta_proposal"]["related"])

    def test_related_rel_field_preserved(self):
        """The rel field on related items is preserved when present."""
        payload = {
            "label": "Component",
            "comment": "",
            "aliases": [],
            "tags": [],
            "related": [{"id": "system", "rel": "partOf"}, {"id": "interface", "rel": "uses"}],
        }
        state = _run_with_response(json.dumps(payload))
        rels = {r["id"]: r["rel"] for r in state["delta_proposal"]["related"]}
        assert rels["assertion/system"] == "partOf"
        assert rels["assertion/interface"] == "uses"

    def test_leading_trailing_whitespace_stripped(self):
        """Whitespace surrounding the JSON payload does not cause a parse failure."""
        payload = {"label": "Edge", "comment": "A connection.", "aliases": [], "tags": [], "related": []}
        raw = "\n\n  " + json.dumps(payload) + "  \n\n"
        state = _run_with_response(raw)
        assert state["delta_proposal"]["label"] == "Edge"


# ---------------------------------------------------------------------------
# Fallback behaviour when LLM returns unusable output
# ---------------------------------------------------------------------------

class TestFallback:
    def test_non_json_response_falls_back_to_title(self):
        """A plain-text response falls back to front_matter.title for label."""
        state = _run_with_response("Sorry, I cannot help with that.", title="My Concept")
        assert state["delta_proposal"]["label"] == "My Concept"

    def test_empty_string_response_falls_back_to_title(self):
        """An empty response string falls back to front_matter.title."""
        state = _run_with_response("", title="Fallback Title")
        assert state["delta_proposal"]["label"] == "Fallback Title"

    def test_truncated_json_falls_back(self):
        """Truncated (malformed) JSON falls back gracefully."""
        state = _run_with_response('{"label": "Incomplete', title="Safe Title")
        assert state["delta_proposal"]["label"] == "Safe Title"

    def test_missing_label_falls_back_to_front_matter(self):
        """Valid JSON without a 'label' key uses front_matter.title."""
        payload = {"comment": "A concept.", "aliases": [], "tags": ["test"], "related": []}
        state = _run_with_response(json.dumps(payload), title="Front Matter Title")
        assert state["delta_proposal"]["label"] == "Front Matter Title"

    def test_null_label_falls_back_to_front_matter(self):
        """A null label in JSON is treated as absent and falls back."""
        payload = {"label": None, "comment": "", "aliases": [], "tags": [], "related": []}
        state = _run_with_response(json.dumps(payload), title="Null Fallback")
        assert state["delta_proposal"]["label"] == "Null Fallback"

    def test_missing_tags_yields_empty_list(self):
        """A response without 'tags' produces an empty tags list (no crash)."""
        payload = {"label": "Concept", "comment": "A concept.", "aliases": []}
        state = _run_with_response(json.dumps(payload))
        assert state["delta_proposal"]["tags"] == []

    def test_missing_related_yields_empty_list(self):
        """A response without 'related' produces an empty related list."""
        payload = {"label": "Concept", "comment": "", "aliases": [], "tags": []}
        state = _run_with_response(json.dumps(payload))
        assert state["delta_proposal"]["related"] == []

    def test_related_item_without_id_is_skipped(self):
        """A related dict entry that lacks an 'id' key is silently dropped."""
        payload = {
            "label": "Concept",
            "comment": "",
            "aliases": [],
            "tags": [],
            "related": [{"rel": "relatedTerm"}, {"id": "ontology", "rel": "relatedTerm"}],
        }
        state = _run_with_response(json.dumps(payload))
        assert len(state["delta_proposal"]["related"]) == 1
        assert state["delta_proposal"]["related"][0]["id"] == "assertion/ontology"
