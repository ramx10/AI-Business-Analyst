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

  // User bubble
  const userBubble = document.createElement('div');
  userBubble.className = 'chat-bubble user';
  userBubble.innerHTML = `
    <div class="chat-avatar user">Q</div>
    <div class="chat-body user">
      <div>${escapeHtml(question)}</div>
      <div class="chat-meta">${ts}</div>
    </div>`;
  chatMessages.appendChild(userBubble);

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

async function askQuestion(question) {
  if (!question.trim()) return;

  const sid = Session.get();
  if (!sid) {
    Toast.show('Please upload a dataset first.', 'error');
    return;
  }

  askBtn.disabled = true;
  askBtn.textContent = 'Thinking…';

  // Add message optimistically
  addMessage(question, { answer: 'Analyzing…', confidence: 'low', chart: null });

  try {
    const result = await API.post('/api/query', { session_id: sid, question: question.trim() });
    // Remove the optimistic message and replace with real one
    const msgs = chatMessages.querySelectorAll('.chat-bubble');
    if (msgs.length >= 2) {
      msgs[msgs.length - 1].remove(); // remove optimistic AI
      msgs[msgs.length - 2].remove(); // remove user bubble
    }
    addMessage(question, result);
  } catch (e) {
    // Show error in the last (optimistic) AI message
    const msgs = chatMessages.querySelectorAll('.chat-bubble');
    const lastAi = msgs[msgs.length - 1];
    if (lastAi && lastAi.classList.contains('ai')) {
      const body = lastAi.querySelector('.chat-body');
      if (body) {
        body.innerHTML = `<div style="color:var(--red);">${escapeHtml(e.message)}</div>`;
      }
    }
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
