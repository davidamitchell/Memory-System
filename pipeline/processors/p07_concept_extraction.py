"""Processor 7 — Concept Extraction Processor.

Supports two extraction strategies selected via ``state["strategy"]``:

``rule-based``
    Reads structured YAML front-matter fields directly.  Near-perfect on
    the glossary corpus; produces sparse results on unstructured prose docs.
    Use explicitly via ``state["strategy"] = "rule-based"`` or the
    ``--strategy rule-based`` CLI flag when evaluating against the structured
    corpus.

    Extraction sources:
      - ``rdfs:label``     ← front_matter.title (or H1 fallback from p02)
      - ``rdfs:comment``   ← bold_definition (from p02)
      - ``ms:aliases``     ← front_matter.aliases
      - ``ms:hasTag``      ← front_matter.tags
      - ``ms:relatedTerm`` ← front_matter.related[].file (slug-based)

``llm``
    Sends the document body to GitHub Models via the ``gh models run``
    CLI and parses the JSON response into the same ``delta_proposal``
    shape.  Requires the ``gh`` CLI to be installed and authenticated
    (``gh auth login``).  The model defaults to ``gpt-4o-mini`` and can
    be overridden with the ``GH_MODEL`` environment variable.  Falls
    back gracefully to front-matter fields when the LLM response is
    missing a field.

    The ``_gh_models_caller`` module-level callable can be replaced in
    tests to inject a mock without invoking the real CLI.
"""
from __future__ import annotations

import json as _json
import logging
import os
import re
import subprocess as _subprocess
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

PROCESSOR_VERSION = "concept-extractor-v1.2.0"

# Maximum number of NLP annotation items (entities, noun chunks) included in
# the LLM prompt.  Keeps prompt size bounded while providing useful signal.
_MAX_NLP_ITEMS_IN_PROMPT = 20

# ---------------------------------------------------------------------------
# gh models caller — swappable for testing
# ---------------------------------------------------------------------------

_GH_MODEL_DEFAULT = "gpt-4o-mini"


