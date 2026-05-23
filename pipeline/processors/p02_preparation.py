"""Processor 2 — Preparation Processor.

Parses YAML front matter and extracts the body text.  Strips markdown
section headers and produces the canonical cleaned representation used
by all downstream processors.
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


def run(state: dict, repo_root: Path) -> dict:  # noqa: ARG001
    """Parse YAML front matter and extract body text.

    Adds to state:
    - ``front_matter``: dict of parsed YAML fields
    - ``bold_definition``: text of the bold one-liner (stripped of **)
    - ``body_text``: full body text after the front matter block
    """
    logger.info("[2/12] Preparation Processor — parsing front matter and body")

    raw = state["raw_content"]

    m = _FRONT_MATTER_RE.match(raw)
    if not m:
        raise ValueError(
            f"No YAML front matter found in {state['source_path']}"
        )

    front_matter: dict[str, Any] = yaml.safe_load(m.group(1)) or {}
    body_text = raw[m.end():]

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

    return {
        **state,
        "front_matter": front_matter,
        "bold_definition": bold_definition,
        "body_text": body_text,
    }
