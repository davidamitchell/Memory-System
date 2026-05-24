#!/usr/bin/env python3
"""pipeline/eval.py — Extractor evaluation harness (W-0203).

Runs any extractor strategy against a document corpus and scores the
``delta_proposal`` output against the ground-truth values in the YAML
front-matter.  Metrics: precision, recall, F1 for each of four fields
(label, aliases, tags, related edges), reported per-file and as an
aggregate.

Usage
-----
    # Rule-based extractor against the glossary (baseline):
    python pipeline/eval.py --corpus glossary/

    # Explicit extractor flag (rule-based is the default):
    python pipeline/eval.py --corpus glossary/ --extractor rule-based

    # LLM extractor (requires OPENAI_API_KEY or equivalent):
    python pipeline/eval.py --corpus glossary/ --extractor llm

    # JSON output:
    python pipeline/eval.py --corpus glossary/ --json

Ground truth
------------
For the ``glossary/`` corpus the ground truth is the YAML front-matter:
  - label     → ``title`` field (single string; F1 is 1.0 if exact match)
  - aliases   → ``aliases`` field (list of strings)
  - tags      → ``tags`` field (list of strings)
  - related   → ``related[].file`` stems (list of slugs)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

from pipeline.processors import (  # noqa: E402
    p01_sourcing,
    p02_preparation,
    p03_segmentation,
    p04_metadata,
    p05_domain_classification,
    p06_domain_matching,
    p07_concept_extraction,
)

logger = logging.getLogger(__name__)

_EXTRACT_PROCESSORS = [
    p01_sourcing,
    p02_preparation,
    p03_segmentation,
    p04_metadata,
    p05_domain_classification,
    p06_domain_matching,
]

_FRONT_MATTER_RE = __import__("re").compile(r"^---\s*\n(.*?\n)---\s*\n", __import__("re").DOTALL)


# ---------------------------------------------------------------------------
# Ground-truth extraction from the file itself (not via pipeline)
# ---------------------------------------------------------------------------

def _load_ground_truth(path: Path) -> dict:
    """Read the YAML front-matter and return canonical ground-truth fields."""
    raw = path.read_text(encoding="utf-8")
    m = _FRONT_MATTER_RE.match(raw)
    if not m:
        return {"label": path.stem, "aliases": [], "tags": [], "related": []}
    fm: dict = yaml.safe_load(m.group(1)) or {}
    label = str(fm.get("title", path.stem)).strip()
    aliases = [str(a).strip() for a in fm.get("aliases", [])]
    tags = [str(t).strip().lower() for t in fm.get("tags", [])]
    related = []
    for r in fm.get("related", []):
        if isinstance(r, dict):
            slug = r.get("file", "")
            # strip extension
            slug = Path(slug).stem if slug else ""
            if slug:
                related.append(slug)
        elif isinstance(r, str):
            related.append(r.strip())
    return {"label": label, "aliases": aliases, "tags": tags, "related": related}


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------

def _prf(predicted: list[str], ground_truth: list[str]) -> tuple[float, float, float]:
    """Precision, recall, F1 for set comparison (case-insensitive)."""
    pred_set = {v.lower() for v in predicted}
    gt_set = {v.lower() for v in ground_truth}
    if not gt_set and not pred_set:
        return 1.0, 1.0, 1.0
    if not pred_set:
        return 0.0, 0.0, 0.0
    if not gt_set:
        return 0.0, 1.0, 0.0
    tp = len(pred_set & gt_set)
    precision = tp / len(pred_set)
    recall = tp / len(gt_set)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return precision, recall, f1


def _label_f1(predicted: str, ground_truth: str) -> tuple[float, float, float]:
    """F1 for label match (1.0 if exact case-insensitive match, else 0.0)."""
    match = predicted.strip().lower() == ground_truth.strip().lower()
    score = 1.0 if match else 0.0
    return score, score, score


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


# ---------------------------------------------------------------------------
# Per-file evaluation
# ---------------------------------------------------------------------------

def evaluate_file(source_path: str, extractor: str = "rule-based") -> dict:
    """Run the extractor on one file and return per-field metrics."""
    # Run p01–p06 to populate state up to domain matching
    state: dict = {"source_path": source_path, "extractor": extractor}
    for proc in _EXTRACT_PROCESSORS:
        state = proc.run(state, REPO_ROOT)

    # Run p07 (concept extraction) with strategy from extractor flag
    state["strategy"] = extractor
    state = p07_concept_extraction.run(state, REPO_ROOT)

    proposal = state["delta_proposal"]
    predicted_label = proposal.get("label", "")
    predicted_aliases = proposal.get("aliases", [])
    predicted_tags = [t.lower() for t in proposal.get("tags", [])]
    predicted_related = [r["id"].split("/")[-1] for r in proposal.get("related", [])]

    # Ground truth from file
    abs_path = REPO_ROOT / source_path
    gt = _load_ground_truth(abs_path)

    lp, lr, lf = _label_f1(predicted_label, gt["label"])
    ap, ar, af = _prf(predicted_aliases, gt["aliases"])
    tp, tr, tf = _prf(predicted_tags, gt["tags"])
    rp, rr, rf = _prf(predicted_related, gt["related"])

    return {
        "file": source_path,
        "label":   {"precision": lp, "recall": lr, "f1": lf,
                    "predicted": predicted_label, "truth": gt["label"]},
        "aliases": {"precision": ap, "recall": ar, "f1": af,
                    "predicted": predicted_aliases, "truth": gt["aliases"]},
        "tags":    {"precision": tp, "recall": tr, "f1": tf,
                    "predicted": predicted_tags, "truth": gt["tags"]},
        "related": {"precision": rp, "recall": rr, "f1": rf,
                    "predicted": predicted_related, "truth": gt["related"]},
    }


# ---------------------------------------------------------------------------
# Aggregate reporting
# ---------------------------------------------------------------------------

def aggregate(results: list[dict]) -> dict:
    """Average per-file metrics across the corpus."""
    fields = ["label", "aliases", "tags", "related"]
    agg: dict = {}
    for field in fields:
        agg[field] = {
            "precision": _avg([r[field]["precision"] for r in results]),
            "recall":    _avg([r[field]["recall"]    for r in results]),
            "f1":        _avg([r[field]["f1"]        for r in results]),
        }
    return agg


def print_report(results: list[dict], agg: dict, extractor: str) -> None:
    """Pretty-print per-file and aggregate metrics to stdout."""
    FIELDS = ["label", "aliases", "tags", "related"]
    col_w = 10

    header = f"{'File':<45}" + "".join(f"{'  '+f+' F1':>{col_w}}" for f in FIELDS)
    print(f"\nExtractor: {extractor}")
    print(f"Files:     {len(results)}")
    print()
    print(header)
    print("-" * len(header))

    for r in results:
        fname = r["file"][-44:] if len(r["file"]) > 44 else r["file"]
        row = f"{fname:<45}" + "".join(
            f"{r[f]['f1']:>{col_w}.3f}" for f in FIELDS
        )
        print(row)

    print("-" * len(header))
    agg_row = f"{'AGGREGATE':<45}" + "".join(
        f"{agg[f]['f1']:>{col_w}.3f}" for f in FIELDS
    )
    print(agg_row)
    print()
    print("Aggregate detail:")
    for f in FIELDS:
        m = agg[f]
        print(f"  {f:<10}  P={m['precision']:.3f}  R={m['recall']:.3f}  F1={m['f1']:.3f}")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate an extractor against a document corpus.")
    parser.add_argument(
        "--corpus",
        type=Path,
        default=REPO_ROOT / "glossary",
        help="Directory of .md files to evaluate (default: glossary/)",
    )
    parser.add_argument(
        "--extractor",
        default="rule-based",
        choices=["rule-based", "llm"],
        help="Extraction strategy to evaluate (default: rule-based)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit results as JSON to stdout instead of the human-readable report",
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        level=logging.WARNING,  # suppress pipeline INFO noise during eval
    )

    corpus_path = args.corpus if args.corpus.is_absolute() else REPO_ROOT / args.corpus
    if not corpus_path.is_dir():
        print(f"Corpus directory not found: {corpus_path}", file=sys.stderr)
        sys.exit(1)

    md_files = sorted(
        p for p in corpus_path.rglob("*.md") if not p.name.startswith("README")
    )
    if not md_files:
        print(f"No .md files found in {corpus_path}", file=sys.stderr)
        sys.exit(1)

    rel_paths = [str(f.relative_to(REPO_ROOT)) for f in md_files]

    results = []
    for rel in rel_paths:
        try:
            result = evaluate_file(rel, extractor=args.extractor)
            results.append(result)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipping %s: %s", rel, exc)

    if not results:
        print("No files could be evaluated.", file=sys.stderr)
        sys.exit(1)

    agg = aggregate(results)

    if args.json_output:
        print(json.dumps({"extractor": args.extractor, "results": results, "aggregate": agg}, indent=2))
    else:
        print_report(results, agg, extractor=args.extractor)


if __name__ == "__main__":
    main()
