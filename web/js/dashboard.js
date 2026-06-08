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
  } else if (theme === 'material-admin') {
    const palette = ['#3f51b5', '#009688', '#ff9800', '#00bcd4', '#e91e63', '#9c27b0', '#ff5722'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '33'),
      gridColor: 'rgba(0, 0, 0, 0.04)',
      textColor: '#616161',
      tooltipBg: '#ffffff',
      tooltipText: '#212121',
      tooltipBorder: '#e0e4ec'
    };
  } else if (theme === 'crypto-admin') {
    const palette = ['#00e5a0', '#ff4d6a', '#ffb000', '#7c3aed', '#00b8ff', '#ff3366', '#a5b4fc'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '55'),
      gridColor: 'rgba(255, 255, 255, 0.04)',
      textColor: '#8892a6',
      tooltipBg: '#131826',
      tooltipText: '#e8ecf4',
      tooltipBorder: '#1e2538'
    };
  } else if (theme === 'medi-admin') {
    const palette = ['#00a8a8', '#10b981', '#3b82f6', '#86efac', '#06b6d4', '#14b8a6', '#0284c7'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '33'),
      gridColor: 'rgba(26, 60, 52, 0.04)',
      textColor: '#4a7268',
      tooltipBg: '#ffffff',
      tooltipText: '#1a3c34',
      tooltipBorder: '#c5e0d6'
    };
  } else if (theme === 'minimal-pro') {
    const palette = ['#111111', '#555555', '#999999', '#777777', '#333333', '#dc2626', '#444444'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '22'),
      gridColor: 'rgba(0, 0, 0, 0.08)',
      textColor: '#555555',
      tooltipBg: '#ffffff',
      tooltipText: '#111111',
      tooltipBorder: '#111111'
    };
  } else if (theme === 'soft-material') {
    const palette = ['#8b5cf6', '#ff7e67', '#34d399', '#fb7185', '#60a5fa', '#f59e0b', '#ec4899'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '44'),
      gridColor: 'rgba(99, 102, 241, 0.04)',
      textColor: '#6366f1',
      tooltipBg: '#ffffff',
      tooltipText: '#1e1b4b',
      tooltipBorder: '#e9e5f5'
    };
  } else if (theme === 'aone-admin') {
    const palette = ['#38bdf8', '#34d399', '#f87171', '#fbbf24', '#a78bfa', '#ec4899', '#60a5fa'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '55'),
      gridColor: 'rgba(255, 255, 255, 0.04)',
      textColor: '#94a3b8',
      tooltipBg: '#1e293b',
      tooltipText: '#f1f5f9',
      tooltipBorder: '#334155'
    };
  } else if (theme === 'alfa-admin') {
    const palette = ['#b45309', '#65a30d', '#dc2626', '#d97706', '#854d0e', '#78350f', '#0f766e'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '33'),
      gridColor: 'rgba(0, 0, 0, 0.04)',
      textColor: '#78716c',
      tooltipBg: '#ffffff',
      tooltipText: '#292524',
      tooltipBorder: '#e8dcc8'
    };
  } else if (theme === 'rubyx-admin') {
    const palette = ['#4f46e5', '#10b981', '#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '33'),
      gridColor: 'rgba(0, 0, 0, 0.04)',
      textColor: '#4b5563',
      tooltipBg: '#ffffff',
      tooltipText: '#111827',
      tooltipBorder: '#e5e7eb'
    };
  } else if (theme === 'pixel-admin') {
    const palette = ['#e11d48', '#059669', '#3b82f6', '#d97706', '#7c3aed', '#0891b2', '#2563eb'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '33'),
      gridColor: 'rgba(15, 23, 42, 0.04)',
      textColor: '#475569',
      tooltipBg: '#ffffff',
      tooltipText: '#0f172a',
      tooltipBorder: '#e2e8f0'
    };
  } else if (theme === 'powerbi-admin') {
    const palette = ['#f2c811', '#107c10', '#d13438', '#0078d4', '#002050', '#8764b8', '#008272'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '33'),
      gridColor: 'rgba(0, 0, 0, 0.06)',
      textColor: '#605e5c',
      tooltipBg: '#ffffff',
      tooltipText: '#252423',
      tooltipBorder: '#d0d5de'
    };
  } else if (theme === 'crmi-admin') {
    const palette = ['#5ce1e6', '#64ffda', '#ff6b8a', '#ff9f43', '#8b5cf6', '#ff5252', '#00d2fc'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '55'),
      gridColor: 'rgba(255, 255, 255, 0.04)',
      textColor: '#8892b0',
      tooltipBg: '#112240',
      tooltipText: '#e6f1ff',
      tooltipBorder: '#1e3a5f'
    };
  } else if (theme === 'gilded-admin') {
    const palette = ['#a67c52', '#6b8e23', '#c0392b', '#8e44ad', '#2c3e50', '#d35400', '#2980b9'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '33'),
      gridColor: 'rgba(61, 46, 26, 0.04)',
      textColor: '#7a6a52',
      tooltipBg: '#ffffff',
      tooltipText: '#3d2e1a',
      tooltipBorder: '#ecdfc8'
    };
  } else if (theme === 'superieur-admin') {
    const palette = ['#1e59ff', '#10b981', '#f43f5e', '#f59e0b', '#8b5cf6', '#0ea5e9', '#64748b'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '33'),
      gridColor: 'rgba(45, 55, 72, 0.05)',
      textColor: '#718096',
      tooltipBg: '#ffffff',
      tooltipText: '#2d3748',
      tooltipBorder: '#e2e8f0'
    };
  } else if (theme === 'study-admin') {
    const palette = ['#2563eb', '#f97316', '#ef4444', '#10b981', '#8b5cf6', '#0ea5e9', '#64748b'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '33'),
      gridColor: 'rgba(15, 23, 42, 0.05)',
      textColor: '#64748b',
      tooltipBg: '#ffffff',
      tooltipText: '#1e293b',
      tooltipBorder: '#cbd5e1'
    };
  } else if (theme === 'server-admin') {
    const palette = ['#0284c7', '#0d9488', '#7c3aed', '#ea580c', '#ec4899', '#3b82f6', '#10b981'];
    return {
      palette: palette,
      paletteMuted: palette.map(c => c + '33'),
      gridColor: 'rgba(15, 23, 42, 0.04)',
      textColor: '#475569',
      tooltipBg: '#ffffff',
      tooltipText: '#0f172a',
      tooltipBorder: '#e2e8f0'
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

// ─── Line Chart (Time Series) ──────────────────────────────────
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

// ─── Bar Chart (Column & Bar) ──────────────────────────────────
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
        borderSkipped: false,
        maxBarThickness: 48
      }]
    },
    options: {
      ...baseOpts,
      indexAxis: horizontal ? 'y' : 'x',
      plugins: { ...baseOpts.plugins, legend: { display: false } }
    }
  });
}