def _call_gh_models(model: str, system_prompt: str, user_prompt: str) -> str:
    """Invoke ``gh models run`` and return the response text.

    The user prompt is supplied via stdin to avoid command-line length
    limits on large documents.  ``check=True`` ensures subprocess errors
    propagate immediately rather than being silently swallowed.
    """
    result = _subprocess.run(
        ["gh", "models", "run", model, "--system-prompt", system_prompt],
        input=user_prompt,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


# This is the single seam tests replace.  Production code calls it;
# tests assign a mock before running (or use monkeypatch).
_gh_models_caller = _call_gh_models


_LLM_SYSTEM_PROMPT = """\
You are a concept extractor for a knowledge graph pipeline.
Given a research document, extract the following fields and return them as JSON:

{
  "label":   "<primary concept name>",
  "comment": "<one-sentence definition or summary, max 200 chars>",
  "aliases": ["<alternative name>", ...],
  "tags":    ["<lowercase keyword>", ...],
  "related": [{"id": "<slug>", "rel": "<relatedTerm|uses|partOf|contrasts|implements|instanceOf>"}, ...]
}

Rules:
- label: the single most precise concept name for this document
- comment: a concise definition extracted or synthesised from the text
- aliases: other names or abbreviations the concept is known by
- tags: 3–8 lowercase single-word or hyphenated keywords
- related: other concept slugs mentioned or implied; use the document filename stems of any referenced documents as slugs
- Respond with valid JSON only — no prose, no markdown fences.
"""


def _format_nlp_annotations(annotations: dict) -> str:
    """Render nlp_annotations as a compact, prompt-friendly string."""
    lines = []
    entities = annotations.get("entities", [])
    if entities:
        ent_strs = [f"{e['text']} ({e['label']})" for e in entities[:_MAX_NLP_ITEMS_IN_PROMPT]]
        lines.append("Named entities: " + ", ".join(ent_strs))
    chunks = annotations.get("noun_chunks", [])
    if chunks:
        chunk_strs = [c["text"] for c in chunks[:_MAX_NLP_ITEMS_IN_PROMPT]]
        lines.append("Key noun phrases: " + ", ".join(chunk_strs))
    return "\n".join(lines)


def _extract_llm(state: dict, source_slug: str, segments: list[dict]) -> dict:
    """Call the LLM and return a delta_proposal dict."""
    fm = state.get("front_matter", {})
    body = state.get("body_text", "")[:6000]  # cap to avoid token overflow

    # Seed the prompt with any structured front-matter already available
    seed_info = ""
    if fm.get("title"):
        seed_info += f"Document title: {fm['title']}\n"
    if fm.get("themes"):
        seed_info += f"Themes: {', '.join(fm['themes'])}\n"

    # Append NLP annotations when available (W-0205)
    nlp_section = ""
    annotations = state.get("nlp_annotations")
    if annotations:
        formatted = _format_nlp_annotations(annotations)
        if formatted:
            nlp_section = f"\n\nNLP pre-analysis:\n{formatted}\n"

    user_prompt = f"{seed_info}\n---\n{body}{nlp_section}"

    model = os.environ.get("GH_MODEL", _GH_MODEL_DEFAULT)
    raw = _gh_models_caller(model, _LLM_SYSTEM_PROMPT, user_prompt) or "{}"
    # Strip optional markdown fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw)

    try:
        extracted = _json.loads(raw)
    except _json.JSONDecodeError:
        logger.warning("LLM returned non-JSON for %s; using front-matter fallback", source_slug)
        extracted = {}

    label = str(extracted.get("label") or fm.get("title") or source_slug.replace("-", " ").title())
    comment = str(extracted.get("comment") or state.get("bold_definition", ""))
    aliases = list(extracted.get("aliases") or [])
    tags = [str(t).lower() for t in (extracted.get("tags") or [])]
    related_raw = extracted.get("related") or []
    related: list[dict] = []
    for r in related_raw:
        if isinstance(r, dict):
            rid = _slug(str(r.get("id", "")))
            rel = str(r.get("rel", "relatedTerm"))
            if rid:
                related.append({"id": f"assertion/{rid}", "rel": rel})
        elif isinstance(r, str):
            rid = _slug(r)
            if rid:
                related.append({"id": f"assertion/{rid}", "rel": "relatedTerm"})

    return {
        "assertion_id": f"assertion/{source_slug}",
        "label": label,
        "comment": comment,
        "aliases": aliases,
        "tags": tags,
        "related": related,
        "primary_segment_hash": segments[0]["hash"] if segments else "",
        "all_segment_hashes": [s["hash"] for s in segments],
    }


# ---------------------------------------------------------------------------
# Rule-based extraction (original implementation)
# ---------------------------------------------------------------------------

def _slug(filename: str) -> str:
    """Convert a filename (with or without .md) to a URI-safe slug."""
    return re.sub(r"\.md$", "", filename.lower().strip())


def _extract_rule_based(state: dict, source_slug: str, segments: list[dict]) -> dict:
    """Extract from structured YAML front-matter."""
    fm = state["front_matter"]

    related_assertions = [
        {
            "id": f"assertion/{_slug(r['file'])}",
            "rel": r.get("rel", "relatedTerm"),
        }
        for r in fm.get("related", [])
        if isinstance(r, dict)
    ]

    label = fm.get("title", "") or source_slug.replace("-", " ").title()

    return {
        "assertion_id": f"assertion/{source_slug}",
        "label": label,
        "comment": state.get("bold_definition", ""),
        "aliases": fm.get("aliases", []),
        "tags": fm.get("tags", []),
        "related": related_assertions,
        "primary_segment_hash": segments[0]["hash"] if segments else "",
        "all_segment_hashes": [s["hash"] for s in segments],
    }


# ---------------------------------------------------------------------------
# Processor entry point
# ---------------------------------------------------------------------------

def run(state: dict, repo_root: Path) -> dict:  # noqa: ARG001
    """Extract concept assertions and record the Extraction Activity.

    Reads ``state["strategy"]`` (default ``"llm"``) to select the
    extraction strategy.

    Adds to state:
    - ``delta_proposal``: dict describing the candidate assertions
    - ``extraction_activity``: dict recording this extraction run
    """
    strategy = state.get("strategy", "llm")
    logger.info("[7/12] Concept Extraction Processor — strategy=%s", strategy)

    segments: list[dict] = state["segments"]
    source_slug = _slug(Path(state["source_path"]).name)

    if strategy == "llm":
        delta_proposal = _extract_llm(state, source_slug, segments)
    else:
        delta_proposal = _extract_rule_based(state, source_slug, segments)

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    safe_ts = re.sub(r"[:\-]", "", timestamp).rstrip("Z")
    activity_id = f"activity/extract-{safe_ts}"

    extraction_activity = {
        "activity_id": activity_id,
        "processor_version": PROCESSOR_VERSION,
        "timestamp": timestamp,
        "strategy": strategy,
        "used_segments": delta_proposal["all_segment_hashes"],
        "source_path": state["source_path"],
    }

    logger.info("  assertion: %s", delta_proposal["assertion_id"])
    logger.info(
        "  extracted: label=%r  aliases=%d  tags=%d  related=%d  segments=%d",
        delta_proposal["label"],
        len(delta_proposal["aliases"]),
        len(delta_proposal["tags"]),
        len(delta_proposal["related"]),
        len(segments),
    )

    return {**state, "delta_proposal": delta_proposal, "extraction_activity": extraction_activity}

