// ─── Upload Page Logic ───────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  const zone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-input');
  const statusEl = document.getElementById('upload-status');
  const previewEl = document.getElementById('upload-preview');
  const sampleBtn = document.getElementById('sample-btn');
  const continueWrap = document.getElementById('continue-wrap');

  function showContinue() { if (continueWrap) continueWrap.style.display = 'block'; }
  // Drag-and-drop
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });
  zone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => { if (fileInput.files[0]) handleFile(fileInput.files[0]); });

  // Sample dataset
  sampleBtn.addEventListener('click', async () => {
    sampleBtn.disabled = true;
    sampleBtn.textContent = 'Generating…';
    statusEl.innerHTML = '';
    try {
      const data = await API.post('/api/upload/sample', {});
      Session.set(data.session_id);
      renderPreview(data, previewEl);
      showAlert(statusEl, 'success', `Sample dataset loaded — ${data.rows.toLocaleString()} rows, ${data.columns} columns.`);
      showContinue();
      renderSessionBadge();
    } catch (e) {
      showAlert(statusEl, 'danger', e.message);
    } finally {
      sampleBtn.disabled = false;
      sampleBtn.textContent = '↑ Load Sample Dataset';
    }
  });

  async function handleFile(file) {
    if (!file.name.endsWith('.csv')) { showAlert(statusEl, 'warning', 'Please upload a .csv file.'); return; }
    const form = new FormData();
    form.append('file', file);
    showAlert(statusEl, 'info', `Uploading ${file.name}…`);
    try {
      const data = await API.post('/api/upload', form, true);
      Session.set(data.session_id);
      renderPreview(data, previewEl);
      showAlert(statusEl, 'success', `Uploaded — ${data.rows.toLocaleString()} rows, ${data.columns} columns.`);
      showContinue();
      renderSessionBadge();
    } catch (e) {
      showAlert(statusEl, 'danger', e.message);
    }
  }

  function renderPreview(data, el) {
    if (!data.preview || !data.preview.length) return;
    const cols = Object.keys(data.preview[0]);
    const headerCells = cols.map(c => `<th>${c}</th>`).join('');
    const rows = data.preview.map(row =>
      `<tr>${cols.map(c => `<td>${row[c] ?? ''}</td>`).join('')}</tr>`
    ).join('');
    el.innerHTML = `
      <div class="card" style="margin-top:24px;">
        <div class="card-header">
          <div><div class="card-title">Data Preview</div>
          <div class="card-subtitle">First 5 rows of your dataset</div></div>
        </div>
        <div class="table-wrap"><table><thead><tr>${headerCells}</tr></thead><tbody>${rows}</tbody></table></div>
      </div>`;
  }
});