// ─── Doughnut Chart ────────────────────────────────────────────
function makeDoughnutChart(id, labels, data) {
  const ctx = document.getElementById(id); if (!ctx) return;
  if (window.chartInstances[id]) { window.chartInstances[id].destroy(); }
  
  const cfg = getThemeConfig();
  const baseOpts = getBaseOpts(cfg);
  const cardBg = getComputedStyle(document.documentElement).getPropertyValue('--bg-elevated').trim() || '#ffffff';
  
  window.chartInstances[id] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: cfg.palette,
        borderColor: cardBg,
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

// ─── Scatter Chart ─────────────────────────────────────────────
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

// ─── Pie Chart ─────────────────────────────────────────────────
function makePieChart(id, labels, data) {
  const ctx = document.getElementById(id); if (!ctx) return;
  if (window.chartInstances[id]) { window.chartInstances[id].destroy(); }

  const cfg = getThemeConfig();
  const baseOpts = getBaseOpts(cfg);
  const cardBg = getComputedStyle(document.documentElement).getPropertyValue('--bg-elevated').trim() || '#ffffff';
  const total = data.reduce((a, b) => a + b, 0);

  window.chartInstances[id] = new Chart(ctx, {
    type: 'pie',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: cfg.palette,
        borderColor: cardBg,
        borderWidth: 2,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 500 },
      plugins: {
        legend: {
          position: 'right',
          labels: { color: cfg.textColor, font: { family: 'Inter', size: 11 }, padding: 14, boxWidth: 10 }
        },
        tooltip: {
          ...baseOpts.plugins.tooltip,
          callbacks: {
            label: ctx => {
              const pct = total > 0 ? ((ctx.raw / total) * 100).toFixed(1) : 0;
              return ` ${ctx.label}: ${ctx.raw.toLocaleString()} (${pct}%)`;
            }
          }
        }
      }
    }
  });
}

