"""Processor 8 — Ontology Build Processor.

Constructs or updates the RDF graph from the delta proposal produced
by Processor 7.  Uses the ``ms:`` namespace and PROV-O for provenance
triples as specified in ADR-0004.

Namespace:
  ms:   <https://memory.example.org/ms/>
  prov: <http://www.w3.org/ns/prov#>
  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  xsd:  <http://www.w3.org/2001/XMLSchema#>
"""
from __future__ import annotations

import logging
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef, XSD
from rdflib.namespace import PROV

logger = logging.getLogger(__name__)

MS = Namespace("https://memory.example.org/ms/")


def _ms(local: str) -> URIRef:
    """Return a URIRef in the ms: namespace, supporting path-like locals."""
    return URIRef(f"https://memory.example.org/ms/{local}")


def run(state: dict, repo_root: Path) -> dict:  # noqa: ARG001
    """Build the RDF graph from the delta proposal.

    When ``state["graph"]`` already exists (batch mode, accumulating across
    multiple documents), new triples are merged into it.  When no graph is
    present a fresh one is created.

    Adds/updates in state:
    - ``graph``: rdflib.Graph containing all triples built so far
    """
    logger.info("[8/12] Ontology Build Processor — constructing RDF graph")

    dp = state["delta_proposal"]
    ea = state["extraction_activity"]

    # Accumulate into existing graph (batch mode) or start fresh (single-file mode)
    g: Graph = state.get("graph")
    if g is None:
        g = Graph()
        g.bind("ms", MS)
        g.bind("prov", PROV)
        g.bind("rdfs", RDFS)
        g.bind("xsd", XSD)
    else:
        logger.debug("  extending existing graph (%d triples)", len(g))

    # --- Assertion Node ---
    node = _ms(dp["assertion_id"])
    g.add((node, RDF.type, _ms("AssertionNode")))
    g.add((node, RDFS.label, Literal(dp["label"])))
    if dp["comment"]:
        g.add((node, RDFS.comment, Literal(dp["comment"])))

    for alias in dp["aliases"]:
        g.add((node, _ms("aliases"), Literal(alias)))

    for rel_item in dp["related"]:
        if isinstance(rel_item, dict):
            rel_id = rel_item["id"]
            rel_pred = rel_item.get("rel", "relatedTerm")
        else:
            rel_id = rel_item
            rel_pred = "relatedTerm"
        g.add((node, _ms(rel_pred), _ms(rel_id)))

    # Domain assignment
    if state.get("domain"):
        # Strip ms: prefix if present for URI construction
        domain_local = state["domain"].replace("ms:", "")
        g.add((node, _ms("inDomain"), _ms(domain_local)))

    # --- Extraction Activity ---
    activity = _ms(ea["activity_id"])
    g.add((activity, RDF.type, _ms("ExtractionActivity")))
    g.add((activity, PROV.wasAssociatedWith, _ms(f"processor/{ea['processor_version']}")))
    g.add((
        activity,
        PROV.endedAtTime,
        Literal(ea["timestamp"], datatype=XSD.dateTime),
    ))

    # Link activity to each segment used
    for seg_hash in ea["used_segments"]:
        seg = _ms(f"segment/{seg_hash}")
        g.add((activity, PROV.used, seg))

    # Link assertion node to extraction activity
    g.add((node, PROV.wasGeneratedBy, activity))

    # --- Prepared Segments ---
    for segment in state["segments"]:
        seg = _ms(f"segment/{segment['hash']}")
        g.add((seg, RDF.type, _ms("PreparedSegment")))
        g.add((seg, _ms("contentHash"), Literal(f"sha256:{segment['hash']}")))
        g.add((seg, _ms("sourceDocument"), Literal(state["source_path"])))

    triple_count = len(g)
    logger.info("  graph: %d triple(s)", triple_count)

    return {**state, "graph": g}
