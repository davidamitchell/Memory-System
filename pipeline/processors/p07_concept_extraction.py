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
                             Detected by ``_is_rate_limited_response`` or
                             ``_is_quota_response`` helpers.  The caller
                             should wait the instructed time and retry once;
                             it must NOT use exponential backoff for this
                             class of error.

  GhModelsUnavailableError — Transient failure (5xx, network glitch, timeout).
                             Safe to retry with exponential backoff.

  CalledProcessError       — Any other non-zero exit (bad model name, auth
                             failure, etc.).  Propagates immediately; retrying
                             would not help.

``_extract_llm`` wraps ``_gh_models_caller`` with the full retry/degradation
logic: rate-limit → honour wait + one retry; transient → exponential backoff
with two retries; any other error or exhausted retries → degrade gracefully
to front-matter fields.

Proactive pacing
-----------------
``_GhModelsPacer`` enforces a minimum inter-call interval derived from the
model's known RPM limit so the process stays comfortably inside the free-tier
window instead of hammering the API until it gets a 429.  The pacer resets
its timer whenever the active model changes.
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

PROCESSOR_VERSION = "concept-extractor-v1.4.0"

# Maximum number of NLP annotation items (entities, noun chunks, lemmas) included in
# the LLM prompt.  Keeps prompt size bounded while providing useful signal.
_MAX_NLP_ITEMS_IN_PROMPT = 20

# POS tags considered content words for lemma extraction.  Closed-class words
# (determiners, prepositions, conjunctions, auxiliaries) are excluded because
# they add noise rather than signal for concept identification.
_CONTENT_POS = {"NOUN", "VERB", "PROPN", "ADJ"}

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
    r"rate.?limit|429|too many requests|requests per minute",
    re.IGNORECASE,
)

