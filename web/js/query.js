// ─── NL Query Page Logic ──────────────────────────────────────

const chatMessages = document.getElementById('chat-messages');
const emptyState = document.getElementById('empty-state');
const questionInput = document.getElementById('question-input');
const askBtn = document.getElementById('ask-btn');
const examplesBar = document.getElementById('examples-bar');

let chartInstances = {};

function getThemeColors() {
  const theme = document.documentElement.getAttribute('data-theme') || 'light-corporate';
  const isDark = theme === 'dark';
  return {
    textColor: isDark ? '#e4e4e7' : '#475569',
    gridColor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(15,23,42,0.06)',
    palette: isDark
      ? ['#7c3aed', '#22c55e', '#eab308', '#ef4444', '#3b82f6', '#06b6d4', '#f97316']
      : ['#2563eb', '#4f46e5', '#0d9488', '#d97706', '#dc2626', '#06b6d4', '#475569'],
  };
}

function renderChart(containerId, chartData) {
  if (!chartData || !chartData.type || !chartData.labels || !chartData.values) return;

  const existing = document.getElementById(containerId);
  if (existing) existing.remove();

  const colors = getThemeColors();
  const wrapper = document.createElement('div');
  wrapper.id = containerId;
  wrapper.className = 'chart-card';
  wrapper.innerHTML = `<h4>${chartData.title || ''}</h4><canvas></canvas>`;
  document.getElementById(containerId.replace('chart-', 'msg-')).querySelector('.chat-body').appendChild(wrapper);

  const ctx = wrapper.querySelector('canvas').getContext('2d');
  const chartId = containerId;

  if (chartInstances[chartId]) {
    chartInstances[chartId].destroy();
  }

  const isDarkOrPastel = document.documentElement.getAttribute('data-theme') === 'dark';

  if (chartData.type === 'number') {
    const numVal = chartData.values[0];
    wrapper.innerHTML = `
      <h4>${chartData.title || ''}</h4>
      <div style="font-size:32px;font-weight:700;color:var(--accent);padding:8px 0;">
        ${typeof numVal === 'number' ? numVal.toLocaleString() : numVal}
      </div>`;
    return;
  }

  const commonOpts = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        labels: { color: colors.textColor, font: { size: 11, family: 'Inter' } },
      },
    },
    scales: chartData.type === 'pie' || chartData.type === 'doughnut' ? undefined : {
      x: {
        ticks: { color: colors.textColor, font: { size: 10, family: 'Inter' }, maxRotation: 45 },
        grid: { color: colors.gridColor },
      },
      y: {
        ticks: { color: colors.textColor, font: { size: 10, family: 'Inter' } },
        grid: { color: colors.gridColor },
      },
    },
  };

  if (chartData.type === 'bar') {
    chartInstances[chartId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: chartData.labels,
        datasets: [{
          label: chartData.dataset_label || 'Value',
          data: chartData.values,
          backgroundColor: colors.palette.map(c => c + '80'),
          borderColor: colors.palette,
          borderWidth: 1,
          borderRadius: 4,
        }],
      },
      options: commonOpts,
    });
  } else if (chartData.type === 'line') {
    chartInstances[chartId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: chartData.labels,
        datasets: [{
          label: chartData.dataset_label || 'Value',
          data: chartData.values,
          borderColor: colors.palette[0],
          backgroundColor: colors.palette[0] + '20',
          fill: true,
          tension: 0.3,
          pointRadius: 3,
          pointBackgroundColor: colors.palette[0],
        }],
      },
      options: commonOpts,
    });
  } else if (chartData.type === 'pie' || chartData.type === 'doughnut') {
    chartInstances[chartId] = new Chart(ctx, {
      type: chartData.type === 'doughnut' ? 'doughnut' : 'pie',
      data: {
        labels: chartData.labels,
        datasets: [{
          data: chartData.values,
          backgroundColor: colors.palette,
          borderColor: isDarkOrPastel ? '#111111' : '#ffffff',
          borderWidth: 2,
        }],
      },
      options: commonOpts,
    });
  } else if (chartData.type === 'table') {
    let rows = chartData.labels.map((l, i) =>
      `<tr><td style="padding:6px 10px;border-bottom:1px solid var(--border);font-size:13px;">${l}</td>
       <td style="padding:6px 10px;border-bottom:1px solid var(--border);font-size:13px;text-align:right;font-weight:600;">${chartData.values[i]?.toLocaleString() || ''}</td></tr>`
    ).join('');
    wrapper.innerHTML += `
      <div class="table-wrap"><table style="width:100%;">
        <thead><tr><th style="padding:8px 10px;text-align:left;font-size:12px;">Item</th>
        <th style="padding:8px 10px;text-align:right;font-size:12px;">Value</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>`;
  }
}

