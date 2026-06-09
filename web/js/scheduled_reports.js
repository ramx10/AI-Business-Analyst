// ─── Tab Switching ──────────────────────────────────────────────

function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
  const btn = document.querySelector(`.tab-btn[data-tab="${name}"]`);
  if (btn) btn.classList.add('active');
  const tab = document.getElementById(`tab-${name}`);
  if (tab) tab.style.display = 'block';
}

// ─── Scheduled Reports ──────────────────────────────────────────

async function loadSchedules() {
  const container = document.getElementById('schedules-list');
  if (!container) return;
  const sid = Session.require(); if (!sid) return;
  try {
    const data = await API.get(`/api/schedule/list?session_id=${sid}`);
    const schedules = data.schedules || [];
    if (schedules.length === 0) {
      container.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-tertiary);font-size:13px;">No schedules yet. Create one above.</div>';
      return;
    }
    container.innerHTML = schedules.map(s => {
      const next = s.next_run ? new Date(s.next_run).toLocaleString() : '—';
      const last = s.last_run ? new Date(s.last_run).toLocaleString() : 'Never';
      const statusClass = s.active ? 'alert-success' : 'alert-warning';
      const statusText = s.active ? 'Active' : 'Disabled';
      return `
        <div class="share-item" style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:8px;">
          <div style="flex:1;">
            <div style="font-size:13px;font-weight:600;color:var(--text-primary);">${escHtml(s.name)}</div>
            <div style="font-size:11px;color:var(--text-secondary);margin-top:4px;display:flex;gap:12px;flex-wrap:wrap;">
              <span>⏱ ${s.frequency}</span>
              <span>⊡ ${s.format}</span>
              <span>◈ Next: ${next}</span>
              <span>◉ Last: ${last}</span>
              <span class="${statusClass}" style="padding:1px 6px;border-radius:4px;font-size:10px;">${statusText}</span>
              ${s.email ? `<span>✦ ${escHtml(s.email)}</span>` : ''}
            </div>
          </div>
          <div style="display:flex;gap:8px;flex-shrink:0;">
            <button class="btn btn-secondary btn-sm" onclick="toggleSchedule('${s.schedule_id}')">${s.active ? 'Disable' : 'Enable'}</button>
            <button class="btn btn-danger btn-sm" onclick="deleteSchedule('${s.schedule_id}')">Delete</button>
          </div>
        </div>`;
    }).join('');
  } catch (e) {
    container.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
  }
}

async function createSchedule() {
  const sid = Session.require(); if (!sid) return;
  const name = document.getElementById('sched-name').value.trim() || 'Untitled Schedule';
  const frequency = document.getElementById('sched-frequency').value;
  const email = document.getElementById('sched-email').value.trim() || null;
  const format = document.getElementById('sched-format').value;
  const resultDiv = document.getElementById('sched-result');

  try {
    await API.post('/api/schedule/create', {
      session_id: sid, name, frequency, email, format,
    });
    resultDiv.innerHTML = `<div class="alert alert-success">Schedule created!</div>`;
    document.getElementById('sched-name').value = '';
    document.getElementById('sched-email').value = '';
    setTimeout(() => resultDiv.innerHTML = '', 3000);
    loadSchedules();
  } catch (e) {
    resultDiv.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
  }
}

async function toggleSchedule(id) {
  try {
    await API.post(`/api/schedule/${id}/toggle`, {});
    loadSchedules();
  } catch (e) {
    Toast.show(e.message, 'error');
  }
}

async function deleteSchedule(id) {
  if (!confirm('Delete this schedule?')) return;
  try {
    await API.post(`/api/schedule/delete/${id}`, {});
  } catch (e) {
    await fetch(`/api/schedule/${id}`, { method: 'DELETE' });
  }
  Toast.show('Schedule deleted.', 'success');
  loadSchedules();
}

// ─── Alert Rules ───────────────────────────────────────────────

async function loadAlerts() {
  const container = document.getElementById('alerts-list');
  if (!container) return;
  const sid = Session.require(); if (!sid) return;
  try {
    const data = await API.get(`/api/alerts/list?session_id=${sid}`);
    const alerts = data.alerts || [];
    if (alerts.length === 0) {
      container.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-tertiary);font-size:13px;">No alert rules yet. Create one above.</div>';
      return;
    }
    container.innerHTML = alerts.map(r => {
      const icons = { revenue_drop: '✦', profit_drop: '↓', missing_data: '◉', duplicate_spike: '↻' };
      return `
        <div class="share-item" style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:8px;">
          <div style="flex:1;">
            <div style="font-size:13px;font-weight:600;color:var(--text-primary);">${icons[r.metric] || '◉'} ${escHtml(r.name)}</div>
            <div style="font-size:11px;color:var(--text-secondary);margin-top:4px;display:flex;gap:12px;flex-wrap:wrap;">
              <span>Metric: ${r.metric}</span>
              <span>Condition: ${r.condition}</span>
              <span>Threshold: ${r.threshold}%</span>
              ${r.email ? `<span>✦ ${escHtml(r.email)}</span>` : ''}
            </div>
          </div>
          <div style="display:flex;gap:8px;flex-shrink:0;">
            <button class="btn btn-danger btn-sm" onclick="deleteAlert('${r.rule_id}')">Delete</button>
          </div>
        </div>`;
    }).join('');
  } catch (e) {
    container.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
  }
}

async function createAlert() {
  const sid = Session.require(); if (!sid) return;
  const name = document.getElementById('alert-name').value.trim() || 'Untitled Alert';
  const metric = document.getElementById('alert-metric').value;
  const condition = document.getElementById('alert-condition').value;
  const threshold = parseFloat(document.getElementById('alert-threshold').value) || 0;
  const email = document.getElementById('alert-email').value.trim() || null;
  const resultDiv = document.getElementById('alert-result');

  try {
    await API.post('/api/alerts/create', {
      session_id: sid, name, metric, condition, threshold, email,
    });
    resultDiv.innerHTML = `<div class="alert alert-success">Alert rule created!</div>`;
    document.getElementById('alert-name').value = '';
    document.getElementById('alert-email').value = '';
    document.getElementById('alert-threshold').value = '10';
    setTimeout(() => resultDiv.innerHTML = '', 3000);
    loadAlerts();
  } catch (e) {
    resultDiv.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
  }
}

async function deleteAlert(id) {
  if (!confirm('Delete this alert rule?')) return;
  try {
    await API.post(`/api/alerts/delete/${id}`, {});
  } catch (e) {
    await fetch(`/api/alerts/${id}`, { method: 'DELETE' });
  }
  Toast.show('Alert rule deleted.', 'success');
  loadAlerts();
}

// ─── Helpers ────────────────────────────────────────────────────

function escHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
