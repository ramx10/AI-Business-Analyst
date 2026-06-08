// ─── Theme Management ──────────────────────────────────────────
(function() {
  const savedTheme = localStorage.getItem('ai_ba_theme') || 'light-corporate';
  document.documentElement.setAttribute('data-theme', savedTheme);
})();

// ─── Authentication Routing ──────────────────────────────────
(function() {
  const urlParams = new URLSearchParams(window.location.search);
  const tokenFromUrl = urlParams.get('token');
  if (tokenFromUrl) {
    localStorage.setItem('auth_token', tokenFromUrl);
    // Strip token from URL
    const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
    window.history.replaceState({path: cleanUrl}, '', cleanUrl);
  }

  const path = window.location.pathname;
  const isLoginPage = path.endsWith('login.html');
  const token = localStorage.getItem('auth_token');
  
  if (!token && !isLoginPage) {
    window.location.href = '/login.html';
  } else if (token && isLoginPage) {
    window.location.href = '/index.html';
  }
})();


function toggleTheme() {
  const current = localStorage.getItem('ai_ba_theme') || 'light-corporate';
  const next = current === 'dark' ? 'light-corporate' : 'dark';
  localStorage.setItem('ai_ba_theme', next);
  document.documentElement.setAttribute('data-theme', next);
  
  const isDark = next === 'dark';
  document.querySelectorAll('.theme-toggle-label').forEach(el => el.textContent = isDark ? 'Light' : 'Dark');
  document.querySelectorAll('#global-theme-toggle').forEach(btn => btn.title = `Switch to ${isDark ? 'Light' : 'Dark'} Mode`);
  
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
    { href: '/visualize.html', icon: '⧉',  label: 'Visualize', badge: '4',   page: 'visualize' },
    { href: '/dashboard.html', icon: '▣',  label: 'Dashboard', badge: '5',   page: 'dashboard' },
  ];
  const aiItems = [
    { href: '/insights.html',  icon: '◉',  label: 'Insights',  badge: '6',   page: 'insights' },
    { href: '/report.html',    icon: '⊡',  label: 'Report',    badge: '7',   page: 'report' },
  ];
  const settingsItem = { href: '/settings.html',  icon: '⚙',  label: 'Settings',  badge: null,  page: 'settings' };

  const makeItem = item => {
    const isActive = item.page === activePage;
    return `<a class="nav-item${isActive ? ' active' : ''}" href="${item.href}">
      <span class="nav-icon">${item.icon}</span>${item.label}
      ${item.badge ? `<span class="nav-badge">${item.badge}</span>` : ''}
    </a>`;
  };

  const theme = localStorage.getItem('ai_ba_theme') || 'light-corporate';
  const profileHtml = (theme === 'superieur-admin' || theme === 'study-admin' || theme === 'server-admin') ? `
    <div class="sidebar-profile">
      <div class="sidebar-profile-avatar">👤</div>
      <div class="sidebar-profile-info">
        <span class="sidebar-profile-name">Samuel Brue</span>
        <span class="sidebar-profile-email">samuel@gmail.com</span>
      </div>
    </div>
  ` : '';

  return `
    <div class="sidebar-header" onclick="window.location='/index.html'">
      <div class="logo-mark">A</div>
      <span class="workspace-name">AI Business Analyst</span>
      <span class="chevron">⌄</span>
    </div>
    ${profileHtml}
    <div class="nav-section">${navItems.map(makeItem).join('')}</div>
    <div class="nav-section">
      <div class="nav-section-label">AI Pipeline</div>
      ${aiItems.map(makeItem).join('')}
    </div>
    <div class="nav-section">${makeItem(settingsItem)}</div>
    <div class="sidebar-footer">Powered by Groq · Llama 3.3</div>`;
}

function initSidebar(activePage) {
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) {
    sidebar.innerHTML = buildSidebar(activePage);
    window.addEventListener('theme-changed', () => {
      sidebar.innerHTML = buildSidebar(activePage);
    });
  }
}

