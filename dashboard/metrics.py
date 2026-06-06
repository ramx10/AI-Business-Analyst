"""
dashboard/metrics.py — Thin wrappers around utils.metrics for use
inside Streamlit dashboard pages.
"""
from utils.metrics import basic_stats, missing_value_summary  # noqa: F401 — re-export