# Patterns that indicate a quota-exceeded response (separate from per-minute rate limits).
_QUOTA_PATTERNS = re.compile(
    r"quota.?exceeded|quota",
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


def _is_rate_limited_response(stderr: str) -> bool:
    """Return True when stderr indicates a rate-limit (429) response from gh models."""
    return bool(_RATE_LIMIT_PATTERNS.search(stderr))


def _is_quota_response(stderr: str) -> bool:
    """Return True when stderr indicates a quota-exceeded response from gh models."""
    return bool(_QUOTA_PATTERNS.search(stderr))


def _parse_retry_after(text: str, default: float = 10.0) -> float:
    """Extract a retry-after value in seconds from an error message."""
    match = _RETRY_AFTER_PATTERN.search(text)
    if match:
        return max(float(match.group(1)), 1.0)
    return default


def _classify_gh_error(stderr: str, returncode: int) -> str:
    """Return 'rate_limit', 'transient', or 'fatal' based on stderr content."""
    if _is_rate_limited_response(stderr) or _is_quota_response(stderr):
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
    once per pipeline run and call ``wait(model)`` before each LLM call.

    When ``model`` changes the last-call timer is reset so a fresh model
    gets its full inter-call window rather than inheriting the old model's
    remaining wait.
    """

    def __init__(self, rpm: int = _DEFAULT_RPM) -> None:
        self._interval = 60.0 / max(rpm, 1)
        self._last: float = 0.0
        self._current_model: str = ""

    def wait(self, model: str = "") -> None:
        if model and model != self._current_model:
            logger.debug(
                "GhModelsPacer: model changed to %r — resetting last-call timer", model
            )
            self._last = 0.0
            self._current_model = model
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
    _pacer.wait(model)
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
You are a knowledge-graph extractor for a personal research memory system.

Given a document, identify the single primary concept it is about and extract its typed \
relationships to other concepts.

Definitions (from the system glossary):
- concept: an abstract unit of meaning defined by necessary and sufficient membership \
conditions — not merely a topic or tag
- relationship: a typed, directed association between two concepts; expressed as \
(subject → predicate → object)
- domain: a bounded region of discourse in which terms have fixed, agreed meanings

Return only this JSON:
{
  "label":   "<primary concept name>",
  "comment": "<one-sentence definition or summary, max 200 chars>",
  "aliases": ["<synonym or abbreviation>", ...],
  "related": [{"id": "<target-concept-slug>", "rel": "<relatedTerm|uses|partOf|contrasts|implements|instanceOf>"}, ...]
}

Rules:
- label: the single most precise concept name this document is about
- comment: a definition synthesised from the text; prefer necessary/sufficient conditions \
where the document states them
- aliases: synonyms, abbreviations, or alternative names for this concept
- related: typed, directed relationships to other concepts; each id is the slug \
(lowercase-hyphenated) of the target concept; omit self-referential entries
- Themes (when provided) indicate the subject area — treat them as directional signals, \
not as constraints on what you extract
- Respond with valid JSON only — no prose, no markdown fences
"""


def _format_nlp_annotations(annotations: dict) -> str:
    """Render nlp_annotations as a compact, prompt-friendly string.

    Includes three sections when data is present:
    - Named entities (text + NER label)
    - Key noun phrases (noun chunk texts)
    - Key lemmas (deduped content-word lemmas from pos_tags: NOUN/VERB/PROPN/ADJ)
    """
    lines = []
    entities = annotations.get("entities", [])
    if entities:
        ent_strs = [f"{e['text']} ({e['label']})" for e in entities[:_MAX_NLP_ITEMS_IN_PROMPT]]
        lines.append("Named entities: " + ", ".join(ent_strs))
    chunks = annotations.get("noun_chunks", [])
    if chunks:
        chunk_strs = [c["text"] for c in chunks[:_MAX_NLP_ITEMS_IN_PROMPT]]
        lines.append("Key noun phrases: " + ", ".join(chunk_strs))
    pos_tags = annotations.get("pos_tags", [])
    if pos_tags:
        seen: set[str] = set()
        lemmas: list[str] = []
        for t in pos_tags:
            if t.get("pos") in _CONTENT_POS:
                lemma = t["lemma"].lower()
                if lemma not in seen and len(lemma) > 2:
                    seen.add(lemma)
                    lemmas.append(lemma)
        if lemmas:
            lines.append("Key lemmas: " + ", ".join(lemmas[:_MAX_NLP_ITEMS_IN_PROMPT]))
    return "\n".join(lines)


def _extract_llm(state: dict, source_slug: str, segments: list[dict]) -> dict:
    """Call the LLM and return a delta_proposal dict.

    Error handling:
    - ``GhModelsRateLimitError``: honour ``retry_after``, one respectful retry;
      degrade gracefully to front-matter if the retry also fails.
    - ``GhModelsUnavailableError``: retry with exponential backoff (up to two
      additional attempts); degrade gracefully if all retries are exhausted.
    - Any other exception: log and degrade immediately to front-matter fields.
    """
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

    raw: str | None = None
    try:
        raw = _gh_models_caller(model, _LLM_SYSTEM_PROMPT, user_prompt)
    except GhModelsRateLimitError as exc:
        logger.warning(
            "gh models: rate-limited for %s — waiting %.0fs then retrying once",
            source_slug,
            exc.retry_after,
        )
        time.sleep(exc.retry_after)
        try:
            raw = _gh_models_caller(model, _LLM_SYSTEM_PROMPT, user_prompt)
        except Exception as retry_exc:
            logger.warning(
                "gh models: rate-limit retry also failed for %s (%s) — degrading to front-matter",
                source_slug,
                retry_exc,
            )
    except GhModelsUnavailableError:
        _backoff_delays = (2.0, 4.0)
        for attempt, delay in enumerate(_backoff_delays, start=1):
            logger.info(
                "gh models: transient error for %s — backoff %.0fs (attempt %d/%d)",
                source_slug,
                delay,
                attempt,
                len(_backoff_delays),
            )
            time.sleep(delay)
            try:
                raw = _gh_models_caller(model, _LLM_SYSTEM_PROMPT, user_prompt)
                break
            except GhModelsUnavailableError:
                continue
            except Exception:
                break
        if raw is None:
            logger.warning(
                "gh models: all retries failed for %s — degrading to front-matter",
                source_slug,
            )
    except Exception as exc:
        logger.warning(
            "gh models: unexpected error for %s (%s) — degrading to front-matter",
            source_slug,
            exc,
        )

    # Strip optional markdown fences and parse JSON
    if raw:
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        raw = re.sub(r"\s*```$", "", raw)
    try:
        extracted = _json.loads(raw or "{}")
    except _json.JSONDecodeError:
        logger.warning("LLM returned non-JSON for %s; using front-matter fallback", source_slug)
        extracted = {}

    label = str(extracted.get("label") or fm.get("title") or source_slug.replace("-", " ").title())
    comment = str(extracted.get("comment") or state.get("bold_definition", ""))
    aliases = list(extracted.get("aliases") or [])
    # Tags are no longer extracted; extraction focuses on concepts and relationships.
    tags: list[str] = []
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