function addMessage(question, result) {
  emptyState?.remove();

  const confidence = result.confidence || 'low';
  const answer = result.answer || 'No answer returned.';
  const chart = result.chart;

  const ts = new Date().toLocaleTimeString();
  const msgId = 'msg-' + Date.now();

  // AI bubble
  const aiBubble = document.createElement('div');
  aiBubble.className = 'chat-bubble ai';
  aiBubble.id = msgId;
  aiBubble.innerHTML = `
    <div class="chat-avatar ai">A</div>
    <div class="chat-body">
      <div>${escapeHtml(answer)}</div>
      <div class="chat-meta">
        <span class="chat-confidence ${confidence}">${confidence}</span>
        <span style="margin-left:8px;">${ts}</span>
      </div>
    </div>`;
  chatMessages.appendChild(aiBubble);

  // Render chart if applicable
  if (chart && chart.type && chart.labels && chart.values && chart.type !== 'table') {
    const chartId = 'chart-' + Date.now();
    renderChart(chartId, chart);
  }

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

function showTypingIndicator() {
  const el = document.createElement('div');
  el.className = 'chat-bubble ai typing-indicator-wrapper';
  el.innerHTML = `
    <div class="chat-avatar ai">A</div>
    <div class="typing-indicator">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>`;
  chatMessages.appendChild(el);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return el;
}

function removeTypingIndicator() {
  const el = chatMessages.querySelector('.typing-indicator-wrapper');
  if (el) el.remove();
}

async function askQuestion(question) {
  if (!question.trim()) return;

  const sid = Session.get();
  if (!sid) {
    Toast.show('Please upload a dataset first.', 'error');
    return;
  }

  askBtn.disabled = true;
  askBtn.textContent = 'Thinking…';

  // User bubble
  emptyState?.remove();
  const userBubble = document.createElement('div');
  userBubble.className = 'chat-bubble user';
  const ts = new Date().toLocaleTimeString();
  userBubble.innerHTML = `
    <div class="chat-avatar user">Q</div>
    <div class="chat-body user">
      <div>${escapeHtml(question.trim())}</div>
      <div class="chat-meta">${ts}</div>
    </div>`;
  chatMessages.appendChild(userBubble);

  // Typing indicator
  const typingEl = showTypingIndicator();

  try {
    const result = await API.post('/api/query', { session_id: sid, question: question.trim() });
    removeTypingIndicator();
    addMessage(question, result);
  } catch (e) {
    removeTypingIndicator();
    // Show error in a new AI bubble
    const errorBubble = document.createElement('div');
    errorBubble.className = 'chat-bubble ai';
    errorBubble.innerHTML = `
      <div class="chat-avatar ai">A</div>
      <div class="chat-body">
        <div style="color:var(--red);display:flex;align-items:center;gap:8px;">
          <span>${Icons.warning}</span>
          <span>${escapeHtml(e.message)}</span>
        </div>
      </div>`;
    chatMessages.appendChild(errorBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  } finally {
    askBtn.disabled = false;
    askBtn.textContent = 'Ask';
    questionInput.focus();
  }
}

// ─── Event Handlers ───────────────────────────────────────────

askBtn.addEventListener('click', () => {
  const q = questionInput.value.trim();
  if (q) { questionInput.value = ''; askQuestion(q); }
});

questionInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    const q = questionInput.value.trim();
    if (q) { questionInput.value = ''; askQuestion(q); }
  }
});

examplesBar.addEventListener('click', e => {
  const chip = e.target.closest('.example-chip');
  if (chip) {
    const q = chip.getAttribute('data-q');
    if (q) askQuestion(q);
  }
});

document.addEventListener('theme-changed', () => {
  // Re-render all chart instances with new colors
  Object.keys(chartInstances).forEach(id => {
    if (chartInstances[id]) {
      const colors = getThemeColors();
      const chart = chartInstances[id];
      if (chart.options.scales) {
        if (chart.options.scales.x) {
          chart.options.scales.x.ticks.color = colors.textColor;
          chart.options.scales.x.grid.color = colors.gridColor;
        }
        if (chart.options.scales.y) {
          chart.options.scales.y.ticks.color = colors.textColor;
          chart.options.scales.y.grid.color = colors.gridColor;
        }
      }
      chart.options.plugins.legend.labels.color = colors.textColor;
      chart.update();
    }
  });
});
