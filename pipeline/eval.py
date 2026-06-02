#!/usr/bin/env python3
"""pipeline/eval.py — Extractor evaluation harness (W-0203, W-0206).

Runs any extractor strategy against a document corpus and scores the
``delta_proposal`` output against the ground-truth values in the YAML
front-matter.  Metrics: precision, recall, F1 for each of three fields
(label, aliases, related edges), reported per-file and as an aggregate.

Usage
-----
    # Rule-based extractor against the foundational concepts (baseline):
    python pipeline/eval.py --corpus foundational_concepts/

    # Explicit extractor flag (rule-based is the default):
    python pipeline/eval.py --corpus foundational_concepts/ --extractor rule-based

    # LLM extractor:
    python pipeline/eval.py --corpus foundational_concepts/ --extractor llm

    # JSON output:
    python pipeline/eval.py --corpus foundational_concepts/ --json

    # Typed relation extraction eval (W-0206, LLM only, requires gh auth):
    python pipeline/eval.py --typed-relations

Ground truth
------------
For the ``foundational_concepts/`` corpus the ground truth is the YAML front-matter
where present (legacy files), or extracted prose otherwise:
  - label     → ``title`` field (single string; F1 is 1.0 if exact match)
  - aliases   → ``aliases`` field (list of strings)
  - related   → ``related[].file`` stems (list of slugs)

Tags and themes are extraction signal only (they hint to the LLM which concepts
may be present) and are not scored as ground truth.

For typed relations (``--typed-relations``) the ground truth is loaded from
``data/eval/typed-relations-ground-truth.json``.  Each annotated file is
scored on (target_slug, rel_type) pair exact match, with per-type breakdown.
NOTE: typed relation evaluation requires the LLM extractor (``--extractor llm``).
Rule-based extraction produces no typed relations from prose files and will
return 0.0 F1.
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
        return {"label": path.stem, "aliases": [], "related": []}
    fm: dict = yaml.safe_load(m.group(1)) or {}
    label = str(fm.get("title", path.stem)).strip()
    aliases = [str(a).strip() for a in fm.get("aliases", [])]
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
    return {"label": label, "aliases": aliases, "related": related}


# ---------------------------------------------------------------------------
# Typed relations ground truth (W-0206)
# ---------------------------------------------------------------------------

_DEFAULT_TYPED_GT_PATH = REPO_ROOT / "data" / "eval" / "typed-relations-ground-truth.json"


def _load_typed_relations_ground_truth(path: Path = _DEFAULT_TYPED_GT_PATH) -> dict:
    """Load typed-relations annotation file.

    Returns a mapping of ``slug -> list[{"target": str, "rel": str}]``.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    gt_by_slug: dict = {}
    for entry in data.get("annotated_files", []):
        slug = entry["slug"]
        gt_by_slug[slug] = entry.get("typed_relations", [])
    return gt_by_slug


def score_typed_relations(
    predicted_related: list[dict],
    ground_truth_typed: list[dict],
) -> dict:
    """Score typed relation predictions against ground truth.

    Parameters
    ----------
    predicted_related:
        List of ``{"id": "assertion/<slug>", "rel": "<type>"}`` dicts from
        ``delta_proposal.related``.
    ground_truth_typed:
        List of ``{"target": "<slug>", "rel": "<type>"}`` dicts from the
        annotation file.

    Returns
    -------
    dict with keys:
    - ``exact``: overall P/R/F1 for (target_slug, rel_type) exact-match pairs
    - ``target_only``: P/R/F1 ignoring rel_type (did we find the right targets?)
    - ``by_type``: per rel_type P/R/F1 breakdown
    """
    # Build predicted pairs: (target_slug, rel_type)
    predicted_pairs: set[tuple[str, str]] = set()
    predicted_targets: set[str] = set()
    for r in predicted_related:
        slug = r.get("id", "").split("/")[-1].lower()
        rel = r.get("rel", "relatedTerm").lower()
        if slug:
            predicted_pairs.add((slug, rel))
            predicted_targets.add(slug)

    # Build ground truth pairs
    gt_pairs: set[tuple[str, str]] = set()
    gt_targets: set[str] = set()
    for r in ground_truth_typed:
        slug = r.get("target", "").lower()
        rel = r.get("rel", "relatedTerm").lower()
        if slug:
            gt_pairs.add((slug, rel))
            gt_targets.add(slug)

    # Exact match P/R/F1 — serialize pairs to "slug:rel" strings for _prf
    def _pairs_as_str(pairs: set[tuple[str, str]]) -> list[str]:
        return [f"{s}:{r}" for s, r in pairs]

    exact_p, exact_r, exact_f = _prf(_pairs_as_str(predicted_pairs), _pairs_as_str(gt_pairs))

    # Target-only P/R/F1
    target_p, target_r, target_f = _prf(list(predicted_targets), list(gt_targets))

    # Per-type breakdown
    all_rel_types = {rel for _, rel in gt_pairs} | {rel for _, rel in predicted_pairs}
    by_type: dict = {}
    for rel_type in sorted(all_rel_types):
        pred_type = {slug for slug, rel in predicted_pairs if rel == rel_type}
        gt_type = {slug for slug, rel in gt_pairs if rel == rel_type}
        p, r, f = _prf(list(pred_type), list(gt_type))
        by_type[rel_type] = {"precision": p, "recall": r, "f1": f}

    return {
        "exact": {"precision": exact_p, "recall": exact_r, "f1": exact_f},
        "target_only": {"precision": target_p, "recall": target_r, "f1": target_f},
        "by_type": by_type,
        "predicted_pairs": sorted(predicted_pairs),
        "gt_pairs": sorted(gt_pairs),
    }


