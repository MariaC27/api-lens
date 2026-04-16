# ABOUTME: Self-contained HTML viewer for comparing OpenAPI snapshots.
# ABOUTME: Served as a single page at GET / with no external dependencies.

VIEWER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ApiLens — API Diff</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #fafafa; color: #3b4151; }
    header { background: #1b1b1b; padding: 16px 24px; }
    header h1 { margin: 0; font-size: 20px; color: #fff; }
    header p { margin: 4px 0 0; font-size: 13px; color: #999; }
    .controls { background: #fff; border-bottom: 1px solid #e8e8e8; padding: 20px 24px; display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-end; }
    .field-group { display: flex; flex-direction: column; gap: 4px; }
    label { font-size: 12px; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    select { padding: 8px 12px; border: 1px solid #d0d0d0; border-radius: 4px; font-size: 13px; min-width: 320px; background: #fff; }
    .compare-btn { padding: 9px 20px; background: #4990e2; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600; }
    .compare-btn:hover { background: #357abd; }
    .results { padding: 24px; max-width: 1300px; margin: 0 auto; }
    .empty { color: #999; text-align: center; padding: 60px 0; font-size: 15px; }
    .summary { display: flex; gap: 6px; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }
    .filter-btn { padding: 4px 12px; border: 1px solid; border-radius: 4px; background: #fff; font-size: 12px; font-weight: 600; cursor: pointer; }
    .filter-btn[data-filter="all"]     { color: #1a6bbf; border-color: #4990e2; }
    .filter-btn[data-filter="new"]     { color: #1e7e34; border-color: #49cc90; }
    .filter-btn[data-filter="removed"] { color: #c62828; border-color: #f93e3e; }
    .filter-btn[data-filter="modified"]{ color: #c05621; border-color: #fca130; }
    .filter-btn[data-filter="all"].active      { background: #4990e2; color: #fff; }
    .filter-btn[data-filter="new"].active      { background: #49cc90; color: #fff; }
    .filter-btn[data-filter="removed"].active  { background: #f93e3e; color: #fff; }
    .filter-btn[data-filter="modified"].active { background: #fca130; color: #fff; }
    .section.hidden { display: none; }
    .section-empty { color: #aaa; font-size: 13px; padding: 8px 0; margin: 0; }
    .section-title { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #888; margin: 20px 0 6px; }
    .endpoint { background: #fff; border: 1px solid #e8e8e8; border-radius: 4px; margin-bottom: 6px; overflow: hidden; }
    .endpoint-header { padding: 10px 16px; display: flex; align-items: center; gap: 12px; cursor: pointer; user-select: none; }
    .endpoint-header:hover { background: #f9f9f9; }
    .endpoint.collapsible .endpoint-header::before { content: '›'; font-size: 18px; line-height: 1; color: #aaa; flex-shrink: 0; display: inline-block; transform: rotate(90deg); }
    .endpoint.collapsible.collapsed .endpoint-header::before { transform: rotate(0deg); }
    .endpoint.collapsed .changes { display: none; }
    .method { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 3px; color: #fff; min-width: 58px; text-align: center; text-transform: uppercase; }
    .get { background: #61affe; } .post { background: #49cc90; } .put { background: #fca130; }
    .patch { background: #50e3c2; color: #fff; } .delete { background: #f93e3e; }
    .path { font-family: monospace; font-size: 14px; }
    .badge { font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 10px; }
    .endpoint-right { margin-left: auto; display: flex; gap: 8px; align-items: center; }
    .badge-new { background: #e6f4ea; color: #1e7e34; }
    .badge-removed { background: #fce8e8; color: #c62828; }
    .badge-modified { background: #fff8e1; color: #f57c00; }
    .changes { border-top: 1px solid #f0f0f0; padding: 8px 0 4px; }
    .change-location { font-size: 11px; color: #999; font-weight: 600; text-transform: uppercase; padding: 4px 16px 2px; letter-spacing: 0.5px; }
    .field-row { padding: 3px 16px; font-family: monospace; font-size: 13px; }
    .field-row.added { background: #f0fff4; color: #276749; }
    .field-row.removed { background: #fff5f5; color: #c53030; }
    .ai-btn { padding: 3px 10px; border: 1px solid #bbb; border-radius: 4px; background: #fff; font-size: 11px; font-weight: 600; cursor: pointer; color: #666; white-space: nowrap; flex-shrink: 0; }
    .ai-btn:hover { background: #f0f0f0; border-color: #999; color: #333; }
    .ai-btn-top { padding: 5px 14px; border: 1px solid #bbb; border-radius: 4px; background: #fff; font-size: 12px; font-weight: 600; cursor: pointer; color: #666; white-space: nowrap; margin-left: auto; }
    .ai-btn-top:hover { background: #f0f0f0; border-color: #999; color: #333; }
  </style>
</head>
<body>
  <header>
    <h1>ApiLens</h1>
    <p>Compare OpenAPI snapshots to see what changed between deploys</p>
  </header>
  <div class="controls">
    <div class="field-group">
      <label>Base (older)</label>
      <select id="base"></select>
    </div>
    <div class="field-group">
      <label>Head (newer)</label>
      <select id="head"></select>
    </div>
    <button class="compare-btn" onclick="compare()">Compare</button>
  </div>
  <div class="results" id="results">
    <p class="empty">Select two snapshots above and click Compare.</p>
  </div>
  <script>
    const BASE = window.location.origin + window.location.pathname.replace(/\\/?$/, '/');

    async function loadSnapshots() {
      const res = await fetch(BASE + 'snapshots');
      const snapshots = await res.json();
      ['base', 'head'].forEach(id => {
        const sel = document.getElementById(id);
        snapshots.forEach(s => {
          const opt = document.createElement('option');
          opt.value = s.filename;
          const date = new Date(s.timestamp).toLocaleString();
          const msg = s.commit_message.split('\\n')[0].slice(0, 60);
          opt.text = date + ' — ' + msg;
          sel.appendChild(opt);
        });
      });
      // head = newest (index 0), base = second newest (index 1)
      document.getElementById('head').selectedIndex = 0;
      document.getElementById('base').selectedIndex = snapshots.length > 1 ? 1 : 0;
      updateHeadOptions();
      document.getElementById('base').addEventListener('change', updateHeadOptions);
    }

    function updateHeadOptions() {
      const baseSel = document.getElementById('base');
      const headSel = document.getElementById('head');
      const baseIdx = baseSel.selectedIndex;
      Array.from(headSel.options).forEach((opt, i) => {
        opt.disabled = i >= baseIdx;
      });
      if (headSel.selectedIndex >= baseIdx) {
        headSel.selectedIndex = baseIdx > 0 ? 0 : -1;
      }
    }

    async function compare() {
      const base = document.getElementById('base').value;
      const head = document.getElementById('head').value;
      if (!base || !head) return;
      document.getElementById('results').innerHTML = '<p class="empty">Loading...</p>';
      try {
        const res = await fetch(BASE + 'compare?base=' + encodeURIComponent(base) + '&head=' + encodeURIComponent(head));
        if (!res.ok) throw new Error(await res.text());
        renderDiff(await res.json());
      } catch (e) {
        document.getElementById('results').innerHTML = '<p class="empty">Error: ' + e.message + '</p>';
      }
    }

    let currentDiff = null;

    function buildTopLevelPrompt(diff) {
      var lines = ['The backend API has changed. Update TypeScript types and data-fetching code accordingly.', ''];
      if (diff.new_endpoints.length) {
        lines.push('## New Endpoints');
        diff.new_endpoints.forEach(function(ep) { lines.push('  + ' + ep.method + ' ' + ep.path); });
        lines.push('');
      }
      if (diff.missing_endpoints.length) {
        lines.push('## Removed Endpoints');
        diff.missing_endpoints.forEach(function(ep) { lines.push('  - ' + ep.method + ' ' + ep.path); });
        lines.push('');
      }
      if (diff.modified_endpoints.length) {
        lines.push('## Modified Endpoints');
        diff.modified_endpoints.forEach(function(ep) {
          ep.changes.forEach(function(c) {
            lines.push('');
            lines.push('  ' + ep.method + ' ' + ep.path + ' (' + c.location + ')');
            c.fields.filter(function(f) { return f.status !== 'unchanged'; }).forEach(function(f) {
              lines.push('    ' + (f.status === 'added' ? '+ ' : '- ') + f.name);
            });
          });
        });
        lines.push('');
      }
      lines.push('---');
      if (diff.new_endpoints.length) lines.push('For new endpoints: add TypeScript types and implement client-side fetching.');
      if (diff.missing_endpoints.length) lines.push('For removed endpoints: remove or update all code that calls them.');
      if (diff.modified_endpoints.length) lines.push('For modified endpoints: update the TypeScript response type and any component or hook that reads from it.');
      return lines.join('\\n');
    }

    function buildEndpointPrompt(ep) {
      var lines = [
        'The following API endpoint response has changed.',
        'Update the TypeScript type and any component or hook that calls it.',
        '',
        ep.method + ' ' + ep.path,
        ''
      ];
      ep.changes.forEach(function(c) {
        lines.push(c.location + ':');
        c.fields.forEach(function(f) {
          var sym = f.status === 'added' ? '+ ' : f.status === 'removed' ? '- ' : '  ';
          lines.push('  ' + sym + f.name);
        });
        lines.push('');
      });
      return lines.join('\\n');
    }

    function copyToClipboard(text, btn) {
      navigator.clipboard.writeText(text).then(function() {
        var orig = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(function() { btn.textContent = orig; }, 1500);
      });
    }

    function setFilter(type) {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.toggle('active', b.dataset.filter === type));
      document.querySelectorAll('.section').forEach(s => {
        const isMatch = type === 'all' ? true : s.dataset.section === type;
        s.classList.toggle('hidden', !isMatch || (type === 'all' && s.dataset.empty === 'true'));
      });
    }

    function renderDiff(diff) {
      currentDiff = diff;
      const total = diff.new_endpoints.length + diff.missing_endpoints.length + diff.modified_endpoints.length;
      if (total === 0) {
        document.getElementById('results').innerHTML = '<p class="empty">No API changes detected between these snapshots.</p>';
        return;
      }

      const allCount = total;
      let html = '<div class="summary">'
        + '<button class="filter-btn active" data-filter="all">All (' + allCount + ')</button>'
        + '<button class="filter-btn" data-filter="new">New (' + diff.new_endpoints.length + ')</button>'
        + '<button class="filter-btn" data-filter="removed">Removed (' + diff.missing_endpoints.length + ')</button>'
        + '<button class="filter-btn" data-filter="modified">Modified (' + diff.modified_endpoints.length + ')</button>'
        + '<button class="ai-btn-top" data-action="copy-all">Copy AI Prompt for All</button>'
        + '</div>';

      const e = ' data-empty="true"';
      html += '<div class="section" data-section="new"' + (diff.new_endpoints.length ? '' : e) + '><div class="section-title">New Endpoints</div>';
      html += diff.new_endpoints.length
        ? diff.new_endpoints.map(ep => endpoint(ep.method, ep.path, 'badge-new', 'NEW', [])).join('')
        : '<p class="section-empty">No new endpoints</p>';
      html += '</div>';

      html += '<div class="section" data-section="removed"' + (diff.missing_endpoints.length ? '' : e) + '><div class="section-title">Removed Endpoints</div>';
      html += diff.missing_endpoints.length
        ? diff.missing_endpoints.map(ep => endpoint(ep.method, ep.path, 'badge-removed', 'REMOVED', [])).join('')
        : '<p class="section-empty">No removed endpoints</p>';
      html += '</div>';

      html += '<div class="section" data-section="modified"' + (diff.modified_endpoints.length ? '' : e) + '><div class="section-title">Modified Endpoints</div>';
      html += diff.modified_endpoints.length
        ? diff.modified_endpoints.map((ep, i) => endpoint(ep.method, ep.path, 'badge-modified', 'MODIFIED', ep.changes, i)).join('')
        : '<p class="section-empty">No modified endpoints</p>';
      html += '</div>';
      document.getElementById('results').innerHTML = html;
      setFilter('all');

      const results = document.getElementById('results');
      results.addEventListener('click', function(e) {
        const filterBtn = e.target.closest('.filter-btn');
        if (filterBtn) { setFilter(filterBtn.dataset.filter); return; }

        const aiBtn = e.target.closest('[data-action]');
        if (aiBtn) {
          if (aiBtn.dataset.action === 'copy-all') {
            copyToClipboard(buildTopLevelPrompt(currentDiff), aiBtn);
          } else if (aiBtn.dataset.action === 'copy-endpoint') {
            const idx = parseInt(aiBtn.dataset.idx);
            copyToClipboard(buildEndpointPrompt(currentDiff.modified_endpoints[idx]), aiBtn);
          }
          return;
        }

        const header = e.target.closest('.endpoint-header');
        if (header) header.closest('.endpoint').classList.toggle('collapsed');
      });
    }

    function endpoint(method, path, badgeClass, badgeLabel, changes, copyIdx) {
      const hasChanges = changes.length > 0;
      const collapsible = hasChanges ? ' collapsible' : '';
      const aiBtn = (copyIdx !== undefined)
        ? '<button class="ai-btn" data-action="copy-endpoint" data-idx="' + copyIdx + '">Copy AI Prompt</button>'
        : '';
      const trailingEl = '<div class="endpoint-right">' + aiBtn + '<span class="badge ' + badgeClass + '">' + badgeLabel + '</span></div>';
      const changesHtml = hasChanges ? '<div class="changes">'
        + changes.map(c =>
            '<div class="change-location">' + c.location + '</div>'
            + c.fields.map(f => {
                if (f.status === 'added') return '<div class="field-row added">&#43; ' + f.name + '</div>';
                if (f.status === 'removed') return '<div class="field-row removed">&#8722; ' + f.name + '</div>';
                return '<div class="field-row">&nbsp;&nbsp; ' + f.name + '</div>';
              }).join('')
          ).join('')
        + '</div>' : '';
      return '<div class="endpoint' + collapsible + '"><div class="endpoint-header">'
        + '<span class="method ' + method.toLowerCase() + '">' + method + '</span>'
        + '<span class="path">' + path + '</span>'
        + trailingEl
        + '</div>' + changesHtml + '</div>';
    }

    loadSnapshots();
  </script>
</body>
</html>"""
