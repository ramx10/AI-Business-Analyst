// ─── Theme Management ──────────────────────────────────────────
(function() {
  const savedTheme = localStorage.getItem('ai_ba_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
})();

function toggleTheme() {
  const current = localStorage.getItem('ai_ba_theme') || 'dark';
  // If corporate light is active, toggle to dark. Otherwise toggle to corporate light.
  const next = current === 'dark' ? 'light-corporate' : 'dark';
  localStorage.setItem('ai_ba_theme', next);
  document.documentElement.setAttribute('data-theme', next);
  
  const toggles = document.querySelectorAll('#global-theme-toggle');
  toggles.forEach(t => t.innerHTML = next === 'dark' ? '☀️' : '🌙');
  
  const select = document.getElementById('theme-select');
  if (select) {
    select.value = next;
  }
  
  window.dispatchEvent(new CustomEvent('theme-changed', { detail: { theme: next } }));
}

// ─── API Client ───────────────────────────────────────────────
const API = {
  async post(path, body, isForm = false) {
    const opts = { method: 'POST' };
    if (isForm) { opts.body = body; }
    else { opts.headers = { 'Content-Type': 'application/json' }; opts.body = JSON.stringify(body); }
    const r = await fetch(path, opts);
    if (!r.ok) { const e = await r.json(); throw new Error(e.detail || 'Request failed'); }
    return r.json();
  },
  async get(path) {
    const r = await fetch(path);
    if (!r.ok) { const e = await r.json(); throw new Error(e.detail || 'Request failed'); }
    return r.json();
  }
};

// ─── Session ──────────────────────────────────────────────────
const Session = {
  key: 'ai_ba_session_id',
  get() { return localStorage.getItem(this.key); },
  set(id) { localStorage.setItem(this.key, id); },
  clear() { localStorage.removeItem(this.key); },
  require() {
    const id = this.get();
    if (!id) { window.location.href = '/upload.html'; return null; }
    return id;
  }
};

// ─── Sidebar Injection ────────────────────────────────────────
function buildSidebar(activePage) {
  const navItems = [
    { href: '/index.html',     icon: '⊞', label: 'Overview',  badge: null,  page: 'index' },
    { href: '/upload.html',    icon: '↑',  label: 'Upload Data', badge: '1', page: 'upload' },
    { href: '/schema.html',    icon: '≡',  label: 'Schema',    badge: '2',   page: 'schema' },
    { href: '/clean.html',     icon: '◈',  label: 'Cleaning',  badge: '3',   page: 'clean' },
    { href: '/dashboard.html', icon: '▣',  label: 'Dashboard', badge: '4',   page: 'dashboard' },
  ];
  const aiItems = [
    { href: '/insights.html',  icon: '◉',  label: 'Insights',  badge: '5',   page: 'insights' },
    { href: '/report.html',    icon: '⊡',  label: 'Report',    badge: '6',   page: 'report' },
  ];

  const makeItem = item => {
    const isActive = item.page === activePage;
    return `<a class="nav-item${isActive ? ' active' : ''}" href="${item.href}">
      <span class="nav-icon">${item.icon}</span>${item.label}
      ${item.badge ? `<span class="nav-badge">${item.badge}</span>` : ''}
    </a>`;
  };

  return `
    <div class="sidebar-header" onclick="window.location='/index.html'">
      <div class="logo-mark">A</div>
      <span class="workspace-name">AI Business Analyst</span>
      <span class="chevron">⌄</span>
    </div>
    <div class="nav-section">${navItems.map(makeItem).join('')}</div>
    <div class="nav-section">
      <div class="nav-section-label">AI Pipeline</div>
      ${aiItems.map(makeItem).join('')}
    </div>
    <div class="sidebar-footer">Powered by Groq · Llama 3.3</div>`;
}

function initSidebar(activePage) {
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) sidebar.innerHTML = buildSidebar(activePage);
}

// ─── Session Badge ────────────────────────────────────────────
function renderSessionBadge() {
  const el = document.getElementById('session-badge');
  if (!el) return;
  const id = Session.get();
  
  const theme = localStorage.getItem('ai_ba_theme') || 'dark';
  const themeToggle = `<button class="btn btn-ghost btn-sm" id="global-theme-toggle" title="Toggle Light/Dark Mode" style="font-size:14px;padding:4px 8px;margin-right:8px;line-height:1;">
    ${theme === 'dark' ? '☀️' : '🌙'}
  </button>`;
  
  let statusHtml = '';
  if (id) {
    statusHtml = `<span class="status-dot">Dataset loaded</span>
      <button class="btn btn-ghost btn-sm" onclick="Session.clear();location.reload();">Clear</button>`;
  } else {
    statusHtml = `<span class="status-dot inactive">No dataset</span>
      <a href="/upload.html" class="btn btn-secondary btn-sm">Upload →</a>`;
  }
  
  el.innerHTML = themeToggle + statusHtml;
  
  const toggleBtn = el.querySelector('#global-theme-toggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', toggleTheme);
  }
}

// ─── UI Helpers ───────────────────────────────────────────────
function showLoading(el, msg = 'Loading…') {
  el.innerHTML = `<div class="loading-state"><div class="spinner"></div><span>${msg}</span></div>`;
}

// ─── Alert Injection ──────────────────────────────────────────
function showAlert(el, type, msg) {
  el.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
}

document.addEventListener('DOMContentLoaded', () => {
  renderSessionBadge();
});
