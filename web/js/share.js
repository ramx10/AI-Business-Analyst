// ─── Share Management ─────────────────────────────────────────

async function loadShareList() {
  const container = document.getElementById('share-list');
  if (!container) return;
  const sid = Session.require(); if (!sid) return;
  try {
    const data = await API.get(`/api/share/list?session_id=${sid}`);
    const shares = data.shares || [];
    if (shares.length === 0) {
      container.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-tertiary);font-size:13px;">No active share links. Create one above.</div>';
      return;
    }
    container.innerHTML = shares.map(s => {
      const expires = new Date(s.expiry).toLocaleString();
      const url = `${window.location.origin}/share.html?token=${s.token}`;
      return `
        <div class="share-item" style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:8px;">
          <div>
            <div style="font-size:13px;font-weight:600;color:var(--text-primary);">
              ${s.has_password ? '⊡ ' : '➔ '}
              <a href="${url}" target="_blank" style="color:var(--accent);text-decoration:none;">${url}</a>
            </div>
            <div style="font-size:11px;color:var(--text-secondary);margin-top:4px;">
              Expires: ${expires} ${s.has_password ? '· Password protected' : ''}
            </div>
          </div>
          <button class="btn btn-danger btn-sm" onclick="revokeShare('${s.token}')" style="flex-shrink:0;">Revoke</button>
        </div>`;
    }).join('');
  } catch (e) {
    container.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
  }
}

