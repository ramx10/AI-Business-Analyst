// ─── Chart Palette ────────────────────────────────────────────
const PALETTE = ['#7c3aed','#2563eb','#059669','#d97706','#dc2626','#0891b2','#7c3aed','#4f46e5'];
const PALETTE_MUTED = PALETTE.map(c => c + '55');

const BASE_OPTS = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 600 },
  plugins: {
    legend: {
      labels: { color: '#52525b', font: { family: 'Inter', size: 11 }, boxWidth: 10, padding: 14 }
    },
    tooltip: {
      backgroundColor: '#111111',
      titleColor: '#e4e4e7',
      bodyColor: '#71717a',
      borderColor: '#222222',
      borderWidth: 1,
      padding: 10,
      cornerRadius: 6,
    }
  },
  scales: {
    x: {
      grid: { color: 'rgba(255,255,255,0.03)', drawBorder: false },
      ticks: { color: '#52525b', font: { family: 'Inter', size: 11 } }
    },
    y: {
      grid: { color: 'rgba(255,255,255,0.03)', drawBorder: false },
      ticks: { color: '#52525b', font: { family: 'Inter', size: 11 } }
    }
  }
};

function makeLineChart(id, labels, data) {
  const ctx = document.getElementById(id); if (!ctx) return;
  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{ data, borderColor: PALETTE[0], backgroundColor: PALETTE[0]+'18',
        fill: true, tension: 0.35, pointRadius: 2, pointHoverRadius: 5,
        pointBackgroundColor: PALETTE[0], borderWidth: 2 }]
    },
    options: { ...BASE_OPTS, plugins: { ...BASE_OPTS.plugins, legend: { display: false } } }
  });
}

function makeBarChart(id, labels, data, horizontal = false) {
  const ctx = document.getElementById(id); if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ data, backgroundColor: PALETTE_MUTED, borderColor: PALETTE,
        borderWidth: 1, borderRadius: 4, borderSkipped: false }]
    },
    options: {
      ...BASE_OPTS,
      indexAxis: horizontal ? 'y' : 'x',
      plugins: { ...BASE_OPTS.plugins, legend: { display: false } }
    }
  });
}

function makeDoughnutChart(id, labels, data) {
  const ctx = document.getElementById(id); if (!ctx) return;
  new Chart(ctx, {
    type: 'doughnut',
    data: { labels, datasets: [{ data, backgroundColor: PALETTE, borderColor: '#111111', borderWidth: 2, hoverOffset: 6 }] },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: '68%',
      animation: { duration: 600 },
      plugins: {
        legend: { position: 'right', labels: { color: '#52525b', font: { family: 'Inter', size: 11 }, padding: 14, boxWidth: 10 } },
        tooltip: BASE_OPTS.plugins.tooltip
      }
    }
  });
}

function makeScatterChart(id, xData, yData, labels) {
  const ctx = document.getElementById(id); if (!ctx) return;
  const points = xData.map((x, i) => ({ x, y: yData[i], label: labels[i] }));
  new Chart(ctx, {
    type: 'scatter',
    data: { datasets: [{ data: points, backgroundColor: PALETTE[0]+'99', borderColor: PALETTE[0], pointRadius: 6, pointHoverRadius: 9, borderWidth: 1 }] },
    options: {
      ...BASE_OPTS,
      plugins: {
        ...BASE_OPTS.plugins,
        legend: { display: false },
        tooltip: {
          ...BASE_OPTS.plugins.tooltip,
          callbacks: { label: ctx => ` ${ctx.raw.label}  Rev: ${ctx.raw.x.toLocaleString()}  Profit: ${ctx.raw.y.toLocaleString()}` }
        }
      }
    }
  });
}
