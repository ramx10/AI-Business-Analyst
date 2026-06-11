// ─── SVG Icons Definition ─────────────────────────────────────
window.Icons = {
  overview: '<svg viewBox="0 0 20 20" fill="currentColor"><rect x="2" y="2" width="7" height="7" rx="1.5"/><rect x="11" y="2" width="7" height="7" rx="1.5"/><rect x="2" y="11" width="7" height="7" rx="1.5"/><rect x="11" y="11" width="7" height="7" rx="1.5"/></svg>',
  upload: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M10 13V4M10 4L6 8M10 4L14 8"/><path d="M3 14v2a2 2 0 002 2h10a2 2 0 002-2v-2"/></svg>',
  schema: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="14" height="14" rx="1.5"/><path d="M3 7h14M7 3v14" stroke-width="1.5"/></svg>',
  clean: '<svg viewBox="0 0 20 20" fill="currentColor"><path d="M10 2l1.5 4.5L16 8l-4.5 1.5L10 14l-1.5-4.5L4 8l4.5-1.5L10 2z"/><path d="M6 14l1 2 1-2 2 1-1-2 2-1-2-1 1-2-2 1-1-2-1 2-2-1 1 2-2 1 2 1-1 2 2-1z"/></svg>',
  pipeline: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="5" cy="5" r="2" fill="currentColor" stroke="none"/><circle cx="15" cy="5" r="2" fill="currentColor" stroke="none"/><circle cx="10" cy="15" r="2" fill="currentColor" stroke="none"/><path d="M7 5h6M10 7v6"/></svg>',
  visualize: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><rect x="3" y="10" width="3" height="7" rx="1"/><rect x="8.5" y="5" width="3" height="12" rx="1"/><rect x="14" y="3" width="3" height="14" rx="1"/></svg>',
  dashboard: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="7" height="7" rx="1"/><rect x="11" y="2" width="7" height="7" rx="1"/><rect x="2" y="11" width="7" height="7" rx="1"/><rect x="11" y="11" width="7" height="7" rx="1"/></svg>',
  compare: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M7 4l-4 6h8l-4 6M13 4l-4 6h8l-4 6" opacity="0.4"/></svg>',
  governance: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2l7 3v5c0 4-3.5 7-7 8-3.5-1-7-4-7-8V5l7-3z"/><path d="M7.5 10.5l1.5 1.5 3.5-3.5" stroke-width="1.2"/></svg>',
  lineage: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="4" cy="4" r="2" fill="currentColor" stroke="none"/><circle cx="16" cy="4" r="2" fill="currentColor" stroke="none"/><circle cx="10" cy="10" r="2" fill="currentColor" stroke="none"/><circle cx="4" cy="16" r="2" fill="currentColor" stroke="none"/><circle cx="16" cy="16" r="2" fill="currentColor" stroke="none"/><path d="M6 6l4 2M14 6l-4 2M4 14l6-2M16 14l-6-2"/></svg>',
  share: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="5" cy="10" r="2.5" fill="currentColor" stroke="none"/><circle cx="15" cy="4" r="2.5" fill="currentColor" stroke="none"/><circle cx="15" cy="16" r="2.5" fill="currentColor" stroke="none"/><path d="M7 11l6 4M7 9l6-4"/></svg>',
  schedules: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="10" cy="10" r="7"/><path d="M10 6v4l3 3" stroke-linecap="round"/></svg>',
  nlq: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M3 10c0-3.3 3.1-6 7-6s7 2.7 7 6-3.1 6-7 6c-.8 0-1.6-.1-2.3-.3L5 18l1.5-3.3C4.5 13.5 3 11.9 3 10z"/></svg>',
  plugins: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2v2h2a2 2 0 012 2v2h-2v-2h-2v2a2 2 0 01-2 2h-2v2h2a2 2 0 012 2v2h2v-2h2v2a2 2 0 01-2 2h-2v2H8v-2H6a2 2 0 01-2-2v-2h2v2h2v-2a2 2 0 012-2h2v-2h-2a2 2 0 01-2-2V6H6v2H4V6a2 2 0 012-2h2V2z"/></svg>',
  insights: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2l1.5 4.5L14 8l-4.5 1.5L8 14l-1.5-4.5L2 8l4.5-1.5L8 2z"/><path d="M11 12l-1 3 1 3M14 11l.5 2.5L17 14l-2.5 1.5L14 18l-1.5-2.5L10 14l2.5-1.5L14 11z"/></svg>',
  report: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 2h7l4 4v12a1 1 0 01-1 1H5a1 1 0 01-1-1V3a1 1 0 011-1z"/><path d="M12 2v4h4M7 11h6M7 14h4"/></svg>',
  settings: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="10" cy="10" r="2.5"/><path d="M10 1.5v2M10 16.5v2M1.5 10h2M16.5 10h2M3.5 3.5l1.4 1.4M15.1 15.1l1.4 1.4M3.5 16.5l1.4-1.4M15.1 4.9l1.4-1.4"/></svg>',
  chevron_down: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 8l4 4 4-4"/></svg>',
  arrow_right: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 10h12M11 5l5 5-5 5"/></svg>',
  arrow_left: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M16 10H4M9 5l-5 5 5 5"/></svg>',
  download: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M10 3v9M6 8l4 4 4-4"/><path d="M3 15v2a2 2 0 002 2h10a2 2 0 002-2v-2"/></svg>',
  search: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="9" cy="9" r="5.5"/><path d="M13 13l4 4"/></svg>',
  check: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10l4 4 8-8"/></svg>',
  close: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 5l10 10M15 5L5 15"/></svg>',
  warning: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2L2 18h16L10 2z"/><path d="M10 8v4M10 14v1"/></svg>',
  info: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="10" cy="10" r="7"/><path d="M10 9v5M10 6.5v.5" stroke-linecap="round"/></svg>',
  user: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="10" cy="7" r="3.5"/><path d="M3 18c0-4 3-7 7-7s7 3 7 7"/></svg>',
  upload_zone: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M24 32V12M24 12l-6 6M24 12l6 6"/><path d="M8 36v4a4 4 0 004 4h24a4 4 0 004-4v-4"/></svg>',
};
const Icons = window.Icons;

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


