"""Processor 3 — Segmentation Processor.

Splits the prepared body text into immutable, content-addressed
Prepared Segments (one paragraph = one segment).  Each segment is
identified by its SHA-256 content hash and written to
``data/segments/<hash>.txt``.

Sub-paragraph splitting is deferred (W-0200 assumption).
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Sections whose content we exclude from segmentation (link lists only)
_EXCLUDED_SECTION_RE = re.compile(
    r"^## (?:Related Terms|References)\s*$", re.MULTILINE
)


def _extract_body_paragraphs(body_text: str) -> list[str]:
    """Return meaningful body paragraphs, excluding link-list sections.

    Strips markdown section headers (## …) and skips empty strings.
    Paragraphs are separated by one or more blank lines.
    """
    # Truncate at the first excluded section
    trunc_match = _EXCLUDED_SECTION_RE.search(body_text)
    if trunc_match:
        body_text = body_text[: trunc_match.start()]

    paragraphs = []
    for block in re.split(r"\n{2,}", body_text):
        # Strip markdown headers and leading/trailing whitespace
        block = re.sub(r"^\s*#{1,6}[^\n]*\n?", "", block, flags=re.MULTILINE)
        block = block.strip()
        # Skip the bold one-liner (it's already stored as bold_definition)
        if block.startswith("**") and block.endswith("**"):
            continue
        if block:
            paragraphs.append(block)

    return paragraphs


def run(state: dict, repo_root: Path) -> dict:
    """Split body into content-addressed segments and write them to disk.

    Adds to state:
    - ``segments``: list of dicts with ``text`` and ``hash`` (SHA-256 hex)
    """
    logger.info("[3/12] Segmentation Processor — splitting body into segments")

    segments_dir = repo_root / "data" / "segments"
    segments_dir.mkdir(parents=True, exist_ok=True)

    paragraphs = _extract_body_paragraphs(state["body_text"])
    segments = []

    for para in paragraphs:
        sha = hashlib.sha256(para.encode("utf-8")).hexdigest()
        seg_file = segments_dir / f"{sha}.txt"
        seg_file.write_text(para, encoding="utf-8")
        segments.append({"text": para, "hash": sha})
        logger.debug("  segment %s… (%d chars)", sha[:12], len(para))

    logger.info("  %d segment(s) written", len(segments))
    return {**state, "segments": segments}