def evaluate_file_typed_relations(source_path: str, extractor: str, gt_entry: list[dict]) -> dict:
    """Run the extractor on one file and score its typed relations."""
    state: dict = {"source_path": source_path, "extractor": extractor, "nlp": False}
    for proc in _EXTRACT_PROCESSORS:
        state = proc.run(state, REPO_ROOT)
    state["strategy"] = extractor
    state = p07_concept_extraction.run(state, REPO_ROOT)

    proposal = state["delta_proposal"]
    predicted_related = proposal.get("related", [])
    scores = score_typed_relations(predicted_related, gt_entry)
    return {"file": source_path, **scores}


def aggregate_typed_relations(results: list[dict]) -> dict:
    """Macro-average typed relation metrics across evaluated files."""
    exact_f = _avg([r["exact"]["f1"] for r in results])
    exact_p = _avg([r["exact"]["precision"] for r in results])
    exact_r = _avg([r["exact"]["recall"] for r in results])

    target_f = _avg([r["target_only"]["f1"] for r in results])
    target_p = _avg([r["target_only"]["precision"] for r in results])
    target_r = _avg([r["target_only"]["recall"] for r in results])

    # Per-type macro-average across files that have ground truth for that type
    all_types: set[str] = set()
    for r in results:
        all_types.update(r.get("by_type", {}).keys())
    by_type: dict = {}
    for rel_type in sorted(all_types):
        vals = [r["by_type"][rel_type]["f1"] for r in results if rel_type in r.get("by_type", {})]
        by_type[rel_type] = {"f1": _avg(vals)}

    return {
        "exact": {"precision": exact_p, "recall": exact_r, "f1": exact_f},
        "target_only": {"precision": target_p, "recall": target_r, "f1": target_f},
        "by_type": by_type,
    }


def print_typed_relations_report(results: list[dict], agg: dict, extractor: str) -> None:
    """Pretty-print typed relation eval results."""
    col_w = 9

    print(f"\nTyped Relation Eval (W-0206)")
    print(f"Extractor: {extractor}  |  Files: {len(results)}")
    print()
    header = f"{'File':<45}{'Exact F1':>{col_w}}{'Target F1':>{col_w}}"
    print(header)
    print("-" * len(header))
    for r in results:
        fname = r["file"][-44:] if len(r["file"]) > 44 else r["file"]
        print(f"{fname:<45}{r['exact']['f1']:>{col_w}.3f}{r['target_only']['f1']:>{col_w}.3f}")
    print("-" * len(header))
    print(f"{'AGGREGATE':<45}{agg['exact']['f1']:>{col_w}.3f}{agg['target_only']['f1']:>{col_w}.3f}")
    print()
    print("Aggregate exact-match:")
    m = agg["exact"]
    print(f"  {'all':<14}  P={m['precision']:.3f}  R={m['recall']:.3f}  F1={m['f1']:.3f}")
    print()
    print("Per-type macro-average F1 (exact target + type match):")
    for rel_type, metrics in agg["by_type"].items():
        print(f"  {rel_type:<14}  F1={metrics['f1']:.3f}")
    print()


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