function getLogoUrl() {
  const theme = localStorage.getItem('ai_ba_theme') || 'light-corporate';
  const darkThemes = ['dark', 'crypto-admin', 'aone-admin', 'crmi-admin'];
  if (darkThemes.includes(theme)) {
    return '/images/dark.png';
  }
  return '/images/light.png';
}

function updateLogos() {
  const logoUrl = getLogoUrl();
  document.querySelectorAll('img.logo-mark, img.login-logo').forEach(img => {
    img.src = logoUrl;
  });
}

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
  updateLogos();
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
    const sep = path.includes('?') ? '&' : '?';
    const r = await fetch(`${path}${sep}_t=${Date.now()}`);
    const body = await r.text();
    if (!r.ok) {
      let msg = `HTTP ${r.status}`;
      try { const e = JSON.parse(body); msg = e.detail || msg; } catch (_) { msg = body.slice(0, 200) || msg; }
      throw new Error(msg);
    }
    if (!body) throw new Error(`Server returned empty body (HTTP ${r.status})`);
    return JSON.parse(body);
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
    { href: '/index.html',     icon: 'overview',    label: 'Overview',           badge: null, page: 'index',     sym: '\u2261' },
    { href: '/upload.html',    icon: 'upload',      label: 'Upload Data',        badge: '1',  page: 'upload',   sym: '\u2794' },
    { href: '/schema.html',    icon: 'schema',      label: 'Schema',             badge: '2',  page: 'schema',   sym: '\u2261' },
    { href: '/clean.html',     icon: 'clean',       label: 'Cleaning',           badge: '3',  page: 'clean',    sym: '\u25C8' },
    { href: '/visualize.html', icon: 'visualize',   label: 'Visualize',          badge: '4',  page: 'visualize',sym: '\u25A3' },
    { href: '/dashboard.html', icon: 'dashboard',   label: 'Dashboard',          badge: '5',  page: 'dashboard',sym: '\u25C9' },
    { href: '/smart-dashboard.html', icon: 'insights',   label: 'Smart Dashboard', badge: null,  page: 'smart-dashboard',sym: '\u2726' },
    { href: '/compare.html',   icon: 'compare',     label: 'Compare Datasets',   badge: null, page: 'compare',  sym: '\u29C9' },
    { href: '/governance.html',icon: 'governance',  label: 'Governance',         badge: null, page: 'governance',sym: '\u22A1' },
    { href: '/lineage.html',   icon: 'lineage',     label: 'Lineage',            badge: null, page: 'lineage',  sym: '\u21BB' },
    { href: '/share-manage.html', icon: 'share',    label: 'Share',              badge: null, page: 'share-manage',sym: '\u2192' },
    { href: '/scheduled-reports.html', icon: 'schedules', label: 'Schedules',    badge: null, page: 'scheduled-reports',sym: '\u21BB' },
    { href: '/query.html',     icon: 'nlq',         label: 'NL Query',           badge: null, page: 'query',    sym: '\u2726' },
    { href: '/plugins.html',   icon: 'plugins',     label: 'Plugins',            badge: null, page: 'plugins',  sym: '\u25C8' },
  ];
  const aiItems = [
    { href: '/insights.html',  icon: 'insights',    label: 'Insights',           badge: '6',  page: 'insights', sym: '\u25C9' },
    { href: '/report.html',    icon: 'report',      label: 'Report',             badge: '7',  page: 'report',   sym: '\u22A1' },
  ];
  const settingsItem = { href: '/settings.html',  icon: 'settings',  label: 'Settings',  badge: null,  page: 'settings', sym: '\u2726' };

  const makeItem = item => {
    const isActive = item.page === activePage;
    return `<a class="nav-item${isActive ? ' active' : ''}" href="${item.href}">
      <span class="nav-icon">${Icons[item.icon] || ''}</span>
      <span class="nav-label">${item.label}</span>
      ${item.badge ? `<span class="nav-badge">${item.badge}</span>` : ''}
    </a>`;
  };

  const savedTemplate = localStorage.getItem('ai_ba_template') || '';
  const userProfileStr = localStorage.getItem('user_profile');
  let userName = 'Guest User';
  let userEmail = 'guest@example.com';
  let userAvatarHtml = Icons.user;
  
  if (userProfileStr) {
    try {
      const userProfile = JSON.parse(userProfileStr);
      userName = userProfile.name || userName;
      userEmail = userProfile.email || userEmail;
      if (userProfile.pictureUrl) {
        userAvatarHtml = `<img src="${userProfile.pictureUrl}" alt="Avatar" />`;
      }
    } catch (e) {
      console.error("Failed to parse cached user profile", e);
    }
  }

  const profileHtml = (savedTemplate === 'superieur-admin' || savedTemplate === 'study-admin' || savedTemplate === 'server-admin') ? `
    <div class="sidebar-profile">
      <div class="sidebar-profile-avatar">${userAvatarHtml}</div>
      <div class="sidebar-profile-info">
        <span class="sidebar-profile-name">${userName}</span>
        <span class="sidebar-profile-email">${userEmail}</span>
      </div>
    </div>
  ` : '';

  return `
    <div class="sidebar-header" onclick="window.location='/index.html'">
      <img class="logo-mark" src="${getLogoUrl()}" alt="A" onerror="this.outerHTML='<div class=&quot;logo-mark&quot;>A</div>'" style="object-fit: cover;">
      <span class="workspace-name">AI Business Analyst</span>
      <span class="chevron">${Icons.chevron_down}</span>
    </div>
    ${profileHtml}
    <div class="sidebar-scroll">
      <div class="nav-section">${navItems.map(makeItem).join('')}</div>
      <div class="nav-section">
        <div class="nav-section-label">AI Pipeline</div>
        ${aiItems.map(makeItem).join('')}
      </div>
      <div class="nav-section">${makeItem(settingsItem)}</div>
    </div>
    <div class="sidebar-footer">AI Business Analyst</div>`;
}

