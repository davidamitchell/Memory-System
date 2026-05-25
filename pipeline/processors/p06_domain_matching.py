"""Processor 6 — Domain Matching Processor.

Maps candidate domain signals to canonical upper-ontology domain nodes
in the ``ms:`` namespace.  Tie-break rule: first signal wins when
multiple signals are present.

Canonical domain map:
  Vocabulary                → ms:VocabularyDomain
  ArchitectureDecisionRecord → ms:ArchitectureDecisionRecordDomain
  Design                    → ms:DesignDomain
  ResearchDocument          → ms:ResearchDocumentDomain
  Project                   → ms:ProjectDomain
  Meeting                   → ms:MeetingDomain
  Journal                   → ms:JournalDomain
  General                   → ms:GeneralDomain
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_DOMAIN_URI_MAP = {
    "Vocabulary": "ms:VocabularyDomain",
    "ArchitectureDecisionRecord": "ms:ArchitectureDecisionRecordDomain",
    "Design": "ms:DesignDomain",
    "ResearchDocument": "ms:ResearchDocumentDomain",
    "Project": "ms:ProjectDomain",
    "Meeting": "ms:MeetingDomain",
    "Journal": "ms:JournalDomain",
    "General": "ms:GeneralDomain",
}


def run(state: dict, repo_root: Path) -> dict:  # noqa: ARG001
    """Map domain signals to a canonical upper-ontology domain URI.

    Adds to state:
    - ``domain``: canonical domain URI string (e.g. ``ms:VocabularyDomain``)
    - ``domain_tie_break_applied``: bool, True if >1 signal required tie-break
    """
    logger.info("[6/12] Domain Matching Processor — mapping to upper ontology")

    signals: list[str] = state["domain_signals"]
    tie_break_applied = len(signals) > 1

    # Tie-break: first signal wins
    primary_signal = signals[0]
    domain = _DOMAIN_URI_MAP.get(primary_signal, "ms:GeneralDomain")

    if tie_break_applied:
        logger.info(
            "  tie-break applied: %d signals → primary=%s → %s",
            len(signals),
            primary_signal,
            domain,
        )
    else:
        logger.info("  domain: %s → %s", primary_signal, domain)

    return {**state, "domain": domain, "domain_tie_break_applied": tie_break_applied}