async function createShare() {
  const sid = Session.require(); if (!sid) return;
  const expirySelect = document.getElementById('share-expiry');
  const passwordInput = document.getElementById('share-password');
  const resultDiv = document.getElementById('share-result');

  const expiryMap = { '1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720 };
  const expiryHours = expiryMap[expirySelect.value] || 24;
  const password = passwordInput.value.trim() || null;

  try {
    const data = await API.post('/api/share/create', {
      session_id: sid,
      expiry_hours: expiryHours,
      password: password,
    });
    const shareUrl = `${window.location.origin}/share.html?token=${data.token}`;
    resultDiv.innerHTML = `
      <div style="padding:16px;background:var(--green-muted);border:1px solid var(--green);border-radius:var(--radius);margin-top:12px;">
        <div style="font-size:13px;font-weight:600;color:var(--green);margin-bottom:8px;">✓ Share link created!</div>
        <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">
          <input type="text" class="input" value="${shareUrl}" readonly style="flex:1;font-size:12px;padding:6px 10px;" id="share-url-copy">
          <button class="btn btn-secondary btn-sm" onclick="copyShareUrl()">Copy</button>
        </div>
        <div style="text-align:center;margin-top:8px;">
          <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(shareUrl)}"
               alt="QR Code" style="border-radius:8px;" />
        </div>
        <div style="font-size:11px;color:var(--text-secondary);margin-top:8px;">
          Expires: ${new Date(data.expiry).toLocaleString()}
          ${password ? '· Password protected' : ''}
        </div>
      </div>
    `;
    passwordInput.value = '';
    loadShareList();
  } catch (e) {
    resultDiv.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
  }
}

function copyShareUrl() {
  const input = document.getElementById('share-url-copy');
  if (!input) return;
  input.select();
  document.execCommand('copy');
  Toast.show('Share URL copied to clipboard!', 'success');
}

async function revokeShare(token) {
  if (!confirm('Revoke this share link? It will no longer be accessible.')) return;
  try {
    await API.post(`/api/share/revoke/${token}`, {});
  } catch (e) {
    // fallback to DELETE
    await fetch(`/api/share/${token}`, { method: 'DELETE' });
  }
  Toast.show('Share link revoked.', 'success');
  loadShareList();
}

// ─── Shared Dashboard View ────────────────────────────────────

async function initSharedView() {
  const params = new URLSearchParams(window.location.search);
  const token = params.get('token');
  if (!token) {
    document.getElementById('shared-root').innerHTML = '<div class="alert alert-danger">No share token provided.</div>';
    return;
  }

  const root = document.getElementById('shared-root');
  if (!root) return;

  try {
    const resp = await API.get(`/api/share/${token}`);

    if (resp.requires_password) {
      root.innerHTML = `
        <div class="password-gate" style="max-width:400px;margin:60px auto;text-align:center;">
          <div style="font-size:48px;margin-bottom:16px;">⊡</div>
          <h2 style="font-size:18px;font-weight:700;color:var(--text-primary);margin-bottom:8px;">Password Required</h2>
          <p style="font-size:13px;color:var(--text-secondary);margin-bottom:20px;">This dashboard is password-protected. Enter the password to view.</p>
          <input type="password" id="share-password-input" class="input" placeholder="Enter password"
                 style="width:100%;margin-bottom:12px;text-align:center;font-size:14px;padding:10px;">
          <button class="btn btn-primary" onclick="verifySharedPassword('${token}')" style="width:100%;justify-content:center;">Unlock Dashboard</button>
          <div id="share-password-error" style="margin-top:8px;"></div>
        </div>
      `;
      return;
    }

    renderSharedDashboard(resp.session_id, resp.dashboard);
  } catch (e) {
    if (e.message.includes('410') || e.message.includes('expired')) {
      root.innerHTML = '<div class="alert alert-warning" style="text-align:center;padding:40px;"><div style="font-size:48px;margin-bottom:12px;">◉</div><h2>This share link has expired.</h2><p style="color:var(--text-secondary);">Please ask the owner to create a new link.</p></div>';
    } else if (e.message.includes('404')) {
      root.innerHTML = '<div class="alert alert-warning" style="text-align:center;padding:40px;"><div style="font-size:48px;margin-bottom:12px;">➔</div><h2>Share link not found.</h2></div>';
    } else {
      root.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
    }
  }
}

async function verifySharedPassword(token) {
  const password = document.getElementById('share-password-input').value;
  const errorDiv = document.getElementById('share-password-error');
  try {
    const resp = await API.post(`/api/share/verify/${token}`, { password });
    renderSharedDashboard(resp.session_id, resp.dashboard);
  } catch (e) {
    errorDiv.innerHTML = `<div class="alert alert-danger" style="font-size:12px;">${e.message}</div>`;
  }
}

function renderSharedDashboard(sessionId, dashData) {
  const root = document.getElementById('shared-root');
  if (!root || !dashData) return;

  const k = dashData.kpis;
  const c = dashData.charts;

  root.innerHTML = `
    <div class="shared-dashboard" style="max-width:1200px;margin:0 auto;padding:24px;">
      <h1 style="font-size:24px;font-weight:700;color:var(--text-primary);margin-bottom:24px;">Executive Dashboard</h1>

      <div class="kpi-grid" style="display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:24px;">
        ${['revenue','profit','orders','customers','profit_margin'].map(key => {
          const kd = k[key]; if (!kd) return '';
          const up = kd.direction === 'up';
          return `<div class="kpi-card" style="background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius);padding:16px;">
            <div class="kpi-label" style="font-size:11px;font-weight:600;text-transform:uppercase;color:var(--text-secondary);margin-bottom:4px;">${key.replace(/_/g,' ').replace(/\b\w/g,l=>l.toUpperCase())}</div>
            <div class="kpi-value" style="font-size:22px;font-weight:700;color:var(--text-primary);">${kd.value}</div>
            <div class="kpi-trend ${up ? 'up' : 'down'}" style="font-size:11px;color:${up ? 'var(--green)' : 'var(--red)'};">${up ? '↑' : '↓'} ${kd.trend}</div>
          </div>`;
        }).join('')}
      </div>

      <div style="display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:24px;">
        <div class="card" style="padding:20px;">
          <h4 style="font-size:14px;font-weight:700;color:var(--text-primary);margin:0 0 12px 0;">Revenue Trend</h4>
          <div style="height:250px;"><canvas id="shared-chart-trend"></canvas></div>
        </div>
        <div class="card" style="padding:20px;">
          <h4 style="font-size:14px;font-weight:700;color:var(--text-primary);margin:0 0 12px 0;">Category Share</h4>
          <div style="height:250px;"><canvas id="shared-chart-cat"></canvas></div>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px;">
        <div class="card" style="padding:20px;">
          <h4 style="font-size:14px;font-weight:700;color:var(--text-primary);margin:0 0 12px 0;">Regional Breakdown</h4>
          <div style="height:250px;"><canvas id="shared-chart-region"></canvas></div>
        </div>
        <div class="card" style="padding:20px;">
          <h4 style="font-size:14px;font-weight:700;color:var(--text-primary);margin:0 0 12px 0;">Top Products</h4>
          <div style="height:250px;"><canvas id="shared-chart-prods"></canvas></div>
        </div>
      </div>
    </div>
    <div class="shared-footer" style="text-align:center;padding:16px;font-size:11px;color:var(--text-tertiary);border-top:1px solid var(--border);margin-top:24px;">
      Powered by <strong>AI Business Analyst</strong>
    </div>
  `;

  const cfg = getThemeConfig();
  const baseOpts = getBaseOpts(cfg);

  function makeSharedChart(id, type, labels, data) {
    const ctx = document.getElementById(id); if (!ctx) return;
    if (window.chartInstances[id]) window.chartInstances[id].destroy();
    const datasets = type === 'line' ? [{
      data, borderColor: cfg.palette[0], backgroundColor: cfg.palette[0] + '18',
      fill: true, tension: 0.35, pointRadius: 3, pointBackgroundColor: cfg.palette[0], borderWidth: 2
    }] : type === 'doughnut' ? [{
      data, backgroundColor: cfg.palette, borderWidth: 2
    }] : [{
      data, backgroundColor: cfg.paletteMuted, borderColor: cfg.palette[0], borderWidth: 1, borderRadius: 4
    }];
    window.chartInstances[id] = new Chart(ctx, {
      type,
      data: { labels, datasets },
      options: {
        ...baseOpts,
        responsive: true, maintainAspectRatio: false,
        plugins: { ...baseOpts.plugins, legend: { display: type === 'doughnut' ? { position: 'right' } : false } },
        ...(type === 'doughnut' ? { cutout: '65%' } : {}),
      }
    });
  }

  const tl = c.revenue_trend?.labels || [];
  const tv = c.revenue_trend?.values || [];
  if (tl.length && tv.length) makeSharedChart('shared-chart-trend', 'line', tl, tv);

  const cl = c.category?.labels || [];
  const cv = c.category?.values || [];
  if (cl.length && cv.length) makeSharedChart('shared-chart-cat', 'doughnut', cl, cv);

  const rl = c.regional?.labels || [];
  const rv = c.regional?.values || [];
  if (rl.length && rv.length) makeSharedChart('shared-chart-region', 'bar', rl, rv);

  const pl = c.products?.labels || [];
  const pv = c.products?.values || [];
  if (pl.length && pv.length) makeSharedChart('shared-chart-prods', 'bar', pl, pv);
}