function initSidebar(activePage) {
  window.activePageGlobal = activePage;
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
      <a href="/upload.html" class="btn btn-secondary btn-sm">Upload ${Icons.arrow_right}</a>`;
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

// ─── Toast Notifications ──────────────────────────────────────
const Toast = {
  container: null,
  init() {
    if (document.getElementById('toast-container')) return;
    this.container = document.createElement('div');
    this.container.id = 'toast-container';
    Object.assign(this.container.style, {
      position: 'fixed', top: '16px', right: '16px', zIndex: '99999',
      display: 'flex', flexDirection: 'column', gap: '8px', maxWidth: '380px'
    });
    document.body.appendChild(this.container);
  },
  show(message, type = 'info', duration = 4000) {
    this.init();
    const el = document.createElement('div');
    const colors = {
      success: 'var(--green)', error: 'var(--red)', warning: 'var(--yellow)', info: 'var(--accent)'
    };
    const iconSvg = { success: Icons.check, error: Icons.close, warning: Icons.warning, info: Icons.info };
    el.innerHTML = `<div style="display:flex;align-items:center;gap:10px;padding:12px 16px;background:var(--bg-elevated);border:1px solid var(--border);border-left:3px solid ${colors[type]||'var(--accent)'};border-radius:var(--radius);box-shadow:0 8px 24px rgba(0,0,0,0.2);font-size:13px;color:var(--text-primary);animation:toastIn 0.25s ease-out;">
      <span style="width:18px;height:18px;flex-shrink:0">${iconSvg[type]||Icons.info}</span>
      <span style="flex:1">${message}</span>
    </div>`;
    this.container.appendChild(el);
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transition = 'opacity 0.3s ease';
      setTimeout(() => el.remove(), 300);
    }, duration);
  }
};

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
  localStorage.removeItem('user_profile');
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
        <div style="width:40px;height:40px;margin:0 auto 16px;color:var(--text-secondary);">${Icons.user}</div>
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

async function loadAndCacheUserProfile() {
  const token = localStorage.getItem('auth_token');
  if (!token || token === 'guest_user@example.com') {
    localStorage.setItem('user_profile', JSON.stringify({
      name: 'Guest User',
      email: 'guest@example.com',
      pictureUrl: ''
    }));
    return;
  }
  try {
    const headers = Auth.getHeaders();
    const userRes = await fetch(`${SPRING_BOOT_BACKEND}/api/user/profile`, { headers });
    if (userRes.ok) {
      const user = await userRes.json();
      const oldProfile = localStorage.getItem('user_profile');
      localStorage.setItem('user_profile', JSON.stringify(user));
      if (oldProfile !== JSON.stringify(user)) {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar && typeof window.activePageGlobal !== 'undefined') {
          sidebar.innerHTML = buildSidebar(window.activePageGlobal);
        }
      }
    }
  } catch (err) {
    console.warn("Failed to fetch user profile in background", err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateLogos();
  renderSessionBadge();
  if (document.getElementById('auth-panel')) {
    initSettings();
  }
  loadAndCacheUserProfile();
});
