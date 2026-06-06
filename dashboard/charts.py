"""
dashboard/charts.py — Thin wrappers around utils.chart_utils for use
inside Streamlit dashboard pages.
"""
from utils.chart_utils import (  # noqa: F401 — re-export for dashboard convenience
    bar_chart,
    line_chart,
    pie_chart,
    histogram,
    box_plot,
    correlation_heatmap,
)
