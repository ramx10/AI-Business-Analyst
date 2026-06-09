// ─── LLM Provider Settings ────────────────────────────────────
async function initLLMSettings() {
  const container = document.getElementById('llm-settings');
  if (!container) return;

  try {
    const cfg = await API.get('/api/llm/config');
    renderLLMForm(container, cfg);
  } catch (err) {
    container.innerHTML = `<div class="alert alert-error">Failed to load LLM config: ${err.message}</div>`;
  }
}

function renderLLMForm(container, cfg) {
  const providers = ['groq', 'openai', 'anthropic', 'ollama'];
  const providerLabels = { groq: 'Groq', openai: 'OpenAI', anthropic: 'Anthropic', ollama: 'Ollama (local)' };

  container.innerHTML = `
    <div class="llm-field">
      <label for="llm-provider">Provider</label>
      <select id="llm-provider">
        ${providers.map(p => `<option value="${p}"${p === cfg.provider ? ' selected' : ''}>${providerLabels[p]}</option>`).join('')}
      </select>
    </div>
    <div class="llm-field">
      <label for="llm-model">Model</label>
      <select id="llm-model"></select>
    </div>
    <div class="llm-field" id="api-key-field">
      <label for="llm-api-key">API Key</label>
      <div class="llm-api-row">
        <input type="password" id="llm-api-key" placeholder="Enter API key for selected provider" />
        <button class="btn btn-ghost btn-sm" id="toggle-key-visibility" type="button" title="Show/Hide key">✦</button>
      </div>
      <span class="llm-hint" id="api-key-hint"></span>
    </div>
    <div class="llm-actions">
      <button class="btn btn-secondary" id="btn-test">Test Connection</button>
      <button class="btn btn-primary" id="btn-save">Save</button>
    </div>
    <div id="llm-status" class="llm-status"></div>
  `;

  const providerSelect = document.getElementById('llm-provider');
  const modelSelect = document.getElementById('llm-model');
  const apiKeyInput = document.getElementById('llm-api-key');
  const apiKeyField = document.getElementById('api-key-field');
  const apiKeyHint = document.getElementById('api-key-hint');
  const toggleBtn = document.getElementById('toggle-key-visibility');
  const testBtn = document.getElementById('btn-test');
  const saveBtn = document.getElementById('btn-save');
  const statusEl = document.getElementById('llm-status');

  const apiKeySet = cfg.has_api_key;

  function updateApiKeyHint(provider) {
    const needsKey = provider !== 'ollama';
    apiKeyField.style.display = needsKey ? '' : 'none';
    if (needsKey) {
      const isSet = apiKeySet[provider];
      apiKeyHint.textContent = isSet ? '✔ API key is configured' : '⚠ No API key set for this provider';
      apiKeyHint.className = `llm-hint ${isSet ? 'llm-hint-ok' : 'llm-hint-warn'}`;
    }
  }

  function updateModels(provider) {
    modelSelect.innerHTML = '<option value="">Loading...</option>';
    API.get(`/api/llm/models?provider=${provider}`)
      .then(data => {
        modelSelect.innerHTML = data.models.map(m =>
          `<option value="${m}"${m === cfg.model ? ' selected' : ''}>${m}</option>`
        ).join('');
      })
      .catch(() => {
        modelSelect.innerHTML = '<option value="">Failed to load models</option>';
      });
  }

  providerSelect.addEventListener('change', () => {
    const p = providerSelect.value;
    updateModels(p);
    updateApiKeyHint(p);
    apiKeyInput.value = '';
  });

  toggleBtn.addEventListener('click', () => {
    const t = apiKeyInput;
    t.type = t.type === 'password' ? 'text' : 'password';
  });

  testBtn.addEventListener('click', async () => {
    statusEl.className = 'llm-status';
    statusEl.textContent = 'Testing connection...';
    testBtn.disabled = true;
    try {
      const payload = { provider: providerSelect.value, model: modelSelect.value };
      if (apiKeyInput.value) payload.api_key = apiKeyInput.value;
      const result = await API.post('/api/llm/test', payload);
      statusEl.className = `llm-status ${result.success ? 'llm-status-ok' : 'llm-status-err'}`;
      statusEl.textContent = result.success ? '✔ Connection successful' : `✗ ${result.message}`;
    } catch (err) {
      statusEl.className = 'llm-status llm-status-err';
      statusEl.textContent = `✗ ${err.message}`;
    } finally {
      testBtn.disabled = false;
    }
  });

  saveBtn.addEventListener('click', async () => {
    statusEl.className = 'llm-status';
    statusEl.textContent = 'Saving...';
    saveBtn.disabled = true;
    try {
      const payload = { provider: providerSelect.value, model: modelSelect.value };
      if (apiKeyInput.value) payload.api_key = apiKeyInput.value;
      const result = await API.post('/api/llm/config', payload);
      statusEl.className = 'llm-status llm-status-ok';
      statusEl.textContent = '✔ Settings saved successfully';
      cfg.provider = result.config.provider;
      cfg.model = result.config.model;
      cfg.has_api_key = result.config.has_api_key;
      updateApiKeyHint(providerSelect.value);
      Toast.show('LLM provider settings saved', 'success');
    } catch (err) {
      statusEl.className = 'llm-status llm-status-err';
      statusEl.textContent = `✗ ${err.message}`;
      Toast.show(`Failed to save: ${err.message}`, 'error');
    } finally {
      saveBtn.disabled = false;
    }
  });

  updateModels(cfg.provider);
  updateApiKeyHint(cfg.provider);
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('llm-settings')) {
    initLLMSettings();
  }
});
