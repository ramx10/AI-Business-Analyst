// ─── Compare Page Logic ───────────────────────────────────────

function computeStats(headers, rows) {
  const colCount = headers.length;
  const rowCount = rows.length;
  const missing = {};
  const colTypes = {};
  const numericData = {};

  headers.forEach(h => {
    missing[h] = 0;
    colTypes[h] = 'other';
    numericData[h] = [];
  });

  rows.forEach(row => {
    headers.forEach((h, i) => {
      const val = row[i];
      if (val === null || val === undefined || val === '' || val === 'NA' || val === 'N/A') {
        missing[h]++;
      } else {
        const num = parseFloat(val);
        if (!isNaN(num) && val.trim() !== '') {
          numericData[h].push(num);
          if (colTypes[h] === 'other') colTypes[h] = 'numeric';
        } else {
          if (colTypes[h] === 'other') colTypes[h] = 'categorical';
        }
      }
    });
  });

  const numericSummary = {};
  headers.forEach(h => {
    const vals = numericData[h];
    if (vals.length > 1) {
      const sorted = [...vals].sort((a, b) => a - b);
      const sum = vals.reduce((s, v) => s + v, 0);
      numericSummary[h] = {
        count: vals.length,
        mean: round(sum / vals.length),
        std: round(Math.sqrt(vals.reduce((sq, v) => sq + (v - sum / vals.length) ** 2, 0) / (vals.length - 1))),
        min: round(sorted[0]),
        q1: round(sorted[Math.floor(sorted.length * 0.25)]),
        median: round(sorted[Math.floor(sorted.length * 0.5)]),
        q3: round(sorted[Math.floor(sorted.length * 0.75)]),
        max: round(sorted[sorted.length - 1]),
      };
    }
  });

  const seen = new Set();
  let dupCount = 0;
  rows.forEach(row => {
    const key = row.join('|');
    if (seen.has(key)) dupCount++;
    else seen.add(key);
  });

  return { colCount, rowCount, missing, colTypes, numericSummary, duplicateRows: dupCount, columns: headers };
}

function round(v) {
  return Math.round(v * 100) / 100;
}

