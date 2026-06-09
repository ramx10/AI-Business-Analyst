document.addEventListener('DOMContentLoaded', () => {
  const sid = Session.require();
  if (!sid) return;

  const colStatus = document.getElementById('column-status');
  const scanResults = document.getElementById('scan-results');
  const scanEmpty = document.getElementById('scan-empty');
  const findingsBody = document.getElementById('findings-body');
  const findingsCount = document.getElementById('findings-count');
  const maskSection = document.getElementById('mask-section');
  const maskColumns = document.getElementById('mask-columns');
  const maskPreview = document.getElementById('mask-preview');
  const maskLog = document.getElementById('mask-log');
  const previewHead = document.getElementById('preview-head');
  const previewBody = document.getElementById('preview-body');

  let findings = [];

  // ─── Column Status ──────────────────────────────────────────
  async function loadColumnStatus() {
    try {
      const data = await API.get(`/api/dataset/stats?session_id=${sid}`);
      const cols = data.column_names || [];
      colStatus.innerHTML = '<span class="chip chip-green">▣ Dataset loaded</span>';
      if (cols.length > 0) {
        colStatus.innerHTML += `<span class="chip chip-blue">${cols.length} columns</span>`;
        colStatus.innerHTML += `<span class="chip chip-purple">${data.row_count} rows</span>`;
      }
    } catch (e) {
      colStatus.innerHTML = '<span class="chip chip-orange">No dataset loaded</span>';
    }
  }

  // ─── Scan ───────────────────────────────────────────────────
  document.getElementById('btn-scan').addEventListener('click', async () => {
    scanResults.style.display = 'none';
    scanEmpty.style.display = 'none';
    maskSection.style.display = 'none';
    maskPreview.style.display = 'none';
    findingsBody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-tertiary);">Scanning…</td></tr>';
    scanResults.style.display = 'block';

    try {
      const data = await API.post(`/api/pii/detect?session_id=${sid}`, {});
      findings = data.findings || [];

      if (findings.length === 0) {
        scanResults.style.display = 'none';
        scanEmpty.style.display = 'block';
        return;
      }

      findingsCount.textContent = findings.length;
      findingsBody.innerHTML = findings.map(f => {
        const riskColors = { high: 'var(--red)', critical: 'var(--red)', medium: 'var(--yellow)', low: 'var(--green)' };
        const color = riskColors[f.risk] || 'var(--text-secondary)';
        return `<tr>
          <td style="padding:8px 12px;font-weight:600;">${esc(f.column)}</td>
          <td style="padding:8px 12px;"><span class="chip chip-blue">${esc(f.type)}</span></td>
          <td style="padding:8px 12px;font-size:12px;color:var(--text-secondary);">${esc(f.sample_values.join(', '))}</td>
          <td style="padding:8px 12px;text-align:right;">${f.count}</td>
          <td style="padding:8px 12px;"><span class="chip" style="background:${color}18;color:${color};">${esc(f.risk)}</span></td>
        </tr>`;
      }).join('');

      // Build mask checkboxes
      maskColumns.innerHTML = findings.map(f => `
        <label style="display:flex;align-items:center;gap:8px;padding:6px 0;cursor:pointer;">
          <input type="checkbox" class="mask-checkbox" value="${esc(f.column)}" checked style="accent-color:var(--accent);" />
          <span style="font-size:13px;font-weight:500;">${esc(f.column)}</span>
          <span class="chip chip-blue" style="font-size:10px;">${esc(f.type)}</span>
          <span style="font-size:11px;color:var(--text-tertiary);">(${f.count} values)</span>
        </label>
      `).join('');
      maskSection.style.display = 'block';
      Toast.show(`Found ${findings.length} PII column(s)`, 'info');
    } catch (e) {
      findingsBody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--red);">Error: ${esc(e.message)}</td></tr>`;
    }
  });

  // ─── Mask ───────────────────────────────────────────────────
  document.getElementById('btn-mask').addEventListener('click', async () => {
    const checked = document.querySelectorAll('.mask-checkbox:checked');
    const columns = Array.from(checked).map(cb => cb.value);

    if (columns.length === 0) {
      Toast.show('Select at least one column to mask.', 'warning');
      return;
    }

    try {
      const data = await API.post(`/api/pii/mask?session_id=${sid}`, { columns });
      const log = data.change_log || [];

      // Show log
      maskLog.innerHTML = '<div style="font-size:14px;font-weight:600;margin-bottom:8px;">✓ Masking Complete</div>';
      if (log.length > 0) {
        const list = log.map(l =>
          `<div style="font-size:12px;color:var(--text-secondary);margin-bottom:4px;">
            • <strong>${esc(l.column)}</strong> (${esc(l.type)}): ${l.values_masked} values masked
          </div>`
        ).join('');
        maskLog.innerHTML += list;
      }

      // Show preview table
      const preview = data.preview || [];
      if (preview.length > 0) {
        const cols = Object.keys(preview[0]);
        previewHead.innerHTML = cols.map(c => `<th style="text-align:left;padding:8px 12px;">${esc(c)}</th>`).join('');
        previewBody.innerHTML = preview.map(row =>
          `<tr>${cols.map(c => `<td style="padding:8px 12px;font-size:12px;">${esc(String(row[c]))}</td>`).join('')}</tr>`
        ).join('');
      }

      maskPreview.style.display = 'block';
      Toast.show(`${log.length} column(s) masked successfully`, 'success');
    } catch (e) {
      Toast.show('Masking failed: ' + e.message, 'error');
    }
  });

  // ─── Helpers ────────────────────────────────────────────────
  function esc(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  loadColumnStatus();
});
