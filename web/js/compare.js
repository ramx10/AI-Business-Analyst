function showAlert(el, type, msg) {
  el.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
}

function round(v) {
  return Math.round(v * 100) / 100;
}

function fmtNum(n) {
  if (n === null || n === undefined || isNaN(n)) return '-';
  return Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

document.addEventListener('DOMContentLoaded', async () => {
  const statusEl = document.getElementById('status-area');
  const currentInfo = document.getElementById('current-info');
  const currentDesc = document.getElementById('current-desc');
  const historySection = document.getElementById('history-section');
  const historyList = document.getElementById('history-list');
  const loadingEl = document.getElementById('loading-compare');
  const insightsEl = document.getElementById('compare-insights');
  const insightsBody = document.getElementById('insights-body');
  const metricsEl = document.getElementById('compare-metrics');
  const metricsGrid = document.getElementById('metrics-grid');
  const numericEl = document.getElementById('compare-numeric');
  const numericBody = document.getElementById('numeric-table-body');
  const qualityEl = document.getElementById('compare-data-quality');
  const qualityBody = document.getElementById('quality-table-body');
  const downloadBtn = document.getElementById('btn-download');
  const downloadSection = document.getElementById('download-section');

  let currentStats = null;
  let previousStats = null;
  let insightsText = '';

  const sid = Session.require();
  if (!sid) return;

  // ── Load current dataset info ──────────────────────────────
  try {
    const res = await API.get(`/api/dataset/stats?session_id=${sid}`);
    currentStats = {
      row_count: res.row_count,
      column_count: res.column_count,
      column_info: {},
      numeric_summary: res.numeric_summary || {},
      cat_summary: {},
      missing_values: res.missing_values || {},
      duplicate_rows: res.duplicate_rows,
      columns: res.column_names || [],
      preview: res.preview || [],
    };
    const numNumeric = Object.keys(res.numeric_summary || {}).length;
    const numCategorical = (res.column_names || []).length - numNumeric;
    currentDesc.textContent = `${res.row_count.toLocaleString()} rows · ${res.column_count} columns · ${numNumeric} numeric · ${numCategorical} categorical`;
    currentInfo.style.display = 'block';
  } catch (e) {
    showAlert(statusEl, 'danger', 'Failed to load current dataset: ' + e.message);
    return;
  }

  // ── Load history list ──────────────────────────────────────
  try {
    const histRes = await API.get('/api/compare/history');
    const entries = histRes.history || [];

    // Filter out the current session itself (can't compare with itself)
    const available = entries.filter(e => e.session_id !== sid);

    if (available.length === 0) {
      historyList.innerHTML = `<div style="text-align:center;padding:20px;color:var(--text-secondary);font-size:13px;">
        <div style="margin-bottom:12px;">No previous uploads found in history.</div>
        <button id="btn-save-snapshot" class="btn btn-secondary btn-sm">Save current dataset as snapshot</button>
        <div style="margin-top:8px;font-size:11px;color:var(--text-tertiary);">This will make the current data available for comparison after your next upload.</div>
      </div>`;
      document.getElementById('btn-save-snapshot')?.addEventListener('click', async () => {
        try {
          await API.post('/api/compare/snapshot', { session_id: sid, filename: 'current_snapshot' });
          showAlert(statusEl, 'success', 'Snapshot saved! Upload a new dataset, then return here to compare.');
        } catch (e) {
          showAlert(statusEl, 'danger', 'Failed to save snapshot: ' + e.message);
        }
      });
      showAlert(statusEl, 'info', 'No previous datasets in history. Save a snapshot or upload a new dataset first.');
    } else {
      historyList.innerHTML = available.map((entry, idx) => {
        const date = entry.uploaded_at ? new Date(entry.uploaded_at).toLocaleDateString() : 'unknown';
        const time = entry.uploaded_at ? new Date(entry.uploaded_at).toLocaleTimeString() : '';
        return `
          <div class="history-item" style="display:flex;align-items:center;justify-content:space-between;padding:12px 0;${idx > 0 ? 'border-top:1px solid var(--border-subtle);' : ''}">
            <div class="history-info">
              <div class="history-title" style="font-weight:600;font-size:13px;">${entry.filename}</div>
              <div class="history-meta" style="font-size:11px;color:var(--text-secondary);margin-top:2px;">
                <span>${entry.rows.toLocaleString()} rows · ${entry.columns} columns</span>
                <span style="margin-left:12px;">${date} ${time}</span>
              </div>
            </div>
            <button class="btn btn-secondary btn-sm compare-btn" data-id="${entry.session_id}" data-name="${entry.filename}">Compare</button>
          </div>
        `;
      }).join('');

      historyList.querySelectorAll('.compare-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          runComparison(btn.dataset.id, btn.dataset.name);
        });
      });
    }
    historySection.style.display = 'block';

    // ── Upload CSV directly to history ──────────────────────
    const historyZone = document.getElementById('upload-history-zone');
    const historyFileInput = document.getElementById('history-file-input');
    if (historyZone) {
      historyZone.addEventListener('dragover', e => { e.preventDefault(); historyZone.classList.add('drag-over'); });
      historyZone.addEventListener('dragleave', () => historyZone.classList.remove('drag-over'));
      historyZone.addEventListener('drop', e => {
        e.preventDefault(); historyZone.classList.remove('drag-over');
        const f = e.dataTransfer.files[0];
        if (f) uploadHistoryCsv(f);
      });
      historyZone.addEventListener('click', () => historyFileInput.click());
      historyFileInput.addEventListener('change', () => { if (historyFileInput.files[0]) uploadHistoryCsv(historyFileInput.files[0]); });
    }

    async function uploadHistoryCsv(file) {
      showAlert(statusEl, 'info', `Uploading ${file.name} to history…`);
      try {
        const fd = new FormData();
        fd.append('file', file);
        const res = await API.post('/api/compare/upload', fd, true);
        showAlert(statusEl, 'success', `"${res.filename}" saved to history (${res.rows} rows). Reloading…`);
        setTimeout(() => location.reload(), 1200);
      } catch (e) {
        showAlert(statusEl, 'danger', 'Upload failed: ' + e.message);
      }
    }
  } catch (e) {
    showAlert(statusEl, 'danger', 'Failed to load history. Make sure the server is running and has been restarted after the latest update. Error: ' + e.message);
    return;
  }

  // ── Run comparison ─────────────────────────────────────────
  async function runComparison(previousId, previousName) {
    showAlert(statusEl, 'info', `Comparing with ${previousName}…`);
    historySection.style.display = 'none';
    loadingEl.style.display = 'block';

    try {
      const res = await API.get(`/api/compare?session_id=${sid}&previous_id=${previousId}`);
      previousStats = res.previous;
      currentStats = res.current;
      insightsText = res.insights;

      loadingEl.style.display = 'none';
      renderResults(previousName);
    } catch (e) {
      loadingEl.style.display = 'none';
      historySection.style.display = 'block';
      showAlert(statusEl, 'danger', 'Comparison failed: ' + e.message);
    }
  }

  // ── Render results ─────────────────────────────────────────
  function renderResults(previousName) {
    showAlert(statusEl, 'success', `Comparison complete against <strong>${previousName}</strong> — AI insights generated.`);

    // Insights
    insightsBody.innerHTML = marked.parse(insightsText);
    insightsEl.style.display = 'block';

    // Metric overview cards
    const prevRow = previousStats.row_count;
    const currRow = currentStats.row_count;
    const rowDiff = currRow - prevRow;
    const rowPct = prevRow > 0 ? round((rowDiff / prevRow) * 100) : 0;

    const prevMiss = Object.values(previousStats.missing_values).reduce((a, b) => a + b, 0);
    const currMiss = Object.values(currentStats.missing_values).reduce((a, b) => a + b, 0);

    const prevDup = previousStats.duplicate_rows;
    const currDup = currentStats.duplicate_rows;

    const newCols = (currentStats.columns || []).filter(c => !(previousStats.columns || []).includes(c));
    const removedCols = (previousStats.columns || []).filter(c => !(currentStats.columns || []).includes(c));

    metricsGrid.innerHTML = `
      <div class="kpi-card">
        <div class="kpi-label">Row Count</div>
        <div class="kpi-value">${currRow.toLocaleString()}</div>
        <div class="kpi-trend ${rowDiff >= 0 ? 'up' : 'down'}">
          ${rowDiff >= 0 ? '↑' : '↓'} ${rowDiff >= 0 ? '+' : ''}${rowDiff.toLocaleString()} (${rowPct >= 0 ? '+' : ''}${rowPct}%)
          <span style="color:var(--text-secondary);font-weight:400;"> vs ${prevRow.toLocaleString()}</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Columns</div>
        <div class="kpi-value">${currentStats.column_count}</div>
        <div class="kpi-trend">
          ${newCols.length > 0 ? `<span style="color:var(--green);">+${newCols.length} new</span>` : ''}
          ${removedCols.length > 0 ? ` <span style="color:var(--red);">-${removedCols.length} removed</span>` : ''}
          <span style="color:var(--text-secondary);font-weight:400;"> ${currentStats.columns.length} total</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Missing Values</div>
        <div class="kpi-value">${currMiss.toLocaleString()}</div>
        <div class="kpi-trend ${currMiss <= prevMiss ? 'up' : 'down'}">
          ${currMiss <= prevMiss ? '↓ Improved' : '↑ Worse'}
          <span style="color:var(--text-secondary);font-weight:400;"> was ${prevMiss.toLocaleString()}</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Duplicate Rows</div>
        <div class="kpi-value">${currDup.toLocaleString()}</div>
        <div class="kpi-trend ${currDup <= prevDup ? 'up' : 'down'}">
          ${currDup <= prevDup ? '↓ Improved' : '↑ Worse'}
          <span style="color:var(--text-secondary);font-weight:400;"> was ${prevDup.toLocaleString()}</span>
        </div>
      </div>
    `;
    metricsEl.style.display = 'block';

    // Numeric column changes
    const numPrev = previousStats.numeric_summary || {};
    const numCurr = currentStats.numeric_summary || {};
    const commonNum = Object.keys(numCurr).filter(c => numPrev[c]);

    if (commonNum.length > 0) {
      const rows = commonNum.map(col => {
        const pMean = numPrev[col].mean;
        const cMean = numCurr[col].mean;
        const diff = round(cMean - pMean);
        const pct = pMean !== 0 ? round((diff / Math.abs(pMean)) * 100) : 0;
        const arrow = diff > 0.01 ? '↑' : diff < -0.01 ? '↓' : '→';
        const color = diff > 0.01 ? 'var(--green)' : diff < -0.01 ? 'var(--red)' : 'var(--text-secondary)';
        return `<tr>
          <td style="font-weight:600;">${col}</td>
          <td>${fmtNum(pMean)}</td>
          <td>${fmtNum(cMean)}</td>
          <td style="color:${color};">${diff >= 0 ? '+' : ''}${fmtNum(diff)}</td>
          <td style="color:${color};">${pct >= 0 ? '+' : ''}${pct}%</td>
          <td style="color:${color};font-size:18px;">${arrow}</td>
        </tr>`;
      }).join('');
      numericBody.innerHTML = rows;
      numericEl.style.display = 'block';
    }

    // Data quality comparison
    qualityBody.innerHTML = `
      <tr><td>Rows</td><td>${prevRow.toLocaleString()}</td><td>${currRow.toLocaleString()}</td><td style="color:${rowDiff >= 0 ? 'var(--green)' : 'var(--red)'};">${rowDiff >= 0 ? '+' : ''}${rowDiff.toLocaleString()}</td></tr>
      <tr><td>Columns</td><td>${previousStats.column_count}</td><td>${currentStats.column_count}</td><td>${currentStats.column_count - previousStats.column_count >= 0 ? '+' : ''}${currentStats.column_count - previousStats.column_count}</td></tr>
      <tr><td>Missing Values</td><td>${prevMiss.toLocaleString()}</td><td>${currMiss.toLocaleString()}</td><td style="color:${currMiss <= prevMiss ? 'var(--green)' : 'var(--red)'};">${currMiss <= prevMiss ? '↓' : '↑'} ${Math.abs(currMiss - prevMiss).toLocaleString()}</td></tr>
      <tr><td>Duplicate Rows</td><td>${prevDup.toLocaleString()}</td><td>${currDup.toLocaleString()}</td><td style="color:${currDup <= prevDup ? 'var(--green)' : 'var(--red)'};">${currDup <= prevDup ? '↓' : '↑'} ${Math.abs(currDup - prevDup).toLocaleString()}</td></tr>
    `;
    qualityEl.style.display = 'block';

    // Download
    downloadSection.style.display = 'block';
  }

  // ── Download report ────────────────────────────────────────
  downloadBtn.addEventListener('click', () => {
    const prevRow = previousStats.row_count;
    const currRow = currentStats.row_count;
    const prevMiss = Object.values(previousStats.missing_values).reduce((a, b) => a + b, 0);
    const currMiss = Object.values(currentStats.missing_values).reduce((a, b) => a + b, 0);
    const prevDup = previousStats.duplicate_rows;
    const currDup = currentStats.duplicate_rows;

    let md = `# Dataset Comparison Report\n\n`;
    md += `## AI Insights\n\n${insightsText}\n\n`;
    md += `## Overview\n\n`;
    md += `| Metric | Previous | Current | Change |\n|---|---|---|---|\n`;
    md += `| Rows | ${prevRow.toLocaleString()} | ${currRow.toLocaleString()} | ${(currRow - prevRow) >= 0 ? '+' : ''}${(currRow - prevRow).toLocaleString()} |\n`;
    md += `| Columns | ${previousStats.column_count} | ${currentStats.column_count} | ${currentStats.column_count - previousStats.column_count} |\n`;
    md += `| Missing Values | ${prevMiss.toLocaleString()} | ${currMiss.toLocaleString()} | ${currMiss - prevMiss >= 0 ? '+' : ''}${(currMiss - prevMiss).toLocaleString()} |\n`;
    md += `| Duplicate Rows | ${prevDup.toLocaleString()} | ${currDup.toLocaleString()} | ${currDup - prevDup >= 0 ? '+' : ''}${(currDup - prevDup).toLocaleString()} |\n\n`;

    const numPrev = previousStats.numeric_summary || {};
    const numCurr = currentStats.numeric_summary || {};
    const commonNum = Object.keys(numCurr).filter(c => numPrev[c]);
    if (commonNum.length > 0) {
      md += `## Numeric Column Changes\n\n`;
      md += `| Column | Previous Mean | Current Mean | Change | % Change |\n|---|---|---|---|---|\n`;
      commonNum.forEach(col => {
        const pMean = numPrev[col].mean;
        const cMean = numCurr[col].mean;
        const diff = round(cMean - pMean);
        const pct = pMean !== 0 ? round((diff / Math.abs(pMean)) * 100) : 0;
        md += `| ${col} | ${fmtNum(pMean)} | ${fmtNum(cMean)} | ${diff >= 0 ? '+' : ''}${fmtNum(diff)} | ${pct >= 0 ? '+' : ''}${pct}% |\n`;
      });
      md += '\n';
    }

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'comparison_report.md';
    a.click();
    URL.revokeObjectURL(url);
  });
});