function renderComparison(statsA, statsB) {
  const root = document.getElementById('compare-results');
  root.style.display = 'block';
  root.innerHTML = '';

  // ─── Summary Cards ───────────────────────────────────────────
  const rowDiff = statsB.rowCount - statsA.rowCount;
  const rowDiffStr = rowDiff >= 0 ? `+${rowDiff}` : `${rowDiff}`;
  const rowDiffClass = rowDiff >= 0 ? 'green' : 'red';

  const colsA = new Set(statsA.columns);
  const colsB = new Set(statsB.columns);
  const inANotB = statsA.columns.filter(c => !colsB.has(c));
  const inBNotA = statsB.columns.filter(c => !colsA.has(c));
  const commonCols = statsA.columns.filter(c => colsB.has(c));

  const colDiffA = inANotB.length;
  const colDiffB = inBNotA.length;

  const missA = Object.values(statsA.missing).reduce((s, v) => s + v, 0);
  const missB = Object.values(statsB.missing).reduce((s, v) => s + v, 0);

  const dupA = statsA.duplicateRows;
  const dupB = statsB.duplicateRows;

  root.innerHTML = `
    <div class="section">
      <div class="section-header"><div class="section-title">Comparison Summary</div></div>
      <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);">
        <div class="kpi-card">
          <div class="kpi-label">Row Count Diff</div>
          <div class="kpi-value" style="color:var(--${rowDiffClass});">${rowDiffStr}</div>
          <div class="kpi-trend ${rowDiff >= 0 ? 'up' : 'down'}">A: ${statsA.rowCount.toLocaleString()} → B: ${statsB.rowCount.toLocaleString()}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Column Diff</div>
          <div class="kpi-value">${inANotB.length + inBNotA.length}</div>
          <div class="kpi-trend up">${inANotB.length} in A only · ${inBNotA.length} in B only</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Missing Values</div>
          <div class="kpi-value">${missA.toLocaleString()} / ${missB.toLocaleString()}</div>
          <div class="kpi-trend up">A / B total missing</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Duplicate Rows</div>
          <div class="kpi-value">${dupA.toLocaleString()} / ${dupB.toLocaleString()}</div>
          <div class="kpi-trend up">A / B total duplicates</div>
        </div>
      </div>
    </div>
  `;

  // ─── Column Differences ─────────────────────────────────────
  if (inANotB.length > 0 || inBNotA.length > 0) {
    root.innerHTML += `
      <div class="section">
        <div class="section-header"><div class="section-title">Column Differences</div></div>
        <div class="grid-2">
          ${inANotB.length > 0 ? `
            <div class="card">
              <div class="card-header"><div class="card-title">In A but not B (${inANotB.length})</div></div>
              <div class="card-body"><div style="display:flex;flex-wrap:wrap;gap:6px;">${inANotB.map(c => `<span class="chip chip-blue">${c}</span>`).join('')}</div></div>
            </div>
          ` : ''}
          ${inBNotA.length > 0 ? `
            <div class="card">
              <div class="card-header"><div class="card-title">In B but not A (${inBNotA.length})</div></div>
              <div class="card-body"><div style="display:flex;flex-wrap:wrap;gap:6px;">${inBNotA.map(c => `<span class="chip chip-orange">${c}</span>`).join('')}</div></div>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  // ─── Common Columns — Missing Values Comparison ──────────────
  const missHtml = commonCols.map(col => {
    const mA = statsA.missing[col] || 0;
    const mB = statsB.missing[col] || 0;
    const pctA = statsA.rowCount ? round((mA / statsA.rowCount) * 100) : 0;
    const pctB = statsB.rowCount ? round((mB / statsB.rowCount) * 100) : 0;
    return `<tr><td>${col}</td><td>${mA.toLocaleString()} (${pctA}%)</td><td>${mB.toLocaleString()} (${pctB}%)</td></tr>`;
  }).join('');

  if (commonCols.length > 0) {
    root.innerHTML += `
      <div class="section">
        <div class="section-header"><div class="section-title">Missing Values by Column</div></div>
        <div class="card">
          <div class="table-wrap">
            <table>
              <thead><tr><th>Column</th><th>Dataset A</th><th>Dataset B</th></tr></thead>
              <tbody>${missHtml}</tbody>
            </table>
          </div>
        </div>
      </div>
    `;
  }

  // ─── Numeric Stats Side-by-Side ──────────────────────────────
  const numCols = Object.keys(statsA.numericSummary).filter(c => statsB.numericSummary[c]);
  if (numCols.length > 0) {
    const statFields = ['count', 'mean', 'std', 'min', 'q1', 'median', 'q3', 'max'];
    const tableRows = numCols.map(col => {
      const sA = statsA.numericSummary[col];
      const sB = statsB.numericSummary[col];
      const cells = statFields.map(f => `<td>${sA[f]}</td><td>${sB[f]}</td>`).join('');
      return `<tr><td style="font-weight:600;white-space:nowrap;">${col}</td>${cells}</tr>`;
    }).join('');
    root.innerHTML += `
      <div class="section">
        <div class="section-header"><div class="section-title">Numeric Statistics (Common Columns)</div></div>
        <div class="card">
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Column</th>
                  <th colspan="2">Count</th>
                  <th colspan="2">Mean</th>
                  <th colspan="2">Std</th>
                  <th colspan="2">Min</th>
                  <th colspan="2">Q1</th>
                  <th colspan="2">Median</th>
                  <th colspan="2">Q3</th>
                  <th colspan="2">Max</th>
                </tr>
                <tr style="font-size:10px;color:var(--text-tertiary);">
                  <th></th>
                  <th>A</th><th>B</th>
                  <th>A</th><th>B</th>
                  <th>A</th><th>B</th>
                  <th>A</th><th>B</th>
                  <th>A</th><th>B</th>
                  <th>A</th><th>B</th>
                  <th>A</th><th>B</th>
                  <th>A</th><th>B</th>
                </tr>
              </thead>
              <tbody>${tableRows}</tbody>
            </table>
          </div>
        </div>
      </div>
    `;
  }

  // ─── Data Preview Side-by-Side ──────────────────────────────
  const previewA = statsA._rawPreview || [];
  const previewB = statsB._rawPreview || [];
  const previewCols = [...new Set([...statsA.columns, ...statsB.columns])];

  const maxPreview = Math.min(10, previewA.length, previewB.length);
  if (maxPreview > 0) {
    const aRows = previewA.slice(0, maxPreview).map(r =>
      `<tr>${previewCols.map(c => `<td>${r[c] ?? ''}</td>`).join('')}</tr>`
    ).join('');
    const bRows = previewB.slice(0, maxPreview).map(r =>
      `<tr>${previewCols.map(c => `<td>${r[c] ?? ''}</td>`).join('')}</tr>`
    ).join('');
    const headers = previewCols.map(c => `<th>${c}</th>`).join('');

    root.innerHTML += `
      <div class="section">
        <div class="section-header"><div class="section-title">Data Preview (side-by-side)</div></div>
        <div class="grid-2">
          <div class="card">
            <div class="card-header"><div class="card-title">Dataset A</div><div class="card-subtitle">${statsA.rowCount.toLocaleString()} rows</div></div>
            <div class="table-wrap"><table><thead><tr>${headers}</tr></thead><tbody>${aRows}</tbody></table></div>
          </div>
          <div class="card">
            <div class="card-header"><div class="card-title">Dataset B</div><div class="card-subtitle">${statsB.rowCount.toLocaleString()} rows</div></div>
            <div class="table-wrap"><table><thead><tr>${headers}</tr></thead><tbody>${bRows}</tbody></table></div>
          </div>
        </div>
      </div>
    `;
  }

  // ─── Download Report Button ──────────────────────────────────
  root.innerHTML += `
    <div style="margin-top:16px;display:flex;gap:8px;">
      <button id="btn-download-report" class="btn btn-primary">Download Comparison Report</button>
    </div>
  `;

  document.getElementById('btn-download-report').addEventListener('click', () => downloadReport(statsA, statsB));
}

function downloadReport(statsA, statsB) {
  const colsA = new Set(statsA.columns);
  const colsB = new Set(statsB.columns);
  const inANotB = statsA.columns.filter(c => !colsB.has(c));
  const inBNotA = statsB.columns.filter(c => !colsA.has(c));
  const missA = Object.values(statsA.missing).reduce((s, v) => s + v, 0);
  const missB = Object.values(statsB.missing).reduce((s, v) => s + v, 0);

  let md = `# Dataset Comparison Report\n\n`;
  md += `## Overview\n\n`;
  md += `| Metric | Dataset A | Dataset B |\n`;
  md += `|---|---|---|\n`;
  md += `| Rows | ${statsA.rowCount.toLocaleString()} | ${statsB.rowCount.toLocaleString()} |\n`;
  md += `| Columns | ${statsA.colCount} | ${statsB.colCount} |\n`;
  md += `| Missing Values | ${missA.toLocaleString()} | ${missB.toLocaleString()} |\n`;
  md += `| Duplicate Rows | ${statsA.duplicateRows.toLocaleString()} | ${statsB.duplicateRows.toLocaleString()} |\n`;
  md += `| Columns in A only | ${inANotB.join(', ') || 'none'} |\n`;
  md += `| Columns in B only | ${inBNotA.join(', ') || 'none'} |\n\n`;

  const commonCols = statsA.columns.filter(c => colsB.has(c));
  if (commonCols.length > 0) {
    md += `## Missing Values by Column\n\n`;
    md += `| Column | A | B |\n|---|---|---|\n`;
    commonCols.forEach(col => {
      const mA = statsA.missing[col] || 0;
      const mB = statsB.missing[col] || 0;
      md += `| ${col} | ${mA.toLocaleString()} | ${mB.toLocaleString()} |\n`;
    });
    md += '\n';
  }

  const numCols = Object.keys(statsA.numericSummary).filter(c => statsB.numericSummary[c]);
  if (numCols.length > 0) {
    md += `## Numeric Statistics\n\n`;
    numCols.forEach(col => {
      const sA = statsA.numericSummary[col];
      const sB = statsB.numericSummary[col];
      md += `### ${col}\n\n`;
      md += `| Stat | A | B |\n|---|---|---|\n`;
      Object.keys(sA).forEach(k => {
        md += `| ${k} | ${sA[k]} | ${sB[k]} |\n`;
      });
      md += '\n';
    });
  }

  const blob = new Blob([md], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'comparison_report.md';
  a.click();
  URL.revokeObjectURL(url);
}

function parseCSV(text) {
  const lines = text.split(/\r?\n/).filter(l => l.trim() !== '');
  if (!lines.length) return { headers: [], rows: [] };
  const headers = parseCSVLine(lines[0]);
  const rows = lines.slice(1).map(line => parseCSVLine(line));
  return { headers, rows };
}

function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"') {
        if (i + 1 < line.length && line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        current += ch;
      }
    } else {
      if (ch === '"') {
        inQuotes = true;
      } else if (ch === ',') {
        result.push(current.trim());
        current = '';
      } else {
        current += ch;
      }
    }
  }
  result.push(current.trim());
  return result;
}

