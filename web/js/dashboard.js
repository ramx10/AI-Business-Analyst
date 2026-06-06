// ─── Chart Theme Manager ───────────────────────────────────────
window.chartInstances = {};

function getThemeConfig() {
  const theme = document.documentElement.getAttribute('data-theme') || 'dark';
  
  if (theme === 'light-corporate') {
    const palette = ['#2563eb', '#4f46e5', '#0d9488', '#d97706', '#dc2626', '#06b6d4', '#475569'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '33'),
      gridColor: 'rgba(15, 23, 42, 0.06)',
      textColor: '#475569',
      tooltipBg: '#ffffff',
      tooltipText: '#0f172a',
      tooltipBorder: '#cbd5e1'
    };
  } else if (theme === 'pastel-soft') {
    const palette = ['#e19584', '#e2a3c7', '#93b7be', '#b5ca8d', '#d9a05b', '#a3b5c7', '#d0b3e1'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '55'),
      gridColor: 'rgba(110, 97, 80, 0.06)',
      textColor: '#6e6150',
      tooltipBg: '#ffffff',
      tooltipText: '#2d261e',
      tooltipBorder: '#e9e3d5'
    };
  } else {
    // Default Dark
    const palette = ['#7c3aed', '#2563eb', '#059669', '#d97706', '#dc2626', '#0891b2', '#4f46e5'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '55'),
      gridColor: 'rgba(255,255,255,0.03)',
      textColor: '#71717a',
      tooltipBg: '#111111',
      tooltipText: '#e4e4e7',
      tooltipBorder: '#222222'
    };
  }
}

function getBaseOpts(cfg) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 500 },
    plugins: {
      legend: {
        labels: { color: cfg.textColor, font: { family: 'Inter', size: 11 }, boxWidth: 10, padding: 14 }
      },
      tooltip: {
        backgroundColor: cfg.tooltipBg,
        titleColor: cfg.tooltipText,
        bodyColor: cfg.textColor,
        borderColor: cfg.tooltipBorder,
        borderWidth: 1,
        padding: 10,
        cornerRadius: 6,
      }
    },
    scales: {
      x: {
        grid: { color: cfg.gridColor, drawBorder: false },
        ticks: { color: cfg.textColor, font: { family: 'Inter', size: 11 } }
      },
      y: {
        grid: { color: cfg.gridColor, drawBorder: false },
        ticks: { color: cfg.textColor, font: { family: 'Inter', size: 11 } }
      }
    }
  };
}

function makeLineChart(id, labels, data) {
  const ctx = document.getElementById(id); if (!ctx) return;
  if (window.chartInstances[id]) { window.chartInstances[id].destroy(); }
  
  const cfg = getThemeConfig();
  const baseOpts = getBaseOpts(cfg);
  
  window.chartInstances[id] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data,
        borderColor: cfg.palette[0],
        backgroundColor: cfg.palette[0] + '18',
        fill: true,
        tension: 0.35,
        pointRadius: 2,
        pointHoverRadius: 5,
        pointBackgroundColor: cfg.palette[0],
        borderWidth: 2
      }]
    },
    options: { ...baseOpts, plugins: { ...baseOpts.plugins, legend: { display: false } } }
  });
}

function makeBarChart(id, labels, data, horizontal = false) {
  const ctx = document.getElementById(id); if (!ctx) return;
  if (window.chartInstances[id]) { window.chartInstances[id].destroy(); }
  
  const cfg = getThemeConfig();
  const baseOpts = getBaseOpts(cfg);
  
  window.chartInstances[id] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: cfg.paletteMuted,
        borderColor: cfg.palette,
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false
      }]
    },
    options: {
      ...baseOpts,
      indexAxis: horizontal ? 'y' : 'x',
      plugins: { ...baseOpts.plugins, legend: { display: false } }
    }
  });
}

function makeDoughnutChart(id, labels, data) {
  const ctx = document.getElementById(id); if (!ctx) return;
  if (window.chartInstances[id]) { window.chartInstances[id].destroy(); }
  
  const cfg = getThemeConfig();
  const baseOpts = getBaseOpts(cfg);
  const isDark = document.documentElement.getAttribute('data-theme') !== 'light-corporate' && 
                 document.documentElement.getAttribute('data-theme') !== 'pastel-soft';
  
  window.chartInstances[id] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: cfg.palette,
        borderColor: isDark ? '#111111' : '#ffffff',
        borderWidth: 2,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      animation: { duration: 500 },
      plugins: {
        legend: {
          position: 'right',
          labels: { color: cfg.textColor, font: { family: 'Inter', size: 11 }, padding: 14, boxWidth: 10 }
        },
        tooltip: baseOpts.plugins.tooltip
      }
    }
  });
}

function makeScatterChart(id, xData, yData, labels) {
  const ctx = document.getElementById(id); if (!ctx) return;
  if (window.chartInstances[id]) { window.chartInstances[id].destroy(); }
  
  const cfg = getThemeConfig();
  const baseOpts = getBaseOpts(cfg);
  const points = xData.map((x, i) => ({ x, y: yData[i], label: labels[i] }));
  
  window.chartInstances[id] = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        data: points,
        backgroundColor: cfg.palette[0] + '99',
        borderColor: cfg.palette[0],
        pointRadius: 6,
        pointHoverRadius: 9,
        borderWidth: 1
      }]
    },
    options: {
      ...baseOpts,
      plugins: {
        ...baseOpts.plugins,
        legend: { display: false },
        tooltip: {
          ...baseOpts.plugins.tooltip,
          callbacks: {
            label: ctx => ` ${ctx.raw.label}  Rev: ${ctx.raw.x.toLocaleString()}  Profit: ${ctx.raw.y.toLocaleString()}`
          }
        }
      }
    }
  });
}
