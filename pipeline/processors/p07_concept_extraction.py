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

Error handling in _call_gh_models
----------------------------------
Three failure modes are distinguished so callers can react appropriately:

  GhModelsRateLimitError   — HTTP 429 / rate-limit message in stderr.
                             The caller should wait the instructed time and
                             retry once; it must NOT use exponential backoff
                             for this class of error.

  GhModelsUnavailableError — Transient failure (5xx, network glitch, timeout).
                             Safe to retry with exponential backoff.

  CalledProcessError       — Any other non-zero exit (bad model name, auth
                             failure, etc.).  Propagates immediately; retrying
                             would not help.

Proactive pacing
-----------------
``_GhModelsPacer`` enforces a minimum inter-call interval derived from the
model's known RPM limit so the process stays comfortably inside the free-tier
window instead of hammering the API until it gets a 429.
"""
from __future__ import annotations

import json as _json
import logging
import os
import re
import subprocess as _subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

PROCESSOR_VERSION = "concept-extractor-v1.3.0"

# Maximum number of NLP annotation items (entities, noun chunks) included in
# the LLM prompt.  Keeps prompt size bounded while providing useful signal.
_MAX_NLP_ITEMS_IN_PROMPT = 20

# ---------------------------------------------------------------------------
# Error sentinels — distinct types so callers handle each case correctly
# ---------------------------------------------------------------------------


class GhModelsRateLimitError(Exception):
    """Raised when ``gh models run`` is rejected with a rate-limit (429) response.

    Retrying immediately or with exponential backoff is wrong — the server has
    told us to wait.  The caller should honour ``retry_after`` (seconds) then
    try once more.  If the retry also hits a rate limit, give up for this item.
    """

    def __init__(self, message: str, retry_after: float = 10.0) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class GhModelsUnavailableError(Exception):
    """Raised when ``gh models run`` fails with a transient server error (5xx).

    Safe to retry with exponential backoff.
    """


# ---------------------------------------------------------------------------
# Rate-limit and transient-error detection from gh CLI stderr
# ---------------------------------------------------------------------------

# Patterns that indicate a rate-limit (429) response from gh models.
_RATE_LIMIT_PATTERNS = re.compile(
    r"rate.?limit|429|too many requests|quota exceeded|requests per minute",
    re.IGNORECASE,
)

# Patterns that indicate a transient server-side failure worth retrying.
_TRANSIENT_PATTERNS = re.compile(
    r"5\d\d|server error|service unavailable|internal error|connection|timeout",
    re.IGNORECASE,
)

# Pattern to extract a suggested wait time (e.g. "retry after 30s", "wait 60 seconds").
_RETRY_AFTER_PATTERN = re.compile(r"(?:retry.after|wait)\D*(\d+)\s*s", re.IGNORECASE)

_SUBPROCESS_TIMEOUT = 120  # seconds — generous for large prompts, prevents hangs


def _parse_retry_after(text: str, default: float = 10.0) -> float:
    """Extract a retry-after value in seconds from an error message."""
    match = _RETRY_AFTER_PATTERN.search(text)
    if match:
        return max(float(match.group(1)), 1.0)
    return default


def _classify_gh_error(stderr: str, returncode: int) -> str:
    """Return 'rate_limit', 'transient', or 'fatal' based on stderr content."""
    if _RATE_LIMIT_PATTERNS.search(stderr):
        return "rate_limit"
    if returncode >= 500 or _TRANSIENT_PATTERNS.search(stderr):
        return "transient"
    return "fatal"


# ---------------------------------------------------------------------------
# Proactive inter-call pacer
# ---------------------------------------------------------------------------

# Default RPM for GitHub Models free tier (conservative — avoids blind 429s).
_DEFAULT_RPM = 10


class _GhModelsPacer:
    """Enforces a minimum gap between consecutive ``gh models run`` calls.

    Uses ``60 / rpm`` seconds as the floor so the pipeline stays inside the
    free-tier window rather than hitting the limit reactively.  Instantiate
    once per pipeline run and call ``wait()`` before each LLM call.
    """

    def __init__(self, rpm: int = _DEFAULT_RPM) -> None:
        self._interval = 60.0 / max(rpm, 1)
        self._last: float = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        gap = self._interval - (now - self._last)
        if gap > 0:
            logger.debug("GhModelsPacer: waiting %.1fs before next gh models call", gap)
            time.sleep(gap)
        self._last = time.monotonic()


# Module-level pacer shared across calls within a single pipeline run.
# Tests can replace this with a no-op instance.
_pacer = _GhModelsPacer()


# ---------------------------------------------------------------------------
# gh models caller — swappable for testing
# ---------------------------------------------------------------------------

_GH_MODEL_DEFAULT = "gpt-4o-mini"


def _call_gh_models(model: str, system_prompt: str, user_prompt: str) -> str:
    """Invoke ``gh models run`` and return the response text.

    The user prompt is supplied via stdin to avoid command-line length limits
    on large documents.

    Raises:
        GhModelsRateLimitError:    server returned 429 / rate-limit message.
        GhModelsUnavailableError:  transient server error — safe to retry.
        subprocess.CalledProcessError: any other non-zero exit (auth, bad model, …).
        subprocess.TimeoutExpired: call took longer than _SUBPROCESS_TIMEOUT seconds.
    """
    try:
        result = _subprocess.run(
            ["gh", "models", "run", model, "--system-prompt", system_prompt],
            input=user_prompt,
            capture_output=True,
            text=True,
            timeout=_SUBPROCESS_TIMEOUT,
        )
    except _subprocess.TimeoutExpired:
        raise GhModelsUnavailableError(
            f"gh models run timed out after {_SUBPROCESS_TIMEOUT}s"
        )

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        kind = _classify_gh_error(stderr, result.returncode)
        if kind == "rate_limit":
            wait = _parse_retry_after(stderr)
            logger.warning(
                "gh models: rate-limited (rc=%d) — suggested wait %.0fs. stderr: %s",
                result.returncode,
                wait,
                stderr[:200],
            )
            raise GhModelsRateLimitError(stderr, retry_after=wait)
        if kind == "transient":
            logger.warning(
                "gh models: transient error (rc=%d) — stderr: %s",
                result.returncode,
                stderr[:200],
            )
            raise GhModelsUnavailableError(stderr)
        # Fatal: auth failure, unknown model, etc. — log clearly and propagate.
        logger.error(
            "gh models: fatal error (rc=%d) — stderr: %s",
            result.returncode,
            stderr[:400],
        )
        result.check_returncode()  # raises CalledProcessError with full context

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

