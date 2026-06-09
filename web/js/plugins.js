// ─── Plugin Manager ──────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initSidebar('plugins');

  const pluginsGrid = document.getElementById('plugins-grid');
  const runSelect = document.getElementById('run-plugin-select');
  const paramsSection = document.getElementById('run-plugin-params');
  const paramsInput = document.getElementById('run-plugin-params-input');
  const btnRun = document.getElementById('btn-run-plugin');
  const btnUninstall = document.getElementById('btn-uninstall-plugin');
  const runResult = document.getElementById('run-plugin-result');
  const fileInput = document.getElementById('install-file-input');
  const btnInstall = document.getElementById('btn-install-plugin');
  const installResult = document.getElementById('install-plugin-result');

  let plugins = [];

  async function loadPlugins() {
    try {
      const data = await API.get('/api/plugins');
      plugins = data.plugins || [];
      renderPlugins();
      populateSelect();
      btnRun.disabled = true;
      btnUninstall.disabled = true;
    } catch (e) {
      pluginsGrid.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
    }
  }

  function renderPlugins() {
    if (plugins.length === 0) {
      pluginsGrid.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-tertiary);font-size:13px;">No plugins installed.</div>';
      return;
    }
    const categoryColors = {
      analysis: 'var(--blue)',
      cleaning: 'var(--green)',
      visualization: 'var(--purple)',
      export: 'var(--orange)',
      other: 'var(--text-tertiary)',
    };
    pluginsGrid.innerHTML = plugins.map(p => `
      <div class="card" style="padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">
          <div style="flex:1;min-width:0;">
            <div style="font-size:13px;font-weight:700;color:var(--text-primary);">${p.name}</div>
            <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">v${p.version}</div>
            <div style="font-size:11px;color:var(--text-tertiary);margin-top:4px;">${p.description || 'No description'}</div>
          </div>
          <span class="pill" style="background:${categoryColors[p.category] || categoryColors.other};color:#fff;font-size:10px;white-space:nowrap;">${p.category}</span>
        </div>
      </div>
    `).join('');
  }

  function populateSelect() {
    runSelect.innerHTML = '<option value="">— Choose a plugin —</option>' +
      plugins.map(p => `<option value="${p.name}">${p.name}</option>`).join('');
  }

  runSelect.addEventListener('change', () => {
    const name = runSelect.value;
    if (name) {
      paramsSection.style.display = 'block';
      btnRun.disabled = false;
      btnUninstall.disabled = false;
      runResult.innerHTML = '';
    } else {
      paramsSection.style.display = 'none';
      btnRun.disabled = true;
      btnUninstall.disabled = true;
    }
  });

  btnRun.addEventListener('click', async () => {
    const name = runSelect.value;
    const sid = Session.get();
    if (!name || !sid) {
      Toast.show('Select a plugin and ensure a dataset is loaded.', 'error');
      return;
    }
    let params = {};
    try {
      const raw = paramsInput.value.trim();
      if (raw) params = JSON.parse(raw);
    } catch {
      Toast.show('Invalid JSON parameters.', 'error');
      return;
    }
    btnRun.disabled = true;
    btnRun.textContent = 'Running…';
    runResult.innerHTML = '<div class="loading-state"><div class="spinner"></div><span>Running plugin…</span></div>';
    try {
      const result = await API.post(`/api/plugins/${encodeURIComponent(name)}/run`, {
        session_id: sid,
        params,
      });
      runResult.innerHTML = `
        <div class="alert alert-success">${result.summary || 'Plugin ran successfully.'}</div>
        <pre style="font-size:11px;max-height:200px;overflow:auto;margin-top:8px;padding:8px;background:var(--bg-elevated);border-radius:var(--radius);">${JSON.stringify(result, null, 2)}</pre>
      `;
      Toast.show('Plugin executed successfully.', 'success');
    } catch (e) {
      runResult.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
    } finally {
      btnRun.disabled = false;
      btnRun.textContent = 'Run';
    }
  });

  btnUninstall.addEventListener('click', async () => {
    const name = runSelect.value;
    if (!name) return;
    if (!confirm(`Uninstall plugin "${name}"?`)) return;
    btnUninstall.disabled = true;
    try {
      const result = await fetch(`/api/plugins/${encodeURIComponent(name)}`, { method: 'DELETE' });
      if (!result.ok) {
        const err = await result.json();
        throw new Error(err.detail || 'Uninstall failed');
      }
      Toast.show(`Plugin "${name}" uninstalled.`, 'success');
      await loadPlugins();
    } catch (e) {
      Toast.show(e.message, 'error');
    } finally {
      btnUninstall.disabled = false;
    }
  });

  fileInput.addEventListener('change', () => {
    btnInstall.disabled = !fileInput.files.length;
  });

  btnInstall.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;
    btnInstall.disabled = true;
    btnInstall.textContent = 'Installing…';
    installResult.innerHTML = '';
    try {
      const form = new FormData();
      form.append('file', file);
      const result = await API.post('/api/plugins/install', form, true);
      installResult.innerHTML = `<div class="alert alert-success">${result.message}</div>`;
      Toast.show(result.message, 'success');
      fileInput.value = '';
      await loadPlugins();
    } catch (e) {
      installResult.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
    } finally {
      btnInstall.disabled = false;
      btnInstall.textContent = 'Install';
    }
  });

  loadPlugins();
});
