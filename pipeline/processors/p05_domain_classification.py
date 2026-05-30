"""Processor 5 — Domain Classification Processor.

Produces candidate domain labels from content analysis using a rule-based
approach.  ML/LLM classification is deferred (W-0200 assumption).

Rule table:
  - ``foundational_concepts/`` path prefix → ``FoundationalConcept``
  - ``_docs/adr/`` path prefix             → ``ArchitectureDecisionRecord``
  - ``_docs/design/`` path prefix         → ``Design``
  - ``raw_document_corpus/`` path prefix  → ``ResearchDocument``
  - ``projects/`` path prefix             → ``Project``
  - ``meetings/`` path prefix             → ``Meeting``
  - ``journal/`` path prefix              → ``Journal``
  - Default                               → ``General``
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_PATH_DOMAIN_MAP = {
    "foundational_concepts/": "FoundationalConcept",
    "_docs/adr/": "ArchitectureDecisionRecord",
    "_docs/design/": "Design",
    "raw_document_corpus/": "ResearchDocument",
    "projects/": "Project",
    "meetings/": "Meeting",
    "journal/": "Journal",
}


def run(state: dict, repo_root: Path) -> dict:  # noqa: ARG001
    """Classify the document into one or more domain signals.

    Adds to state:
    - ``domain_signals``: list of candidate domain label strings
    """
    logger.info("[5/12] Domain Classification Processor — classifying domain")

    source_path: str = state["source_path"]
    signals: list[str] = []

    for prefix, domain in _PATH_DOMAIN_MAP.items():
        if source_path.startswith(prefix):
            signals.append(domain)

    if not signals:
        signals.append("General")

    logger.info("  domain signal(s): %s (path=%s)", signals, source_path)
    return {**state, "domain_signals": signals}
