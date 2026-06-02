/* docs/app.js — Progressive enhancement for the ontology browser.
 *
 * Layers added on top of the static HTML:
 *  1. Data index   — builds concept / relation lookups from embedded DOM data
 *  2. Router       — hash-based routing: #concept/<id>, #relation/<from>/<pred>/<to>
 *  3. Tab switcher — shows/hides sections for #overview, #concepts, #relations, #documents
 *  4. Live search  — injects a <input type="search"> above each table
 *  5. Concept page — full-page detail view for a concept
 *  6. Relation page — full-page detail view for a relation edge
 *
 * None of this is required; the page works fully without JS.
 */

(function () {
  'use strict';

  // -------------------------------------------------------------------------
  // 1. Data index
  // -------------------------------------------------------------------------

  // Build concept lookup from data-concept JSON attrs on concept rows
  var conceptIndex = Object.create(null);
  document.querySelectorAll('tr.concept-row[data-concept]').forEach(function (row) {
    try {
      var c = JSON.parse(row.getAttribute('data-concept'));
      conceptIndex[c.id] = c;
    } catch (_) {}
  });

  // Build relation list from data-relation JSON attrs on relation rows
  var relationList = [];
  document.querySelectorAll('tr.relation-row[data-relation]').forEach(function (row) {
    try {
      relationList.push(JSON.parse(row.getAttribute('data-relation')));
    } catch (_) {}
  });

  // -------------------------------------------------------------------------
  // 2. Router + shared page container
  // -------------------------------------------------------------------------

  var mainEl = document.querySelector('main');
  var sections = Array.from(document.querySelectorAll('main > section'));
  var nav = document.getElementById('main-nav');
  var navLinks = nav ? Array.from(nav.querySelectorAll('a')) : [];

  // Inject a single detail-page container that replaces section content
  var detailPage = document.createElement('div');
  detailPage.id = 'detail-page';
  detailPage.hidden = true;
  mainEl.appendChild(detailPage);

  function route() {
    var hash = location.hash || '#overview';
    if (hash.startsWith('#concept/')) {
      showConceptPage(decodeURIComponent(hash.slice('#concept/'.length)));
    } else if (hash.startsWith('#relation/')) {
      var parts = decodeURIComponent(hash.slice('#relation/'.length)).split('/');
      if (parts.length >= 3) {
        showRelationPage(parts[0], parts[1], parts[2]);
      } else {
        showSection(sections[0].id);
      }
    } else {
      var targetId = hash.slice(1);
      var valid = sections.some(function (s) { return s.id === targetId; });
      showSection(valid ? targetId : sections[0].id);
    }
  }

  window.addEventListener('hashchange', route);

  // -------------------------------------------------------------------------
  // 3. Tab switcher
  // -------------------------------------------------------------------------

  function showSection(targetId) {
    detailPage.hidden = true;
    detailPage.innerHTML = '';
    sections.forEach(function (sec) {
      sec.hidden = sec.id !== targetId;
    });
    navLinks.forEach(function (a) {
      var active = a.getAttribute('href') === '#' + targetId;
      a.classList.toggle('active', active);
      a.setAttribute('aria-current', active ? 'page' : 'false');
    });
    history.replaceState(null, '', '#' + targetId);
  }

  navLinks.forEach(function (a) {
    a.addEventListener('click', function (e) {
      var href = a.getAttribute('href');
      // Only intercept simple section tab links (no sub-paths)
      if (href && href.startsWith('#') && href.indexOf('/') === -1) {
        e.preventDefault();
        showSection(href.slice(1));
      }
    });
  });

  // -------------------------------------------------------------------------
  // 4. Live search
  // -------------------------------------------------------------------------

  function injectSearch(tableId, placeholder) {
    var table = document.getElementById(tableId);
    if (!table) return;

    var wrap = document.createElement('div');
    wrap.className = 'search-wrap';
    var input = document.createElement('input');
    input.type = 'search';
    input.placeholder = placeholder || 'Filter…';
    input.setAttribute('aria-label', placeholder || 'Filter rows');
    wrap.appendChild(input);

    // Insert above any .table-scroll wrapper, not inside it
    var parent = table.parentNode;
    var insertBefore = (parent.classList && parent.classList.contains('table-scroll'))
      ? parent : table;
    insertBefore.parentNode.insertBefore(wrap, insertBefore);

    var tbody = table.querySelector('tbody');
    var noResultsRow = null;

    function updateNoResults() {
      var allHidden = Array.from(tbody.rows).every(function (row) {
        return row.classList.contains('hidden-row') || row === noResultsRow;
      });
      if (allHidden && !noResultsRow) {
        noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results-row';
        noResultsRow.innerHTML = '<td colspan="10" class="no-results-msg">No matching results.</td>';
        tbody.appendChild(noResultsRow);
      } else if (!allHidden && noResultsRow) {
        tbody.removeChild(noResultsRow);
        noResultsRow = null;
      }
    }

    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      Array.from(tbody.rows).forEach(function (row) {
        if (row === noResultsRow) return;
        row.classList.toggle('hidden-row', q.length > 0 && !row.textContent.toLowerCase().includes(q));
      });
      updateNoResults();
    });
  }

  injectSearch('concepts-table',  'Search concepts…');
  injectSearch('relations-table', 'Search relations…');
  injectSearch('documents-table', 'Search documents…');

  // -------------------------------------------------------------------------
  // Shared helpers
  // -------------------------------------------------------------------------

  function esc(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderPage(html, activeHref) {
    sections.forEach(function (sec) { sec.hidden = true; });
    navLinks.forEach(function (a) {
      var active = a.getAttribute('href') === activeHref;
      a.classList.toggle('active', active);
      a.setAttribute('aria-current', active ? 'page' : 'false');
    });
    detailPage.innerHTML = html;
    detailPage.hidden = false;
    window.scrollTo(0, 0);
  }

  function backBtn(href, label) {
    return '<a href="' + href + '" class="back-btn">&#8592; ' + esc(label) + '</a>';
  }

  function predBadge(pred) {
    return '<span class="predicate predicate-' + esc(pred) + '">' + esc(pred) + '</span>';
  }

  // -------------------------------------------------------------------------
  // 5. Concept detail page
  // -------------------------------------------------------------------------

  function showConceptPage(id) {
    var concept = conceptIndex[id];
    if (!concept) {
      renderPage(
        backBtn('#concepts', 'All concepts') +
        '<p class="muted" style="margin-top:1rem">Concept not found: ' + esc(id) + '</p>',
        '#concepts'
      );
      return;
    }

    var aliases = (concept.aliases || []).join(', ') || '—';

    // Related concepts with predicate badges
    var relatedItems = concept.related || [];
    var relatedHtml = relatedItems.length
      ? '<ul class="dp-list">' + relatedItems.map(function (item) {
          var rid    = typeof item === 'object' ? item.id  : item;
          var rel    = typeof item === 'object' ? item.rel : 'relatedTerm';
          var rlabel = (conceptIndex[rid] && conceptIndex[rid].label) || rid.replace(/-/g, '\u2011');
          var badge  = rel !== 'relatedTerm'
            ? ' <span class="pred-badge pred-' + esc(rel) + '">' + esc(rel) + '</span>'
            : '';
          return '<li><a href="#concept/' + encodeURIComponent(rid) + '">' + esc(rlabel) + '</a>' + badge + '</li>';
        }).join('') + '</ul>'
      : '<span class="muted">—</span>';

    // Outgoing / incoming relations from the full relation list
    var outgoing = relationList.filter(function (r) { return r.from_id === id; });
    var incoming = relationList.filter(function (r) { return r.to_id   === id; });

    function edgeLink(r) {
      return ' <a href="#relation/' +
        encodeURIComponent(r.from_id) + '/' +
        encodeURIComponent(r.predicate) + '/' +
        encodeURIComponent(r.to_id) +
        '" class="edge-link" title="View relation detail">&nearr;</a>';
    }

    var outHtml = outgoing.length
      ? '<ul class="dp-list">' + outgoing.map(function (r) {
          return '<li>' + predBadge(r.predicate) + ' <a href="#concept/' + encodeURIComponent(r.to_id) + '">' + esc(r.to_label) + '</a>' + edgeLink(r) + '</li>';
        }).join('') + '</ul>'
      : '<span class="muted">—</span>';

    var inHtml = incoming.length
      ? '<ul class="dp-list">' + incoming.map(function (r) {
          return '<li><a href="#concept/' + encodeURIComponent(r.from_id) + '">' + esc(r.from_label) + '</a> ' + predBadge(r.predicate) + edgeLink(r) + '</li>';
        }).join('') + '</ul>'
      : '<span class="muted">—</span>';

    var docsHtml = (concept.docs || []).length
      ? '<ul class="dp-list">' + concept.docs.map(function (f) {
          return '<li><code>' + esc(f.replace(/^.*\//, '')) + '</code></li>';
        }).join('') + '</ul>'
      : '<span class="muted">—</span>';

    var html =
      backBtn('#concepts', 'All concepts') +
      '<article class="dp-content">' +
        '<header class="dp-header">' +
          '<h2>' + esc(concept.label) + '</h2>' +
          (concept.domain ? '<span class="badge">' + esc(concept.domain) + '</span>' : '') +
        '</header>' +

        (concept.comment
          ? '<section class="dp-section"><h3>Definition</h3><p>' + esc(concept.comment) + '</p></section>'
          : '') +

        '<section class="dp-section"><h3>Aliases</h3><p>' + esc(aliases) + '</p></section>' +
        '<section class="dp-section"><h3>Related concepts</h3>' + relatedHtml + '</section>' +

        (outgoing.length
          ? '<section class="dp-section"><h3>Outgoing relations (' + outgoing.length + ')</h3>' + outHtml + '</section>'
          : '') +
        (incoming.length
          ? '<section class="dp-section"><h3>Incoming relations (' + incoming.length + ')</h3>' + inHtml + '</section>'
          : '') +

        '<section class="dp-section"><h3>Source documents</h3>' + docsHtml + '</section>' +
      '</article>';

    history.replaceState(null, '', '#concept/' + encodeURIComponent(id));
    renderPage(html, '#concepts');
  }

  // -------------------------------------------------------------------------
  // 6. Relation detail page
  // -------------------------------------------------------------------------

  function showRelationPage(fromId, predicate, toId) {
    var fromConcept = conceptIndex[fromId];
    var toConcept   = conceptIndex[toId];
    var fromLabel   = fromConcept ? fromConcept.label : fromId;
    var toLabel     = toConcept   ? toConcept.label   : toId;

    function conceptCard(concept, id) {
      if (!concept) {
        return '<div class="rel-card rel-card--missing"><span class="muted">' + esc(id) + '</span></div>';
      }
      var snippet = concept.comment
        ? esc(concept.comment.slice(0, 200)) + (concept.comment.length > 200 ? '…' : '')
        : '';
      return '<div class="rel-card">' +
        '<a href="#concept/' + encodeURIComponent(concept.id) + '" class="rel-card-title">' + esc(concept.label) + '</a>' +
        (concept.domain ? ' <span class="badge">' + esc(concept.domain) + '</span>' : '') +
        (snippet ? '<p class="rel-card-def">' + snippet + '</p>' : '') +
      '</div>';
    }

    // Other edges with the same predicate type
    var sameType = relationList.filter(function (r) {
      return r.predicate === predicate && !(r.from_id === fromId && r.to_id === toId);
    });
    var sameTypeHtml = sameType.length
      ? '<ul class="dp-list">' + sameType.map(function (r) {
          return '<li>' +
            '<a href="#concept/' + encodeURIComponent(r.from_id) + '">' + esc(r.from_label) + '</a>' +
            ' ' + predBadge(r.predicate) + ' ' +
            '<a href="#concept/' + encodeURIComponent(r.to_id) + '">' + esc(r.to_label) + '</a>' +
          '</li>';
        }).join('') + '</ul>'
      : '<span class="muted">No other relations with this predicate.</span>';

    var html =
      backBtn('#relations', 'All relations') +
      '<article class="dp-content">' +
        '<header class="dp-header">' +
          '<h2>' + esc(fromLabel) + ' ' + predBadge(predicate) + ' ' + esc(toLabel) + '</h2>' +
        '</header>' +

        '<section class="dp-section rel-pair">' +
          '<div class="rel-pair-col"><h3>From</h3>' + conceptCard(fromConcept, fromId) + '</div>' +
          '<div class="rel-pair-arrow">' + predBadge(predicate) + '</div>' +
          '<div class="rel-pair-col"><h3>To</h3>' + conceptCard(toConcept, toId) + '</div>' +
        '</section>' +

        '<section class="dp-section">' +
          '<h3>Other &ldquo;' + esc(predicate) + '&rdquo; relations (' + sameType.length + ')</h3>' +
          sameTypeHtml +
        '</section>' +
      '</article>';

    history.replaceState(null, '', '#relation/' + encodeURIComponent(fromId) + '/' + encodeURIComponent(predicate) + '/' + encodeURIComponent(toId));
    renderPage(html, '#relations');
  }

  // -------------------------------------------------------------------------
  // 7. Row click bindings
  // -------------------------------------------------------------------------

  // Concept rows — navigate to concept detail page
  document.querySelectorAll('tr.concept-row').forEach(function (row) {
    row.addEventListener('click', function (e) {
      if (e.target.closest('a')) return;
      var id = row.getAttribute('data-id');
      if (id) location.hash = '#concept/' + encodeURIComponent(id);
    });
    row.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        var id = row.getAttribute('data-id');
        if (id) location.hash = '#concept/' + encodeURIComponent(id);
      }
    });
  });

  // Relation rows — navigate to relation detail page
  document.querySelectorAll('tr.relation-row').forEach(function (row) {
    row.addEventListener('click', function (e) {
      if (e.target.closest('a')) return;
      var fromId    = row.getAttribute('data-from');
      var predicate = row.getAttribute('data-pred');
      var toId      = row.getAttribute('data-to');
      if (fromId && predicate && toId) {
        location.hash = '#relation/' + encodeURIComponent(fromId) + '/' + encodeURIComponent(predicate) + '/' + encodeURIComponent(toId);
      }
    });
    row.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        row.click();
      }
    });
  });

  // -------------------------------------------------------------------------
  // Initial route
  // -------------------------------------------------------------------------

  route();

})();

