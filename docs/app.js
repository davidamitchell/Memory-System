/* docs/app.js — Progressive enhancement for the ontology browser.
 *
 * Layers added on top of the static HTML:
 *  1. Tab switcher — replaces the static anchor nav with a tab bar that
 *     shows/hides sections without a page reload.
 *  2. Live search — injects a <input type="search"> above each table and
 *     filters rows on keyup.
 *  3. Concept detail panel — clicking (or pressing Enter on) a concept row
 *     renders a detail panel below the table showing aliases, tags, related
 *     terms, and the full definition.
 *  4. Concept-link navigation — clicking concept links in the Relations or
 *     Documents sections switches to the Concepts tab and highlights the row.
 *
 * None of this is required; the page works fully without JS.
 */

(function () {
  'use strict';

  // -------------------------------------------------------------------------
  // 1. Tab switcher
  // -------------------------------------------------------------------------

  const sections = Array.from(document.querySelectorAll('main > section'));
  const nav = document.getElementById('main-nav');

  if (nav && sections.length) {
    // Build tab buttons from existing nav links
    const links = Array.from(nav.querySelectorAll('a'));

    function showSection(targetId) {
      sections.forEach(function (sec) {
        sec.hidden = sec.id !== targetId;
      });
      links.forEach(function (a) {
        const active = a.getAttribute('href') === '#' + targetId;
        a.classList.toggle('active', active);
        a.setAttribute('aria-current', active ? 'page' : 'false');
      });
      // Update URL hash without scrolling
      history.replaceState(null, '', '#' + targetId);
    }

    links.forEach(function (a) {
      a.addEventListener('click', function (e) {
        const hash = a.getAttribute('href');
        if (hash && hash.startsWith('#')) {
          e.preventDefault();
          showSection(hash.slice(1));
        }
      });
    });

    // Activate the section matching the current hash, or default to overview
    const initial = (location.hash || '#overview').slice(1);
    const validId = sections.some(function (s) { return s.id === initial; })
      ? initial
      : sections[0].id;
    showSection(validId);
  }

  // -------------------------------------------------------------------------
  // 2. Live search
  // -------------------------------------------------------------------------

  function injectSearch(tableId, placeholder) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const wrap = document.createElement('div');
    wrap.className = 'search-wrap';

    const input = document.createElement('input');
    input.type = 'search';
    input.placeholder = placeholder || 'Filter…';
    input.setAttribute('aria-label', placeholder || 'Filter rows');

    wrap.appendChild(input);
    table.parentNode.insertBefore(wrap, table);

    const tbody = table.querySelector('tbody');

    input.addEventListener('input', function () {
      const q = input.value.trim().toLowerCase();
      Array.from(tbody.rows).forEach(function (row) {
        const text = row.textContent.toLowerCase();
        row.classList.toggle('hidden-row', q.length > 0 && !text.includes(q));
      });
    });
  }

  injectSearch('concepts-table',  'Search concepts…');
  injectSearch('relations-table', 'Search relations…');
  injectSearch('documents-table', 'Search documents…');

  // -------------------------------------------------------------------------
  // 3. Concept detail panel
  // -------------------------------------------------------------------------

  const detailPanel = document.getElementById('concept-detail');

  function renderDetail(concept) {
    if (!detailPanel) return;

    const aliases = (concept.aliases || []).join(', ') || '—';
    const tags    = (concept.tags    || []).map(function (t) {
      return '<span class="badge">' + esc(t) + '</span>';
    }).join(' ') || '—';

    // related is now [{id, rel}, ...] — build labelled links grouped by predicate
    const relatedItems = (concept.related || []);
    const related = relatedItems.length
      ? relatedItems.map(function (item) {
          var id  = typeof item === 'object' ? item.id  : item;
          var rel = typeof item === 'object' ? item.rel : 'relatedTerm';
          var display = id.replace(/-/g, '\u2011');
          var badge = rel !== 'relatedTerm'
            ? ' <span class="pred-badge pred-' + esc(rel) + '">' + esc(rel) + '</span>'
            : '';
          return '<a href="#' + esc(id) + '" class="concept-link" data-id="' + esc(id) + '">' +
                 esc(display) + '</a>' + badge;
        }).join(', ')
      : '—';

    // docs list
    const docs = (concept.docs || []);
    const docsHtml = docs.length
      ? '<ul class="docs-list">' + docs.map(function (f) {
          var fname = f.replace(/^.*\//, '');
          // Link to the Documents tab entry
          return '<li><a href="#documents" class="section-link" data-doc="' + esc(f) + '">' +
                 '<code>' + esc(fname) + '</code></a></li>';
        }).join('') + '</ul>'
      : '<span class="muted">—</span>';

    detailPanel.innerHTML =
      '<button class="detail-close" aria-label="Close detail panel">&times;</button>' +
      '<h3>' + esc(concept.label) + '</h3>' +
      '<div class="detail-row"><span class="detail-label">Definition</span>' +
        '<span class="detail-value">' + esc(concept.comment || '—') + '</span></div>' +
      '<div class="detail-row"><span class="detail-label">Domain</span>' +
        '<span class="detail-value">' + esc(concept.domain || '—') + '</span></div>' +
      '<div class="detail-row"><span class="detail-label">Aliases</span>' +
        '<span class="detail-value">' + esc(aliases) + '</span></div>' +
      '<div class="detail-row"><span class="detail-label">Tags</span>' +
        '<span class="detail-value">' + tags + '</span></div>' +
      '<div class="detail-row"><span class="detail-label">Related</span>' +
        '<span class="detail-value">' + related + '</span></div>' +
      '<div class="detail-row"><span class="detail-label">Documents</span>' +
        '<span class="detail-value">' + docsHtml + '</span></div>';

    detailPanel.hidden = false;

    // Bind close button
    detailPanel.querySelector('.detail-close').addEventListener('click', function () {
      closeDetail();
    });

    // Bind concept links inside the panel
    bindConceptLinks(detailPanel);

    // Bind document links — navigate to Documents tab and scroll to the row
    detailPanel.querySelectorAll('a.section-link').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var docFile = a.getAttribute('data-doc');
        if (nav) {
          var docsLink = nav.querySelector('a[href="#documents"]');
          if (docsLink) docsLink.click();
        }
        if (docFile) {
          var row = document.querySelector('tr[data-file="' + docFile + '"]');
          if (row) {
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
            row.classList.add('highlight');
            setTimeout(function () { row.classList.remove('highlight'); }, 1500);
          }
        }
      });
    });
  }

  function closeDetail() {
    if (!detailPanel) return;
    detailPanel.hidden = true;
    detailPanel.innerHTML = '';
    // Remove selected state from all rows
    document.querySelectorAll('tr.concept-row.selected').forEach(function (r) {
      r.classList.remove('selected');
    });
  }

  function esc(str) {
    return String(str)
      .replace(/&/g,  '&amp;')
      .replace(/</g,  '&lt;')
      .replace(/>/g,  '&gt;')
      .replace(/"/g,  '&quot;');
  }

  // Attach click/keydown handlers to all concept rows in the concepts table
  document.querySelectorAll('tr.concept-row').forEach(function (row) {
    function activate() {
      var raw = row.getAttribute('data-concept');
      if (!raw) return;
      try {
        var concept = JSON.parse(raw);
        // Deselect others
        document.querySelectorAll('tr.concept-row.selected').forEach(function (r) {
          r.classList.remove('selected');
        });
        row.classList.add('selected');
        renderDetail(concept);
      } catch (e) {
        // Silently ignore malformed data
      }
    }

    row.addEventListener('click', activate);
    row.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        activate();
      }
      if (e.key === 'Escape') {
        closeDetail();
      }
    });
  });

  // -------------------------------------------------------------------------
  // 4. Concept-link navigation
  // -------------------------------------------------------------------------

  function bindConceptLinks(root) {
    (root || document).querySelectorAll('a.concept-link').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('data-id');
        if (!id) return;

        // Switch to the concepts tab
        e.preventDefault();
        if (nav) {
          var conceptsLink = nav.querySelector('a[href="#concepts"]');
          if (conceptsLink) conceptsLink.click();
        }

        // Find the matching row and activate it
        var targetRow = document.querySelector('tr.concept-row[data-id="' + id + '"]');
        if (targetRow) {
          targetRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
          targetRow.focus();
          targetRow.click();
        }
      });
    });
  }

  bindConceptLinks(document);

})();
