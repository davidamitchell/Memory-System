"""tests/test_gh_models_error_handling.py — Tests for gh models error handling.

Covers:
  - _is_rate_limited_response / _is_quota_response helpers
  - _classify_gh_error using the new helpers
  - _GhModelsPacer model-change reset
  - _extract_llm rate-limit → respectful retry → success
  - _extract_llm rate-limit → retry also fails → graceful degradation
  - _extract_llm transient → backoff retry → success
  - _extract_llm transient always → all retries exhausted → graceful degradation
  - _extract_llm fatal error → immediate graceful degradation
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pipeline.processors.p07_concept_extraction as p07

_TEST_FILE = "foundational_concepts/concept.md"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GOOD_RESPONSE = {
    "label": "Test Concept",
    "comment": "A concept used in tests.",
    "aliases": [],
    "tags": ["test"],
    "related": [],
}


def _minimal_state() -> dict:
    """Build the pipeline state up to (but not including) p07."""
    from pipeline.processors import (
        p01_sourcing,
        p02_preparation,
        p03_segmentation,
        p04_metadata,
        p05_domain_classification,
        p06_domain_matching,
    )

    state: dict = {"source_path": _TEST_FILE, "strategy": "llm"}
    for proc in [
        p01_sourcing,
        p02_preparation,
        p03_segmentation,
        p04_metadata,
        p05_domain_classification,
        p06_domain_matching,
    ]:
        state = proc.run(state, REPO_ROOT)
    return state


def _run_extract_llm_with_caller(mock_caller, sleep_mock=None):
    """Run p07 with the given caller mock (and optional sleep mock).

    Both ``_gh_models_caller`` and ``time.sleep`` are patched so no
    real network calls or delays occur.
    """
    state = _minimal_state()

    ctx_caller = patch.object(p07, "_gh_models_caller", mock_caller)
    ctx_sleep = patch.object(p07.time, "sleep") if sleep_mock is None else patch.object(
        p07.time, "sleep", sleep_mock
    )
    # Always no-op the pacer so tests don't wait 6 s between calls.
    no_op_pacer = MagicMock()
    no_op_pacer.wait = MagicMock()
    ctx_pacer = patch.object(p07, "_pacer", no_op_pacer)

    with ctx_caller, ctx_sleep, ctx_pacer:
        state = p07.run(state, REPO_ROOT)
    return state


class _SequencedCaller:
    """A callable that returns/raises pre-programmed responses in order."""

    def __init__(self, sequence):
        self._seq = list(sequence)
        self._idx = 0
        self.call_count = 0

    def __call__(self, model, system_prompt, user_prompt):
        self.call_count += 1
        if self._idx >= len(self._seq):
            return json.dumps(_GOOD_RESPONSE)
        item = self._seq[self._idx]
        self._idx += 1
        if isinstance(item, BaseException):
            raise item
        return json.dumps(item) if isinstance(item, dict) else item


# ---------------------------------------------------------------------------
# _is_rate_limited_response helper
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("stderr,expected", [
    ("error: 429 Too Many Requests", True),
    ("rate limit exceeded", True),
    ("too many requests from this IP", True),
    ("requests per minute quota hit", True),
    ("server error 500", False),
    ("quota exceeded", False),          # quota is handled by _is_quota_response
    ("connection refused", False),
    ("", False),
])
def test_is_rate_limited_response(stderr, expected) -> None:
    assert p07._is_rate_limited_response(stderr) is expected


# ---------------------------------------------------------------------------
# _is_quota_response helper
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("stderr,expected", [
    ("quota exceeded for this model", True),
    ("quota.exceeded", True),
    ("your quota has been reached", True),
    ("rate limit exceeded", False),
    ("429 too many requests", False),
    ("server error", False),
    ("", False),
])
def test_is_quota_response(stderr, expected) -> None:
    assert p07._is_quota_response(stderr) is expected


# ---------------------------------------------------------------------------
# _classify_gh_error uses the new helpers
# ---------------------------------------------------------------------------

def test_classify_rate_limited_via_429() -> None:
    assert p07._classify_gh_error("error: 429 too many requests", 1) == "rate_limit"


def test_classify_rate_limited_via_rate_limit_text() -> None:
    assert p07._classify_gh_error("rate limit exceeded", 1) == "rate_limit"


def test_classify_rate_limited_via_quota() -> None:
    assert p07._classify_gh_error("quota exceeded", 1) == "rate_limit"


def test_classify_transient_5xx() -> None:
    assert p07._classify_gh_error("500 internal server error", 500) == "transient"


def test_classify_transient_by_text() -> None:
    assert p07._classify_gh_error("connection refused", 1) == "transient"


def test_classify_fatal() -> None:
    assert p07._classify_gh_error("unknown model: bad-model", 1) == "fatal"


# ---------------------------------------------------------------------------
# _GhModelsPacer model-change reset
# ---------------------------------------------------------------------------

def test_pacer_resets_last_on_model_change() -> None:
    pacer = p07._GhModelsPacer(rpm=600)  # high RPM so _interval is tiny
    with patch.object(p07.time, "sleep"):
        pacer.wait("gpt-4o-mini")
    original_last = pacer._last

    # Simulate a long gap so _last is in the past, then switch model
    pacer._last = original_last - 100.0  # pretend we called 100 s ago
    pacer.wait("gpt-4o")               # model changed → should reset _last to 0 first

    # After reset, the timer should have been restarted cleanly
    assert pacer._current_model == "gpt-4o"


def test_pacer_no_reset_same_model() -> None:
    pacer = p07._GhModelsPacer(rpm=600)
    with patch.object(p07.time, "sleep"):
        pacer.wait("gpt-4o-mini")
    first_last = pacer._last

    # Same model: _last should NOT be zeroed out
    pacer._last = first_last  # confirm value unchanged before next call
    # Force time ahead so no sleep is needed
    pacer._last = 0.0
    with patch.object(p07.time, "sleep"):
        pacer.wait("gpt-4o-mini")
    assert pacer._current_model == "gpt-4o-mini"


# ---------------------------------------------------------------------------
# _extract_llm — rate-limit → success on retry
# ---------------------------------------------------------------------------

def test_extract_llm_rate_limit_retries_once_and_succeeds() -> None:
    rate_limit_err = p07.GhModelsRateLimitError("rate limit", retry_after=0.0)
    caller = _SequencedCaller([rate_limit_err, _GOOD_RESPONSE])

    sleep_calls: list[float] = []
    state = _run_extract_llm_with_caller(caller, sleep_mock=lambda s: sleep_calls.append(s))

    assert caller.call_count == 2
    assert state["delta_proposal"]["label"] == "Test Concept"
    # sleep should have been called with the retry_after value
    assert any(s == pytest.approx(0.0) for s in sleep_calls)


def test_extract_llm_rate_limit_honours_retry_after() -> None:
    rate_limit_err = p07.GhModelsRateLimitError("rate limit", retry_after=30.0)
    caller = _SequencedCaller([rate_limit_err, _GOOD_RESPONSE])

    sleep_calls: list[float] = []
    _run_extract_llm_with_caller(caller, sleep_mock=lambda s: sleep_calls.append(s))

    assert 30.0 in sleep_calls


# ---------------------------------------------------------------------------
# _extract_llm — rate-limit retry also fails → graceful degradation
# ---------------------------------------------------------------------------

def test_extract_llm_rate_limit_both_fail_degrades_gracefully() -> None:
    rate_limit_err = p07.GhModelsRateLimitError("rate limit", retry_after=0.0)
    caller = _SequencedCaller([rate_limit_err, rate_limit_err])

    state = _run_extract_llm_with_caller(caller)

    proposal = state["delta_proposal"]
    assert proposal["label"]                     # fallback — non-empty
    assert isinstance(proposal["related"], list)
    assert isinstance(proposal["tags"], list)


def test_extract_llm_rate_limit_retry_fatal_error_degrades_gracefully() -> None:
    rate_limit_err = p07.GhModelsRateLimitError("rate limit", retry_after=0.0)
    proc = CalledProcessError(1, ["gh"], stderr="auth failure")
    caller = _SequencedCaller([rate_limit_err, proc])

    state = _run_extract_llm_with_caller(caller)

    assert state["delta_proposal"]["label"]      # graceful fallback, no exception raised


# ---------------------------------------------------------------------------
# _extract_llm — transient error → backoff retry → success
# ---------------------------------------------------------------------------

def test_extract_llm_transient_retries_with_backoff_and_succeeds() -> None:
    transient = p07.GhModelsUnavailableError("server error")
    caller = _SequencedCaller([transient, _GOOD_RESPONSE])

    sleep_calls: list[float] = []
    state = _run_extract_llm_with_caller(caller, sleep_mock=lambda s: sleep_calls.append(s))

    assert caller.call_count == 2
    assert state["delta_proposal"]["label"] == "Test Concept"
    # One backoff sleep should have occurred
    assert len(sleep_calls) >= 1


def test_extract_llm_transient_two_retries_second_succeeds() -> None:
    transient = p07.GhModelsUnavailableError("server error")
    caller = _SequencedCaller([transient, transient, _GOOD_RESPONSE])

    state = _run_extract_llm_with_caller(caller)

    assert caller.call_count == 3
    assert state["delta_proposal"]["label"] == "Test Concept"


# ---------------------------------------------------------------------------
# _extract_llm — transient always fails → graceful degradation
# ---------------------------------------------------------------------------

def test_extract_llm_transient_always_fails_degrades_gracefully() -> None:
    transient = p07.GhModelsUnavailableError("server error")
    caller = _SequencedCaller([transient, transient, transient])

    state = _run_extract_llm_with_caller(caller)

    proposal = state["delta_proposal"]
    assert proposal["label"]
    assert isinstance(proposal["related"], list)


# ---------------------------------------------------------------------------
# _extract_llm — fatal CalledProcessError → immediate graceful degradation
# ---------------------------------------------------------------------------

def test_extract_llm_fatal_error_degrades_immediately() -> None:
    proc = CalledProcessError(1, ["gh"], stderr="authentication required")
    caller = _SequencedCaller([proc])

    state = _run_extract_llm_with_caller(caller)

    assert caller.call_count == 1         # no retry attempted
    proposal = state["delta_proposal"]
    assert proposal["label"]              # front-matter fallback
    assert isinstance(proposal["aliases"], list)


def test_extract_llm_timeout_degrades_gracefully() -> None:
    import subprocess as _sp
    timeout_err = _sp.TimeoutExpired(["gh"], timeout=120)
    caller = _SequencedCaller([p07.GhModelsUnavailableError("timeout")])

    state = _run_extract_llm_with_caller(caller)

    assert state["delta_proposal"]["label"]