// ─── Session Badge ────────────────────────────────────────────
function renderSessionBadge() {
  const el = document.getElementById('session-badge');
  if (!el) return;
  const id = Session.get();
  
  const theme = localStorage.getItem('ai_ba_theme') || 'light-corporate';
  const isDark = theme === 'dark';
  const themeToggle = `<button class="theme-toggle-btn" id="global-theme-toggle" title="Switch to ${isDark ? 'Light' : 'Dark'} Mode">
    <span class="theme-toggle-label">${isDark ? 'Light' : 'Dark'}</span>
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

// ─── Authentication & Settings ───────────────────────────────
const SPRING_BOOT_BACKEND = 'http://localhost:8081'; // Change this port if port 8080 is in use (e.g., by Jenkins)

const Auth = {
  getToken() { return localStorage.getItem('auth_token'); },
  setToken(token) { localStorage.setItem('auth_token', token); },
  clearToken() { localStorage.removeItem('auth_token'); },
  getHeaders() {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
};

function handleGoogleLogin() {
  // Redirect to Spring Boot OAuth2 entrypoint
  window.location.href = `${SPRING_BOOT_BACKEND}/oauth2/authorization/google`;
}

function handleLogout() {
  Auth.clearToken();
  location.reload();
}

async function initSettings() {
  // 1. Check for token in URL (redirect from Spring Boot)
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');
  if (token) {
    Auth.setToken(token);
    window.history.replaceState({}, document.title, window.location.pathname);
  }

  const authPanel = document.getElementById('auth-panel');
  const historyContainer = document.getElementById('history-container');
  if (!authPanel || !historyContainer) return;

  let user = null;
  let historyData = [];
  let isDemo = false;

  // 2. Try fetching from Spring Boot API
  try {
    const headers = Auth.getHeaders();
    if (headers.Authorization) {
      // Fetch user profile
      const userRes = await fetch(`${SPRING_BOOT_BACKEND}/api/user/profile`, { headers });
      if (userRes.ok) {
        user = await userRes.json();
      } else if (userRes.status === 401) {
        Auth.clearToken();
        window.location.href = '/login.html';
        return;
      }
      
      // Fetch history
      const historyRes = await fetch(`${SPRING_BOOT_BACKEND}/api/user/dashboards/history`, { headers });
      if (historyRes.ok) {
        historyData = await historyRes.json();
      } else if (historyRes.status === 401) {
        Auth.clearToken();
        window.location.href = '/login.html';
        return;
      }
    }
  } catch (err) {
    console.warn("Spring Boot backend offline or unauthorized. Falling back to Demo Mode.", err);
    isDemo = true;
  }

  // 3. Render Auth Panel
  if (user) {
    authPanel.innerHTML = `
      <div class="profile-card">
        <img class="profile-avatar" src="${user.pictureUrl || 'https://lh3.googleusercontent.com/a/default-user'}" alt="Avatar" />
        <div class="profile-name">${user.name || 'AI Analyst User'}</div>
        <div class="profile-email">${user.email}</div>
        <button class="btn btn-danger btn-lg" onclick="handleLogout()" style="width: 100%">Sign Out</button>
      </div>
    `;
  } else {
    authPanel.innerHTML = `
      <div style="text-align: center; padding: 24px;">
        <div style="font-size: 40px; margin-bottom: 16px;">👤</div>
        <h3 style="margin-bottom: 10px; font-size: 14px;">Sign in Required</h3>
        <p style="color: var(--text-secondary); font-size: 12px; margin-bottom: 24px; line-height: 1.5;">
          Connect your Google account to sync your datasets, analysis reports, and dashboards across devices.
        </p>
        <button class="oauth-btn" onclick="handleGoogleLogin()">
          <svg class="google-logo" viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 8px;">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.56-2.77c-.98.66-2.23 1.06-3.72 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22-.03-.63z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
          </svg>
          Sign in with Google
        </button>
      </div>
    `;
  }

  // 4. Render Dashboard History
  if (isDemo) {
    historyData = [
      { id: 1, datasetName: "sales_data_may_2026.csv", rowCount: 12450, cleaningSummary: "Cleaned 12 empty cells, parsed 2 date columns", createdAt: "2026-05-28T14:30:00Z" },
      { id: 2, datasetName: "customer_churn_q1.csv", rowCount: 3200, cleaningSummary: "Handled outlier values in age column", createdAt: "2026-05-15T09:15:00Z" },
      { id: 3, datasetName: "product_inventory_v2.csv", rowCount: 8910, cleaningSummary: "Removed duplicate rows, filled missing prices", createdAt: "2026-04-30T16:45:00Z" }
    ];
  }
  
  if (historyData.length === 0 && !isDemo) {
    historyContainer.innerHTML = `
      <div style="padding: 24px; text-align: center; color: var(--text-tertiary); font-size: 13px;">
        No dashboards generated yet. Upload a dataset to get started.
      </div>
    `;
    return;
  }

  const last3 = historyData.slice(0, 3);
  
  historyContainer.innerHTML = last3.map(item => `
    <div class="history-item">
      <div class="history-info">
        <div class="history-title">${item.datasetName}</div>
        <div class="history-meta">
          <span>${item.rowCount.toLocaleString()} rows</span>
          <span class="history-date">${new Date(item.createdAt).toLocaleDateString()}</span>
        </div>
      </div>
      <button class="btn btn-secondary btn-sm" onclick="loadDashboardFromHistory(${item.id})">Load</button>
    </div>
  `).join('');

  if (isDemo) {
    historyContainer.innerHTML += `
      <div style="font-size: 11px; color: var(--text-tertiary); text-align: center; margin-top: 8px;">
        Displaying demo history (Spring Boot backend offline).
      </div>
    `;
  }
}

function loadDashboardFromHistory(id) {
  Session.set(`mock_session_${id}`);
  alert(`Loaded dashboard state for session ID: ${id}`);
  window.location.href = '/dashboard.html';
}

document.addEventListener('DOMContentLoaded', () => {
  renderSessionBadge();
  if (document.getElementById('auth-panel')) {
    initSettings();
  }
});