// ─── Bubble Chart ──────────────────────────────────────────────
function makeBubbleChart(id, bubbleData) {
  // bubbleData: [{ x, y, r, label }]
  const ctx = document.getElementById(id); if (!ctx) return;
  if (window.chartInstances[id]) { window.chartInstances[id].destroy(); }

  const cfg = getThemeConfig();
  const baseOpts = getBaseOpts(cfg);

  // Normalize r values to 5-30 pixel range
  const maxR = Math.max(...bubbleData.map(d => d.r), 1);
  const normalized = bubbleData.map((d, i) => ({
    x: d.x,
    y: d.y,
    r: Math.max(5, (d.r / maxR) * 30),
    label: d.label,
    rawR: d.r
  }));

  window.chartInstances[id] = new Chart(ctx, {
    type: 'bubble',
    data: {
      datasets: [{
        data: normalized,
        backgroundColor: normalized.map((_, i) => cfg.palette[i % cfg.palette.length] + '88'),
        borderColor: normalized.map((_, i) => cfg.palette[i % cfg.palette.length]),
        borderWidth: 1.5,
        hoverBorderWidth: 2
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
            label: ctx => {
              const d = ctx.raw;
              return ` ${d.label}  Revenue: ${d.x.toLocaleString()}  Profit: ${d.y.toLocaleString()}  Orders: ${d.rawR.toLocaleString()}`;
            }
          }
        }
      }
    }
  });
}

// ─── Heatmap Chart (canvas-based fallback) ─────────────────────
function makeHeatmapChart(id, xLabels, yLabels, matrixData) {
  // matrixData: 2D array [yLabels.length][xLabels.length]
  const canvas = document.getElementById(id); if (!canvas) return;
  if (window.chartInstances[id]) {
    if (window.chartInstances[id].destroy) window.chartInstances[id].destroy();
  }

  const ctx = canvas.getContext('2d');
  const cfg = getThemeConfig();
  const isDark = document.documentElement.getAttribute('data-theme') !== 'light-corporate' &&
                 document.documentElement.getAttribute('data-theme') !== 'pastel-soft';

  // Flatten to find min/max
  const flat = matrixData.flat().filter(v => v != null);
  const minVal = Math.min(...flat);
  const maxVal = Math.max(...flat);
  const range = maxVal - minVal || 1;

  // Calculate dimensions
  const parent = canvas.parentElement;
  const W = parent.clientWidth || 500;
  const H = parent.clientHeight || 300;
  canvas.width = W * 2;   // retina
  canvas.height = H * 2;
  canvas.style.width = W + 'px';
  canvas.style.height = H + 'px';
  ctx.scale(2, 2);

  const padLeft = 90, padTop = 30, padRight = 60, padBottom = 40;
  const gridW = W - padLeft - padRight;
  const gridH = H - padTop - padBottom;
  const cellW = gridW / xLabels.length;
  const cellH = gridH / yLabels.length;

  // Clear
  ctx.clearRect(0, 0, W, H);

  // Color interpolation
  function heatColor(val) {
    const t = (val - minVal) / range;
    if (isDark) {
      // Purple scale for dark theme
      const r = Math.round(30 + t * 94);
      const g = Math.round(20 + t * 18);
      const b = Math.round(60 + t * 177);
      return `rgba(${r},${g},${b},${0.3 + t * 0.7})`;
    } else {
      // Blue scale for light theme
      const r = Math.round(220 - t * 183);
      const g = Math.round(230 - t * 131);
      const b = Math.round(245 - t * 10);
      return `rgb(${r},${g},${b})`;
    }
  }

  // Draw cells
  for (let yi = 0; yi < yLabels.length; yi++) {
    for (let xi = 0; xi < xLabels.length; xi++) {
      const val = matrixData[yi][xi] || 0;
      const x = padLeft + xi * cellW;
      const y = padTop + yi * cellH;

      ctx.fillStyle = heatColor(val);
      ctx.fillRect(x + 1, y + 1, cellW - 2, cellH - 2);

      // Value text
      ctx.fillStyle = cfg.textColor;
      ctx.font = `${Math.min(11, cellW / 5)}px Inter`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const displayVal = val >= 1000 ? (val / 1000).toFixed(1) + 'K' : Math.round(val);
      ctx.fillText(displayVal, x + cellW / 2, y + cellH / 2);
    }
  }

  // X labels
  ctx.fillStyle = cfg.textColor;
  ctx.font = '10px Inter';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  xLabels.forEach((lbl, i) => {
    const x = padLeft + i * cellW + cellW / 2;
    ctx.fillText(lbl.length > 10 ? lbl.slice(0, 10) + '…' : lbl, x, padTop + gridH + 8);
  });

  // Y labels
  ctx.textAlign = 'right';
  ctx.textBaseline = 'middle';
  yLabels.forEach((lbl, i) => {
    const y = padTop + i * cellH + cellH / 2;
    ctx.fillText(lbl.length > 12 ? lbl.slice(0, 12) + '…' : lbl, padLeft - 8, y);
  });

  // Legend gradient bar
  const lgX = W - padRight + 14, lgY = padTop, lgW = 14, lgH = gridH;
  for (let i = 0; i < lgH; i++) {
    const t = 1 - i / lgH;
    ctx.fillStyle = heatColor(minVal + t * range);
    ctx.fillRect(lgX, lgY + i, lgW, 1);
  }
  ctx.fillStyle = cfg.textColor;
  ctx.font = '9px Inter';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';
  const maxDisplay = maxVal >= 1000 ? (maxVal / 1000).toFixed(0) + 'K' : Math.round(maxVal);
  const minDisplay = minVal >= 1000 ? (minVal / 1000).toFixed(0) + 'K' : Math.round(minVal);
  ctx.fillText(maxDisplay, lgX + lgW + 4, lgY);
  ctx.fillText(minDisplay, lgX + lgW + 4, lgY + lgH - 10);

  // Store a dummy reference so we can "destroy" later
  window.chartInstances[id] = {
    destroy: () => { ctx.clearRect(0, 0, canvas.width, canvas.height); }
  };
}

