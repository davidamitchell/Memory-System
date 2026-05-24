"""Processor 7 — Concept Extraction Processor.

Supports two extraction strategies selected via ``state["strategy"]``:

``rule-based`` (default)
    Reads structured YAML front-matter fields directly.  Near-perfect on
    the glossary corpus; produces sparse results on unstructured prose docs.

    Extraction sources:
      - ``rdfs:label``     ← front_matter.title (or H1 fallback from p02)
      - ``rdfs:comment``   ← bold_definition (from p02)
      - ``ms:aliases``     ← front_matter.aliases
      - ``ms:hasTag``      ← front_matter.tags
      - ``ms:relatedTerm`` ← front_matter.related[].file (slug-based)

``llm``
    Sends the document body to an OpenAI-compatible chat endpoint and
    parses the JSON response into the same ``delta_proposal`` shape.
    Requires the ``OPENAI_API_KEY`` environment variable (and optionally
    ``OPENAI_BASE_URL`` and ``OPENAI_MODEL``).  Falls back gracefully
    to front-matter fields when the LLM response is missing a field.

    The ``_llm_client`` module-level variable can be replaced in tests
    to inject a mock without touching the real API.
"""
from __future__ import annotations

import json as _json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PROCESSOR_VERSION = "concept-extractor-v1.1.0"

# ---------------------------------------------------------------------------
# LLM client — swappable for testing
# ---------------------------------------------------------------------------

# This is the single seam tests replace.  Production code calls it;
# tests assign a mock before importing (or use monkeypatch).
_llm_client: Any = None  # set lazily on first llm call


def _get_llm_client():
    """Return (and lazily initialise) the OpenAI client."""
    global _llm_client  # noqa: PLW0603
    if _llm_client is not None:
        return _llm_client
    try:
        import openai  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "The 'openai' package is required for the llm extraction strategy. "
            "Install it with: pip install openai"
        ) from exc

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is not set. "
            "Set it to use the llm extraction strategy."
        )
    base_url = os.environ.get("OPENAI_BASE_URL")
    _llm_client = openai.OpenAI(api_key=api_key, **({"base_url": base_url} if base_url else {}))
    return _llm_client


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

    user_prompt = f"{seed_info}\n---\n{body}"

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    client = _get_llm_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _LLM_SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0,
    )

    raw = response.choices[0].message.content or "{}"
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

    Reads ``state["strategy"]`` (default ``"rule-based"``) to select the
    extraction strategy.

    Adds to state:
    - ``delta_proposal``: dict describing the candidate assertions
    - ``extraction_activity``: dict recording this extraction run
    """
    strategy = state.get("strategy", "rule-based")
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

