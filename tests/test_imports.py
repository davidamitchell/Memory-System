"""tests/test_imports.py — Foundational import smoke tests.

Verifies that every pipeline processor (and the top-level run_pipeline module)
can be imported without raising ImportError / ModuleNotFoundError.  A failure
here means a required dependency is missing from the environment, which would
cause a hard crash when the pipeline is executed.

This test MUST pass before any other pipeline tests are considered reliable.
"""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_PROCESSORS_DIR = _REPO_ROOT / "pipeline" / "processors"


def _discover_processor_modules() -> list[str]:
    """Return dotted module paths for every module under pipeline/processors/."""
    import pipeline.processors as _pkg  # noqa: PLC0415

    return [
        f"pipeline.processors.{info.name}"
        for info in pkgutil.iter_modules(_pkg.__path__)
        if not info.name.startswith("_")
    ]


PIPELINE_MODULES = ["pipeline.run_pipeline"] + _discover_processor_modules()


@pytest.mark.parametrize("module_path", PIPELINE_MODULES)
def test_module_importable(module_path: str) -> None:
    """Each pipeline module must import without error."""
    importlib.import_module(module_path)
