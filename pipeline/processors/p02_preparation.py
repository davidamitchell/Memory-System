"""Processor 2 — Preparation Processor.

Parses YAML front matter and extracts the body text.  Strips markdown
section headers and produces the canonical cleaned representation used
by all downstream processors.

Front matter is optional.  Documents without a ``---`` block (e.g. ADRs
and design docs) are accepted: the H1 heading is used as the title fallback
and all structured fields (aliases, tags, related) default to empty.

Optional NLP enrichment (W-0205)
---------------------------------
When ``state["nlp"]`` is ``True`` the processor also runs the document
body through a spaCy pipeline and attaches structured annotations to
state under ``nlp_annotations``.  When ``state["nlp"]`` is ``False``
(the default) the output is identical to the pre-W-0205 state.

Requires ``spacy`` and the ``en_core_web_sm`` model:

    pip install "spacy>=3.7"
    python -m spacy download en_core_web_sm

The spaCy model is loaded lazily on the first enriched document and
cached for the remainder of the session.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
_BOLD_DEF_RE = re.compile(r"^\*\*(.+?)\*\*\s*$", re.MULTILINE)
_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)

# Limit text fed to spaCy to avoid excessive processing on very long documents.
# en_core_web_sm processes ~3 k tokens/s; 8 000 chars ≈ 1 500 tokens ≈ sub-second.
_MAX_NLP_TEXT_LENGTH = 8000

# ---------------------------------------------------------------------------
# spaCy model — loaded lazily and cached
# ---------------------------------------------------------------------------

_nlp_model: Any = None  # module-level cache; replaceable in tests


def _get_nlp_model():
    """Return (and lazily load) the spaCy English model."""
    global _nlp_model  # noqa: PLW0603
    if _nlp_model is not None:
        return _nlp_model
    try:
        import spacy  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "The 'spacy' package is required for NLP enrichment. "
            "Install it with: pip install 'spacy>=3.7' && python -m spacy download en_core_web_sm"
        ) from exc
    try:
        _nlp_model = spacy.load("en_core_web_sm")
    except OSError as exc:
        raise OSError(
            "spaCy model 'en_core_web_sm' not found. "
            "Download it with: python -m spacy download en_core_web_sm"
        ) from exc
    return _nlp_model


def _enrich_with_nlp(text: str) -> dict:
    """Run spaCy on *text* and return structured annotations.

    Returns a dict with three keys:

    ``entities``
        List of ``{"text": str, "label": str, "start": int, "end": int}``
        dicts for each named entity span.

    ``noun_chunks``
        List of ``{"text": str, "root": str}`` dicts for each noun chunk.

    ``pos_tags``
        List of ``{"text": str, "pos": str, "lemma": str}`` dicts for each
        token that is not punctuation or whitespace.
    """
    # Cap to avoid excessive processing on very long documents
    capped = text[:_MAX_NLP_TEXT_LENGTH]
    nlp = _get_nlp_model()
    doc = nlp(capped)

    entities = [
        {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
        for ent in doc.ents
    ]
    noun_chunks = [
        {"text": chunk.text, "root": chunk.root.text}
        for chunk in doc.noun_chunks
    ]
    pos_tags = [
        {"text": token.text, "pos": token.pos_, "lemma": token.lemma_}
        for token in doc
        if token.pos_ not in ("PUNCT", "SPACE")
    ]

    return {"entities": entities, "noun_chunks": noun_chunks, "pos_tags": pos_tags}


# ---------------------------------------------------------------------------
# Processor entry point
# ---------------------------------------------------------------------------

def run(state: dict, repo_root: Path) -> dict:  # noqa: ARG001
    """Parse YAML front matter, extract body text, and optionally enrich with NLP.

    Adds to state:
    - ``front_matter``: dict of parsed YAML fields (empty dict if absent)
    - ``bold_definition``: text of the bold one-liner (stripped of **)
    - ``body_text``: full body text after the front matter block (or full
      content when there is no front matter block)
    - ``nlp_annotations``: dict of NLP annotations (only when
      ``state["nlp"]`` is ``True``; absent otherwise)
    """
    nlp_enabled = state.get("nlp", False)
    logger.info("[2/12] Preparation Processor — parsing front matter and body%s",
                " (NLP enrichment enabled)" if nlp_enabled else "")

    raw = state["raw_content"]

    m = _FRONT_MATTER_RE.match(raw)
    if m:
        front_matter: dict[str, Any] = yaml.safe_load(m.group(1)) or {}
        body_text = raw[m.end():]
    else:
        # No YAML front matter — accept the document and derive title from H1
        front_matter = {}
        body_text = raw
        h1_match = _H1_RE.search(raw)
        if h1_match:
            front_matter["title"] = h1_match.group(1).strip()
            logger.debug("  no front matter; H1 title: %r", front_matter["title"])
        else:
            logger.debug("  no front matter and no H1 heading in %s", state["source_path"])

    # Find the bold one-liner definition (first ** ... ** paragraph)
    bold_match = _BOLD_DEF_RE.search(body_text)
    bold_definition = bold_match.group(1).strip() if bold_match else ""

    logger.debug(
        "  title=%r  tags=%s  related=%d  aliases=%d",
        front_matter.get("title"),
        front_matter.get("tags", []),
        len(front_matter.get("related", [])),
        len(front_matter.get("aliases", [])),
    )
    logger.debug("  bold definition: %r", bold_definition[:80])

    result = {
        **state,
        "front_matter": front_matter,
        "bold_definition": bold_definition,
        "body_text": body_text,
    }

    if nlp_enabled:
        annotations = _enrich_with_nlp(body_text)
        logger.debug(
            "  NLP: %d entities  %d noun_chunks  %d pos_tags",
            len(annotations["entities"]),
            len(annotations["noun_chunks"]),
            len(annotations["pos_tags"]),
        )
        result["nlp_annotations"] = annotations

    return result
