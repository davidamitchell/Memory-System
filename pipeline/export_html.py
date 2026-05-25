#!/usr/bin/env python3
"""pipeline/export_html.py — Ontology JSON → static HTML generator.

Reads ``docs/data/ontology.json`` (produced by ``export_json.py``) and
writes ``docs/index.html``.  The HTML is fully self-contained: all four
sections (Overview, Concepts, Relations, Documents) are rendered as plain
``<table>`` elements so the page is navigable without JavaScript.

``docs/app.js`` then progressively enhances the page with tab switching,
live search, and a concept detail panel.

Usage
-----
    python pipeline/export_html.py
    python pipeline/export_html.py --json path/to/ontology.json --out path/to/index.html
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def h(text: str) -> str:
    """HTML-escape a string."""
    return html.escape(str(text), quote=True)


def badge(text: str) -> str:
    return f'<span class="badge">{h(text)}</span>'


def tag_badges(tags: list[str]) -> str:
    return " ".join(badge(t) for t in tags)


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def render_overview(data: dict) -> str:
    meta = data["meta"]
    counts = meta["counts"]
    return f"""
<section id="overview" aria-label="Overview">
  <h2>Overview</h2>
  <table class="stats">
    <tbody>
      <tr><th>Ontology version</th><td>{h(meta['version'])}</td></tr>
      <tr><th>Generated</th><td>{h(meta['generated'])}</td></tr>
      <tr><th>Concepts</th><td>{counts['concepts']}</td></tr>
      <tr><th>Relations</th><td>{counts['relations']}</td></tr>
      <tr><th>Source documents</th><td>{counts['documents']}</td></tr>
    </tbody>
  </table>
</section>
""".strip()


def render_concepts(data: dict) -> str:
    rows = []
    for c in data["concepts"]:
        cid = h(c["id"])
        label = h(c["label"])
        comment_short = h(c["comment"][:120] + ("…" if len(c["comment"]) > 120 else ""))
        domain = h(c["domain"])
        n_tags = len(c["tags"])
        n_related = len(c["related"])

        # Encode full concept data as JSON in data-* attribute for JS detail panel
        concept_json = h(json.dumps(c))

        rows.append(
            f'    <tr class="concept-row" data-id="{cid}" data-concept="{concept_json}" tabindex="0">\n'
            f'      <td><strong>{label}</strong><br><small class="muted">{comment_short}</small></td>\n'
            f'      <td data-label="Domain">{domain}</td>\n'
            f'      <td class="num" data-label="Tags">{n_tags}</td>\n'
            f'      <td class="num" data-label="Related">{n_related}</td>\n'
            f'    </tr>'
        )

    rows_html = "\n".join(rows)
    return f"""
<section id="concepts" aria-label="Concepts">
  <h2>Concepts <span class="count">({len(data['concepts'])})</span></h2>
  <table id="concepts-table">
    <thead>
      <tr>
        <th>Label / Definition</th>
        <th>Domain</th>
        <th class="num" title="Number of tags">Tags</th>
        <th class="num" title="Number of related terms">Related</th>
      </tr>
    </thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
  <div id="concept-detail" class="detail-panel" hidden aria-live="polite"></div>
</section>
""".strip()


def render_relations(data: dict) -> str:
    rows = []
    for r in data["relations"]:
        from_id = h(r["from_id"])
        from_label = h(r["from_label"])
        predicate = h(r.get("predicate", "relatedTerm"))
        to_id = h(r["to_id"])
        to_label = h(r["to_label"])
        rows.append(
            f'    <tr>\n'
            f'      <td data-label="From"><a href="#{from_id}" class="concept-link" data-id="{from_id}">{from_label}</a></td>\n'
            f'      <td class="predicate predicate-{predicate}" data-label="Predicate">{predicate}</td>\n'
            f'      <td data-label="To"><a href="#{to_id}" class="concept-link" data-id="{to_id}">{to_label}</a></td>\n'
            f'    </tr>'
        )

    rows_html = "\n".join(rows)
    return f"""
<section id="relations" aria-label="Relations">
  <h2>Relations <span class="count">({len(data['relations'])})</span></h2>
  <div class="table-scroll">
  <table id="relations-table">
    <thead>
      <tr>
        <th>From</th>
        <th>Predicate</th>
        <th>To</th>
      </tr>
    </thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
  </div>
</section>
""".strip()


def render_documents(data: dict) -> str:
    # Build concept id → label lookup
    label_lookup = {c["id"]: c["label"] for c in data["concepts"]}

    rows = []
    for doc in data["documents"]:
        fname = h(doc["file"])
        seg_count = doc["segment_count"]
        concept_links = []
        for cid in doc["concept_ids"]:
            cid_h = h(cid)
            clabel = h(label_lookup.get(cid, cid))
            concept_links.append(
                f'<a href="#{cid_h}" class="concept-link" data-id="{cid_h}">{clabel}</a>'
            )
        concepts_cell = ", ".join(concept_links) if concept_links else '<span class="muted">—</span>'
        rows.append(
            f'    <tr data-file="{fname}">\n'
            f'      <td data-label="File"><code>{fname}</code></td>\n'
            f'      <td class="num" data-label="Segments">{seg_count}</td>\n'
            f'      <td data-label="Concepts">{concepts_cell}</td>\n'
            f'    </tr>'
        )

    rows_html = "\n".join(rows)
    return f"""
<section id="documents" aria-label="Documents">
  <h2>Documents <span class="count">({len(data['documents'])})</span></h2>
  <div class="table-scroll">
  <table id="documents-table">
    <thead>
      <tr>
        <th>File</th>
        <th class="num" title="Number of text segments">Segments</th>
        <th>Concepts</th>
      </tr>
    </thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
  </div>
</section>
""".strip()


# ---------------------------------------------------------------------------
# Full page
# ---------------------------------------------------------------------------

def render_page(data: dict) -> str:
    meta = data["meta"]
    overview = render_overview(data)
    concepts = render_concepts(data)
    relations = render_relations(data)
    documents = render_documents(data)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Open-Brain Ontology Browser — {h(meta['version'])}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
<header>
  <h1>Open-Brain Ontology Browser</h1>
  <p class="subtitle">Version <strong>{h(meta['version'])}</strong> &middot; {h(meta['generated'])}</p>
  <nav id="main-nav" aria-label="Sections">
    <a href="#overview">Overview</a>
    <a href="#concepts">Concepts</a>
    <a href="#relations">Relations</a>
    <a href="#documents">Documents</a>
  </nav>
</header>

<main>
{overview}

{concepts}

{relations}

{documents}
</main>

<footer>
  <p>Generated from <code>data/ontology/{h(meta['version'])}.ttl</code> &middot;
  <a href="https://github.com/davidamitchell/Memory-System">Memory-System</a></p>
</footer>

<script src="app.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Export ontology JSON to static HTML.")
    parser.add_argument(
        "--json",
        type=Path,
        default=REPO_ROOT / "docs" / "data" / "ontology.json",
        help="Input JSON file (default: docs/data/ontology.json)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "docs" / "index.html",
        help="Output HTML file (default: docs/index.html)",
    )
    args = parser.parse_args()

    if not args.json.exists():
        print(f"JSON not found: {args.json}. Run export_json.py first.", file=sys.stderr)
        sys.exit(1)

    with open(args.json, encoding="utf-8") as fh:
        data = json.load(fh)

    page = render_page(data)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(page)

    print(f"Written {len(page):,} bytes → {args.out}")


if __name__ == "__main__":
    main()