def evaluate_file(source_path: str, extractor: str = "rule-based", nlp: bool = False) -> dict:
    """Run the extractor on one file and return per-field metrics."""
    # Run p01–p06 to populate state up to domain matching
    state: dict = {"source_path": source_path, "extractor": extractor, "nlp": nlp}
    for proc in _EXTRACT_PROCESSORS:
        state = proc.run(state, REPO_ROOT)

    # Run p07 (concept extraction) with strategy from extractor flag
    state["strategy"] = extractor
    state = p07_concept_extraction.run(state, REPO_ROOT)

    proposal = state["delta_proposal"]
    predicted_label = proposal.get("label", "")
    predicted_aliases = proposal.get("aliases", [])
    predicted_related = [r["id"].split("/")[-1] for r in proposal.get("related", [])]

    # Ground truth from file
    abs_path = REPO_ROOT / source_path
    gt = _load_ground_truth(abs_path)

    lp, lr, lf = _label_f1(predicted_label, gt["label"])
    ap, ar, af = _prf(predicted_aliases, gt["aliases"])
    rp, rr, rf = _prf(predicted_related, gt["related"])

    return {
        "file": source_path,
        "label":   {"precision": lp, "recall": lr, "f1": lf,
                    "predicted": predicted_label, "truth": gt["label"]},
        "aliases": {"precision": ap, "recall": ar, "f1": af,
                    "predicted": predicted_aliases, "truth": gt["aliases"]},
        "related": {"precision": rp, "recall": rr, "f1": rf,
                    "predicted": predicted_related, "truth": gt["related"]},
    }


# ---------------------------------------------------------------------------
# Aggregate reporting
# ---------------------------------------------------------------------------

def aggregate(results: list[dict]) -> dict:
    """Average per-file metrics across the corpus."""
    fields = ["label", "aliases", "related"]
    agg: dict = {}
    for field in fields:
        agg[field] = {
            "precision": _avg([r[field]["precision"] for r in results]),
            "recall":    _avg([r[field]["recall"]    for r in results]),
            "f1":        _avg([r[field]["f1"]        for r in results]),
        }
    return agg


def print_report(results: list[dict], agg: dict, extractor: str, nlp: bool = False) -> None:
    """Pretty-print per-file and aggregate metrics to stdout."""
    FIELDS = ["label", "aliases", "related"]
    col_w = 10

    header = f"{'File':<45}" + "".join(f"{'  '+f+' F1':>{col_w}}" for f in FIELDS)
    print(f"\nExtractor: {extractor}" + (" + NLP enrichment" if nlp else ""))
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
        default=REPO_ROOT / "foundational_concepts",
        help="Directory of .md files to evaluate (default: foundational_concepts/)",
    )
    parser.add_argument(
        "--extractor",
        default="rule-based",
        choices=["rule-based", "llm"],
        help="Extraction strategy to evaluate (default: rule-based)",
    )
    parser.add_argument(
        "--nlp",
        action="store_true",
        dest="nlp",
        help="Enable NLP enrichment in p02 (requires spacy and en_core_web_sm)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit results as JSON to stdout instead of the human-readable report",
    )
    parser.add_argument(
        "--typed-relations",
        action="store_true",
        dest="typed_relations",
        help=(
            "Score typed relation extraction (W-0206). Reads ground truth from "
            "data/eval/typed-relations-ground-truth.json. NOTE: requires --extractor llm "
            "and a working gh auth session; rule-based returns 0.0 F1 on prose files."
        ),
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

    # --typed-relations mode: score only the annotated files in the ground-truth JSON
    if args.typed_relations:
        gt_path = _DEFAULT_TYPED_GT_PATH
        if not gt_path.exists():
            print(f"Ground truth file not found: {gt_path}", file=sys.stderr)
            sys.exit(1)
        gt_by_slug = _load_typed_relations_ground_truth(gt_path)
        tr_results = []
        for slug, gt_entry in gt_by_slug.items():
            rel_path = str(Path("foundational_concepts") / f"{slug}.md")
            abs_path = REPO_ROOT / rel_path
            if not abs_path.exists():
                logger.warning("Skipping %s: file not found", rel_path)
                continue
            try:
                result = evaluate_file_typed_relations(rel_path, extractor=args.extractor, gt_entry=gt_entry)
                tr_results.append(result)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Skipping %s: %s", rel_path, exc)

        if not tr_results:
            print("No files could be evaluated.", file=sys.stderr)
            sys.exit(1)

        tr_agg = aggregate_typed_relations(tr_results)
        if args.json_output:
            print(json.dumps({"extractor": args.extractor, "results": tr_results, "aggregate": tr_agg}, indent=2))
        else:
            print_typed_relations_report(tr_results, tr_agg, extractor=args.extractor)
        return

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
            result = evaluate_file(rel, extractor=args.extractor, nlp=args.nlp)
            results.append(result)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipping %s: %s", rel, exc)

    if not results:
        print("No files could be evaluated.", file=sys.stderr)
        sys.exit(1)

    agg = aggregate(results)

    if args.json_output:
        print(json.dumps({"extractor": args.extractor, "nlp": args.nlp, "results": results, "aggregate": agg}, indent=2))
    else:
        print_report(results, agg, extractor=args.extractor, nlp=args.nlp)


if __name__ == "__main__":
    main()
