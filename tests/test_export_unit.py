"""tests/test_export_unit.py — Unit tests for pipeline/export_json.py and export_html.py.

Tests use small hand-crafted rdflib Graphs and data dicts rather than the live
ontology, so they run without any file I/O or pipeline execution.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef

from pipeline.export_json import export_ontology
from pipeline.export_html import (
    badge,
    h,
    render_concepts,
    render_documents,
    render_overview,
    render_page,
    render_relations,
    tag_badges,
)

MS = Namespace("https://memory.example.org/ms/")
PROV = Namespace("http://www.w3.org/ns/prov#")


# ---------------------------------------------------------------------------
# Helpers — build small in-memory graphs
# ---------------------------------------------------------------------------

def _build_minimal_graph() -> Graph:
    """Two AssertionNodes with one relatedTerm edge and one PreparedSegment."""
    g = Graph()
    g.bind("ms", MS)

    nodeA = MS["assertion/concept-a"]
    g.add((nodeA, RDF.type, MS.AssertionNode))
    g.add((nodeA, RDFS.label, Literal("Concept A")))
    g.add((nodeA, RDFS.comment, Literal("First test concept.")))
    g.add((nodeA, MS.aliases, Literal("alias-a")))
    g.add((nodeA, MS.hasTag, Literal("test")))
    g.add((nodeA, MS.hasTag, Literal("alpha")))
    g.add((nodeA, MS.inDomain, MS.TestDomain))
    g.add((nodeA, MS.relatedTerm, MS["assertion/concept-b"]))

    nodeB = MS["assertion/concept-b"]
    g.add((nodeB, RDF.type, MS.AssertionNode))
    g.add((nodeB, RDFS.label, Literal("Concept B")))
    g.add((nodeB, RDFS.comment, Literal("Second test concept.")))
    g.add((nodeB, MS.inDomain, MS.TestDomain))

    seg = MS["segment/abc123"]
    g.add((seg, RDF.type, MS.PreparedSegment))
    g.add((seg, MS.sourceDocument, Literal("test/concept-a.md")))

    return g


def _build_multi_domain_graph() -> Graph:
    """Three nodes across two domains for domain-distribution tests."""
    g = Graph()
    g.bind("ms", MS)

    for name, domain, label in [
        ("concept-x", "DomainX", "Concept X"),
        ("concept-y", "DomainX", "Concept Y"),
        ("concept-z", "DomainZ", "Concept Z"),
    ]:
        node = MS[f"assertion/{name}"]
        g.add((node, RDF.type, MS.AssertionNode))
        g.add((node, RDFS.label, Literal(label)))
        g.add((node, MS.inDomain, MS[domain]))

    return g


# ---------------------------------------------------------------------------
# export_ontology — concept list
# ---------------------------------------------------------------------------

class TestExportOntologyConceptList:
    def test_correct_concept_count(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        assert data["meta"]["counts"]["concepts"] == 2

    def test_concepts_sorted_by_label(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        labels = [c["label"] for c in data["concepts"]]
        assert labels == sorted(labels, key=str.lower)

    def test_concept_has_required_fields(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        for concept in data["concepts"]:
            for field in ("id", "label", "comment", "aliases", "tags", "domain", "related"):
                assert field in concept, f"Missing field '{field}' in concept {concept.get('id')}"

    def test_aliases_exported(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        concept_a = next(c for c in data["concepts"] if c["id"] == "concept-a")
        assert "alias-a" in concept_a["aliases"]

    def test_tags_exported(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        concept_a = next(c for c in data["concepts"] if c["id"] == "concept-a")
        assert sorted(concept_a["tags"]) == ["alpha", "test"]

    def test_domain_field_is_local_name(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        for concept in data["concepts"]:
            assert concept["domain"] == "TestDomain"


# ---------------------------------------------------------------------------
# export_ontology — relations
# ---------------------------------------------------------------------------

class TestExportOntologyRelations:
    def test_relation_count(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        assert data["meta"]["counts"]["relations"] == 1

    def test_relation_fields(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        rel = data["relations"][0]
        assert rel["from_id"] == "concept-a"
        assert rel["to_id"] == "concept-b"
        assert rel["predicate"] == "relatedTerm"

    def test_concept_related_list_matches_relations(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        concept_a = next(c for c in data["concepts"] if c["id"] == "concept-a")
        assert len(concept_a["related"]) == 1
        assert concept_a["related"][0] == {"id": "concept-b", "rel": "relatedTerm"}

    def test_no_self_referential_artifacts(self):
        """concept-b has no outgoing relations; its related list should be empty."""
        data = export_ontology(_build_minimal_graph(), "v0001")
        concept_b = next(c for c in data["concepts"] if c["id"] == "concept-b")
        assert concept_b["related"] == []


# ---------------------------------------------------------------------------
# export_ontology — domain distribution
# ---------------------------------------------------------------------------

class TestExportOntologyDomainDistribution:
    def test_single_domain(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        dist = data["meta"]["domain_distribution"]
        assert len(dist) == 1
        assert dist[0]["domain"] == "TestDomain"
        assert dist[0]["count"] == 2

    def test_multi_domain_counts(self):
        data = export_ontology(_build_multi_domain_graph(), "v0002")
        dist = {d["domain"]: d["count"] for d in data["meta"]["domain_distribution"]}
        assert dist["DomainX"] == 2
        assert dist["DomainZ"] == 1

    def test_most_common_domain_first(self):
        data = export_ontology(_build_multi_domain_graph(), "v0002")
        counts = [d["count"] for d in data["meta"]["domain_distribution"]]
        assert counts == sorted(counts, reverse=True)


# ---------------------------------------------------------------------------
# export_ontology — meta block
# ---------------------------------------------------------------------------

class TestExportOntologyMeta:
    def test_version_label_preserved(self):
        data = export_ontology(_build_minimal_graph(), "v0099")
        assert data["meta"]["version"] == "v0099"

    def test_generated_timestamp_present(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        assert "generated" in data["meta"]
        assert data["meta"]["generated"]  # non-empty

    def test_counts_block_present(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        counts = data["meta"]["counts"]
        assert "concepts" in counts
        assert "relations" in counts
        assert "documents" in counts


# ---------------------------------------------------------------------------
# HTML helpers — h(), badge(), tag_badges()
# ---------------------------------------------------------------------------

class TestHtmlHelpers:
    def test_h_escapes_angle_brackets(self):
        assert "&lt;" in h("<script>")
        assert "&gt;" in h("<script>")

    def test_h_escapes_ampersand(self):
        assert "&amp;" in h("A & B")

    def test_h_escapes_quotes(self):
        assert "&#x27;" in h("it's") or "&apos;" in h("it's") or "'" not in h("it's")
        assert "&quot;" in h('"quoted"')

    def test_badge_contains_text(self):
        result = badge("ontology")
        assert "ontology" in result
        assert '<span' in result

    def test_tag_badges_multiple(self):
        result = tag_badges(["ai", "graph", "logic"])
        assert "ai" in result
        assert "graph" in result
        assert "logic" in result


# ---------------------------------------------------------------------------
# render_overview — section HTML
# ---------------------------------------------------------------------------

class TestRenderOverview:
    def _sample_data(self) -> dict:
        g = _build_minimal_graph()
        return export_ontology(g, "v0001")

    def test_renders_without_error(self):
        html = render_overview(self._sample_data())
        assert isinstance(html, str) and len(html) > 0

    def test_contains_concept_count(self):
        html = render_overview(self._sample_data())
        assert "2" in html  # 2 concepts

    def test_contains_domain_name(self):
        html = render_overview(self._sample_data())
        assert "TestDomain" in html


# ---------------------------------------------------------------------------
# render_concepts — concepts table
# ---------------------------------------------------------------------------

class TestRenderConcepts:
    def _sample_data(self) -> dict:
        return export_ontology(_build_minimal_graph(), "v0001")

    def test_renders_without_error(self):
        html = render_concepts(self._sample_data())
        assert isinstance(html, str) and len(html) > 0

    def test_contains_concept_labels(self):
        html = render_concepts(self._sample_data())
        assert "Concept A" in html
        assert "Concept B" in html

    def test_contains_tags(self):
        html = render_concepts(self._sample_data())
        assert "test" in html
        assert "alpha" in html

    def test_html_escapes_special_chars(self):
        """Labels with HTML-special characters are safely escaped."""
        g = Graph()
        g.bind("ms", MS)
        node = MS["assertion/xss-test"]
        g.add((node, RDF.type, MS.AssertionNode))
        g.add((node, RDFS.label, Literal("<script>alert(1)</script>")))
        g.add((node, MS.inDomain, MS.TestDomain))
        data = export_ontology(g, "v0001")
        html = render_concepts(data)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


# ---------------------------------------------------------------------------
# render_page — full page smoke test
# ---------------------------------------------------------------------------

class TestRenderPage:
    def test_renders_full_page(self):
        data = export_ontology(_build_minimal_graph(), "v0001")
        html = render_page(data)
        assert "<!DOCTYPE html>" in html or "<html" in html
        assert "Concept A" in html
        assert "Concept B" in html
