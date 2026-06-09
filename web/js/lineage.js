// ─── Data Lineage Visualization ───────────────────────────────

const CATEGORY_COLORS = {
  upload: '#3b82f6',
  schema: '#8b5cf6',
  clean: '#10b981',
  pii: '#f59e0b',
  kpi: '#eab308',
  insights: '#ef4444',
  report: '#6b7280',
};

const CATEGORY_ORDER = ['upload', 'schema', 'clean', 'pii', 'kpi', 'insights', 'report'];

const CATEGORY_LABELS = {
  upload: 'Upload',
  schema: 'Schema',
  clean: 'Cleaning',
  pii: 'PII Masking',
  kpi: 'KPI Calculation',
  insights: 'Insights',
  report: 'Report',
};

function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return String(n);
}

async function loadLineage() {
  const sessionId = Session.get();
  if (!sessionId) {
    document.getElementById('lineage-root').innerHTML =
      '<div class="alert alert-warning">Please upload a dataset first.</div>';
    return;
  }

  const root = document.getElementById('lineage-root');
  showLoading(root, 'Loading lineage…');

  try {
    const data = await API.get(`/api/lineage?session_id=${sessionId}`);
    renderLineage(data);
    document.getElementById('lineage-session').textContent =
      `Session: ${sessionId.substring(0, 12)}…`;
  } catch (err) {
    root.innerHTML = `<div class="alert alert-error">Failed to load lineage: ${err.message}</div>`;
  }
}

function renderLineage(data) {
  const root = document.getElementById('lineage-root');
  const steps = data.steps || [];

  if (steps.length === 0) {
    root.innerHTML = `
      <div class="alert alert-info" style="text-align:center;padding:40px;">
        <div style="font-size:40px;margin-bottom:12px;">↗</div>
        <h3 style="margin-bottom:8px;">No Lineage Data</h3>
        <p style="color:var(--text-secondary);">Upload and process a dataset to see the data lineage DAG.</p>
      </div>`;
    return;
  }

  // Group by category
  const grouped = {};
  for (const cat of CATEGORY_ORDER) grouped[cat] = [];
  for (const step of steps) {
    const cat = step.category || 'clean';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(step);
  }

  // Build DAG HTML
  let dagHtml = '<div class="lineage-dag">';
  let firstColumn = true;

  for (const cat of CATEGORY_ORDER) {
    const catSteps = grouped[cat];
    if (catSteps.length === 0) continue;

    const color = CATEGORY_COLORS[cat] || '#6b7280';
    dagHtml += `<div class="lineage-column">
      <div class="lineage-category-header" style="border-color:${color};color:${color}">
        ${CATEGORY_LABELS[cat] || cat}
        <span class="lineage-step-count">${catSteps.length}</span>
      </div>`;

    for (const step of catSteps) {
      const rowDiff = step.rows_after - step.rows_before;
      const colDiff = step.columns_after - step.columns_before;
      dagHtml += `
        <div class="lineage-card" style="border-left:3px solid ${color}" data-step-id="${step.step_id}">
          <div class="lineage-card-header">
            <span class="lineage-step-id">${step.step_id}</span>
            <span class="lineage-step-name">${step.step_name}</span>
          </div>
          <div class="lineage-card-desc">${step.description}</div>
          <div class="lineage-card-meta">
            ${step.affected_columns && step.affected_columns.length ? `
              <span class="lineage-meta-item" title="Affected columns">
                <span class="lineage-meta-label">Cols:</span>
                ${step.affected_columns.length <= 3
                  ? step.affected_columns.join(', ')
                  : step.affected_columns.slice(0, 3).join(', ') + '…'}
              </span>
            ` : ''}
            ${rowDiff !== 0 ? `
              <span class="lineage-meta-item ${rowDiff < 0 ? 'lineage-meta-down' : 'lineage-meta-up'}">
                ${rowDiff < 0 ? '↓' : '↑'} ${formatNumber(Math.abs(rowDiff))} rows
              </span>
            ` : `<span class="lineage-meta-item">${formatNumber(step.rows_after)} rows</span>`}
            <span class="lineage-meta-item">${step.duration_ms ? (step.duration_ms / 1000).toFixed(1) + 's' : ''}</span>
          </div>
        </div>`;
    }

    dagHtml += '</div>';

    // Connector arrow between columns
    if (!firstColumn) {
      // Arrow is rendered via CSS ::before on the column
    }
    firstColumn = false;
  }

  dagHtml += '</div>';

  // Build detail table
  let tableHtml = '';
  if (steps.length > 0) {
    tableHtml = `
      <div class="lineage-table-wrapper">
        <table class="lineage-table">
          <thead>
            <tr>
              <th>Step ID</th>
              <th>Name</th>
              <th>Category</th>
              <th>Description</th>
              <th>Columns</th>
              <th>Rows Before</th>
              <th>Rows After</th>
              <th>Duration</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            ${steps.map(s => {
              const color = CATEGORY_COLORS[s.category] || '#6b7280';
              return `<tr>
                <td><code>${s.step_id}</code></td>
                <td>${s.step_name}</td>
                <td><span class="cat-badge" style="background:${color}20;color:${color};border:1px solid ${color}40">${s.category}</span></td>
                <td>${s.description}</td>
                <td>${(s.affected_columns || []).length > 0 ? (s.affected_columns || []).join(', ') : '—'}</td>
                <td>${formatNumber(s.rows_before)}</td>
                <td>${formatNumber(s.rows_after)}</td>
                <td>${s.duration_ms ? (s.duration_ms / 1000).toFixed(1) + 's' : '—'}</td>
                <td class="lineage-timestamp">${s.timestamp ? new Date(s.timestamp).toLocaleString() : '—'}</td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>`;
  }

  // Summary stats
  const totalSteps = steps.length;
  const totalRowChange = steps.reduce((sum, s) => sum + (s.rows_before - s.rows_after), 0);
  const categories = new Set(steps.map(s => s.category)).size;

  root.innerHTML = `
    <div class="lineage-summary">
      <div class="summary-stat"><span class="stat-value">${totalSteps}</span><span class="stat-label">Total Steps</span></div>
      <div class="summary-stat"><span class="stat-value">${categories}</span><span class="stat-label">Categories</span></div>
      <div class="summary-stat"><span class="stat-value ${totalRowChange > 0 ? 'stat-negative' : 'stat-neutral'}">${formatNumber(Math.abs(totalRowChange))}</span><span class="stat-label">Rows Changed</span></div>
      <div class="summary-stat"><span class="stat-value">${steps[steps.length-1].columns_after}</span><span class="stat-label">Final Columns</span></div>
    </div>
    <div class="lineage-dag-container">${dagHtml}</div>
    <h3 class="lineage-table-title">Step Details</h3>
    ${tableHtml}`;
}

document.addEventListener('DOMContentLoaded', () => {
  initSidebar('lineage');
  renderSessionBadge();
  loadLineage();
  // Refresh button
  const refreshBtn = document.getElementById('refresh-lineage');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', loadLineage);
  }
});