function renderTable(el, headers, rows, label) {
  const hCells = headers.map(h => `<th>${h}</th>`).join('');
  const rHtml = rows.slice(0, 20).map(r =>
    `<tr>${headers.map(h => `<td>${r[h] ?? ''}</td>`).join('')}</tr>`
  ).join('');
  el.innerHTML = `
    <div class="section">
      <div class="section-header"><div class="section-title">${label}</div></div>
      <div class="card">
        <div class="table-wrap"><table><thead><tr>${hCells}</tr></thead><tbody>${rHtml}</tbody></table></div>
      </div>
    </div>
  `;
}

// ─── Main Init ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  const root = document.getElementById('compare-root');
  const statusEl = document.getElementById('compare-status');
  const uploadB = document.getElementById('upload-b');
  const resultsEl = document.getElementById('compare-results');
  const zoneB = document.getElementById('upload-zone-b');
  const fileInputB = document.getElementById('file-input-b');

  let statsA = null;
  let headersA = [];
  let rowsA = [];

  // Load Dataset A stats from API
  const sid = Session.require();
  if (!sid) return;

  try {
    const schemaRes = await API.get(`/api/schema?session_id=${sid}`);
    const previewRes = await API.get(`/api/dataset/stats?session_id=${sid}`);

    headersA = previewRes.column_names || schemaRes.schema?.columns?.map(c => c.name) || [];
    rowsA = previewRes.preview || [];

    statsA = computeStats(headersA, rowsA);
    statsA._rawPreview = rowsA;

    showAlert(statusEl, 'success', `Dataset A loaded — ${statsA.rowCount.toLocaleString()} rows, ${statsA.colCount} columns.`);
    uploadB.style.display = 'block';

    // Show dataset A preview
    renderTable(root, headersA, rowsA, 'Dataset A');
  } catch (e) {
    showAlert(statusEl, 'danger', 'Failed to load dataset A: ' + e.message);
    return;
  }

  // Handle file upload for dataset B
  zoneB.addEventListener('dragover', e => { e.preventDefault(); zoneB.classList.add('drag-over'); });
  zoneB.addEventListener('dragleave', () => zoneB.classList.remove('drag-over'));
  zoneB.addEventListener('drop', e => {
    e.preventDefault(); zoneB.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFileB(file);
  });
  zoneB.addEventListener('click', () => fileInputB.click());
  fileInputB.addEventListener('change', () => { if (fileInputB.files[0]) handleFileB(fileInputB.files[0]); });

  async function handleFileB(file) {
    showAlert(statusEl, 'info', `Reading ${file.name}…`);
    try {
      const text = await file.text();
      const parsed = parseCSV(text);
      if (parsed.headers.length === 0 || parsed.rows.length === 0) {
        showAlert(statusEl, 'danger', 'CSV appears empty or invalid.');
        return;
      }

      const headersB = parsed.headers;
      const rowsB = parsed.rows.map(r => {
        const obj = {};
        headersB.forEach((h, i) => { obj[h] = r[i] || ''; });
        return obj;
      });

      const statsB = computeStats(headersB, parsed.rows);
      statsB._rawPreview = rowsB;

      showAlert(statusEl, 'success', `Dataset B loaded — ${statsB.rowCount.toLocaleString()} rows, ${statsB.colCount} columns.`);

      // Show B preview
      const bPreview = document.getElementById('compare-b-preview') || document.createElement('div');
      bPreview.id = 'compare-b-preview';
      if (!bPreview.parentNode) uploadB.parentNode.insertBefore(bPreview, uploadB.nextSibling);
      renderTable(bPreview, headersB, rowsB, 'Dataset B');

      resultsEl.style.display = 'none';
      renderComparison(statsA, statsB);
      resultsEl.scrollIntoView({ behavior: 'smooth' });
    } catch (e) {
      showAlert(statusEl, 'danger', 'Failed to read file: ' + e.message);
    }
  }
});