// ─── Superieur Custom Grouped Bar Chart ───────────────────────
function makeGroupedBarChart(id, labels, revData, costData, profitData) {
  const ctx = document.getElementById(id); if (!ctx) return;
  if (window.chartInstances[id]) { window.chartInstances[id].destroy(); }
  
  const cfg = getThemeConfig();
  const baseOpts = getBaseOpts(cfg);
  
  window.chartInstances[id] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Revenue',
          data: revData,
          backgroundColor: '#1e59ff',
          borderRadius: 3,
          maxBarThickness: 10
        },
        {
          label: 'Cost',
          data: costData,
          backgroundColor: '#10b981',
          borderRadius: 3,
          maxBarThickness: 10
        },
        {
          label: 'Profit',
          data: profitData,
          backgroundColor: '#0ea5e9',
          borderRadius: 3,
          maxBarThickness: 10
        }
      ]
    },
    options: {
      ...baseOpts,
      plugins: {
        ...baseOpts.plugins,
        legend: { display: false }
      },
      scales: {
        x: {
          ...baseOpts.scales.x,
          grid: { display: false }
        },
        y: {
          ...baseOpts.scales.y,
          border: { dash: [4, 4] }
        }
      }
    }
  });
}

// ─── Superieur Mini Sparkline Helper ───────────────────────────
function makeSuperieurSparkline(id, data, color, type = 'line') {
  const ctx = document.getElementById(id); if (!ctx) return;
  if (window.chartInstances[id]) { window.chartInstances[id].destroy(); }
  
  const dataset = {
    data: data,
    borderWidth: type === 'line' ? 2 : 1,
    borderColor: color,
    backgroundColor: type === 'line' ? color + '22' : color,
    fill: type === 'line',
    borderRadius: type === 'bar' ? 2 : 0,
    maxBarThickness: type === 'bar' ? 6 : undefined
  };

  window.chartInstances[id] = new Chart(ctx, {
    type: type === 'line' ? 'line' : 'bar',
    data: {
      labels: data.map((_, i) => i + 1),
      datasets: [dataset]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      events: [],
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      },
      scales: {
        x: { display: false },
        y: { display: false }
      },
      elements: {
        point: { radius: 0 }
      }
    }
  });
}

