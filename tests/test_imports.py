"""tests/test_imports.py — Foundational import smoke tests.

Verifies that every pipeline processor (and the top-level run_pipeline module)
can be imported without raising ImportError / ModuleNotFoundError.  A failure
here means a required dependency is missing from the environment, which would
cause a hard crash when the pipeline is executed.

This test MUST pass before any other pipeline tests are considered reliable.
"""
from __future__ import annotations

import importlib

import pytest

# All modules that must be importable in a correctly-provisioned environment.
# Add new processors here as they are introduced.
PIPELINE_MODULES = [
    "pipeline.run_pipeline",
    "pipeline.processors.p01_sourcing",
    "pipeline.processors.p02_preparation",
    "pipeline.processors.p03_segmentation",
    "pipeline.processors.p04_metadata",
    "pipeline.processors.p05_domain_classification",
    "pipeline.processors.p06_domain_matching",
    "pipeline.processors.p07_concept_extraction",
    "pipeline.processors.p08_ontology_build",
    "pipeline.processors.p09_consistency_validation",
    "pipeline.processors.p10_reconciliation",
    "pipeline.processors.p11_version_commit",
    "pipeline.processors.p12_export",
]


@pytest.mark.parametrize("module_path", PIPELINE_MODULES)
def test_module_importable(module_path: str) -> None:
    """Each pipeline module must import without error."""
    importlib.import_module(module_path)
