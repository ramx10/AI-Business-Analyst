const ExportManager = {
  formats: [],

  async init() {
    try {
      this.formats = await API.get('/api/export/formats');
    } catch {
      this.formats = [];
    }
  },

  async downloadData(sessionId, formatId) {
    const blob = await this._postBlob('/api/export/data', { session_id: sessionId, format: formatId });
    const fmt = this.formats.find(f => f.id === formatId);
    const ext = fmt ? fmt.extension : '.bin';
    this._triggerDownload(blob, `export_${sessionId.slice(0, 8)}${ext}`);
  },

  async downloadDashboard(sessionId, formatId) {
    const blob = await this._postBlob('/api/export/dashboard', { session_id: sessionId, format: formatId });
    const fmt = this.formats.find(f => f.id === formatId);
    const ext = fmt ? fmt.extension : '.bin';
    this._triggerDownload(blob, `dashboard_${sessionId.slice(0, 8)}${ext}`);
  },

  async pushToGoogleSheets(sessionId, credentialsJson, spreadsheetId, sheetName) {
    const r = await API.post('/api/export/google-sheets', {
      session_id: sessionId,
      credentials_json: credentialsJson,
      spreadsheet_id: spreadsheetId,
      sheet_name: sheetName
    });
    Toast.show(r.message || 'Exported to Google Sheets', 'success');
  },

  async _postBlob(path, body) {
    const r = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!r.ok) {
      const e = await r.json();
      throw new Error(e.detail || 'Export failed');
    }
    return r.blob();
  },

  _triggerDownload(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  async renderExportSection(container, sessionId, mode = 'data') {
    await this.init();
    if (this.formats.length === 0) {
      container.innerHTML = '<div class="alert alert-warning">No export formats available.</div>';
      return;
    }

    const normalFormats = this.formats.filter(f => f.id !== 'google_sheets');
    const gsFormat = this.formats.find(f => f.id === 'google_sheets');

    let html = `
      <div class="card" style="padding:20px;margin-top:20px;">
        <h4 style="font-size:13px;font-weight:700;color:var(--text-primary);margin:0 0 12px 0;">
          ↑ Export Dataset
        </h4>
        <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end;">
          <div style="flex:1;min-width:180px;">
            <label style="font-size:11px;font-weight:600;color:var(--text-secondary);display:block;margin-bottom:4px;">Format</label>
            <select id="export-format-select" class="input" style="width:100%;padding:7px 10px;font-size:12px;cursor:pointer;">
              ${normalFormats.map(f => `<option value="${f.id}" data-ext="${f.extension}">${f.icon} ${f.name}</option>`).join('')}
              ${gsFormat ? `<option value="google_sheets">${gsFormat.icon} ${gsFormat.name}</option>` : ''}
            </select>
          </div>
          <div id="export-gs-fields" style="display:none;flex:2;gap:8px;align-items:flex-end;flex-wrap:wrap;">
            <div style="flex:1;min-width:150px;">
              <label style="font-size:11px;font-weight:600;color:var(--text-secondary);display:block;margin-bottom:4px;">Credentials JSON</label>
              <textarea id="export-gs-credentials" class="input" style="width:100%;padding:5px 8px;font-size:11px;height:32px;resize:none;" placeholder='{"type": "service_account", ...}'></textarea>
            </div>
            <div style="flex:1;min-width:120px;">
              <label style="font-size:11px;font-weight:600;color:var(--text-secondary);display:block;margin-bottom:4px;">Spreadsheet ID</label>
              <input id="export-gs-spreadsheet" class="input" type="text" style="width:100%;padding:5px 8px;font-size:11px;" placeholder="Sheet ID" />
            </div>
            <div style="flex:0 0 100px;">
              <label style="font-size:11px;font-weight:600;color:var(--text-secondary);display:block;margin-bottom:4px;">Sheet Name</label>
              <input id="export-gs-sheetname" class="input" type="text" style="width:100%;padding:5px 8px;font-size:11px;" value="Export" />
            </div>
          </div>
          <div style="flex:0 0 auto;">
            <button id="btn-export-download" class="btn btn-primary btn-sm" style="padding:7px 18px;font-size:12px;">
              ⬇ Download
            </button>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;

    const formatSelect = document.getElementById('export-format-select');
    const gsFields = document.getElementById('export-gs-fields');
    const downloadBtn = document.getElementById('btn-export-download');

    if (formatSelect) {
      formatSelect.addEventListener('change', () => {
        if (gsFields) {
          gsFields.style.display = formatSelect.value === 'google_sheets' ? 'flex' : 'none';
        }
        if (downloadBtn) {
          downloadBtn.textContent = formatSelect.value === 'google_sheets' ? '☁ Push to Sheets' : '⬇ Download';
        }
      });
    }

    if (downloadBtn) {
      downloadBtn.addEventListener('click', async () => {
        const fmt = formatSelect ? formatSelect.value : 'csv';
        downloadBtn.disabled = true;
        downloadBtn.textContent = '⏳ Exporting...';
        try {
          if (fmt === 'google_sheets') {
            const creds = document.getElementById('export-gs-credentials')?.value;
            const sheetId = document.getElementById('export-gs-spreadsheet')?.value;
            const sheetName = document.getElementById('export-gs-sheetname')?.value || 'Export';
            if (!creds || !sheetId) {
              Toast.show('Credentials JSON and Spreadsheet ID are required', 'error');
              return;
            }
            await this.pushToGoogleSheets(sessionId, creds, sheetId, sheetName);
          } else if (mode === 'dashboard') {
            await this.downloadDashboard(sessionId, fmt);
          } else {
            await this.downloadData(sessionId, fmt);
          }
          if (fmt !== 'google_sheets') {
            Toast.show('Download started', 'success');
          }
        } catch (e) {
          Toast.show(e.message, 'error');
        } finally {
          downloadBtn.disabled = false;
          downloadBtn.textContent = fmt === 'google_sheets' ? '☁ Push to Sheets' : '⬇ Download';
        }
      });
    }
  }
};
