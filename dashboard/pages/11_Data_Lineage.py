import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from dashboard.styles import apply_page_styling
from utils.lineage import LineageTracker

apply_page_styling()

st.title("↗ Data Lineage")
st.markdown("""
<div style="font-size: 16px; color: #94a3b8; margin-bottom: 25px;">
Visual trace of every transformation applied to your dataset, from upload through cleaning and analysis.
</div>
""", unsafe_allow_html=True)

session_id = st.session_state.get("session_id", None)

if not session_id:
    st.markdown("""
    <div class="alert-box" style="border-left-color: #f59e0b;">
        <span style="font-weight: 600; color: #f59e0b;">⚠ Warning:</span> 
        <span style="color: #94a3b8;">Please upload a dataset first under <b>01 Upload Data</b>.</span>
    </div>
    """, unsafe_allow_html=True)
else:
    tracker = LineageTracker(session_id)
    steps = tracker.get_steps()

    if not steps:
        st.info("No lineage data recorded yet. Upload and process a dataset to see the transformation trace.")
    else:
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Steps", len(steps))
        with col2:
            categories = len(set(s.category for s in steps))
            st.metric("Categories", categories)
        with col3:
            total_rows_changed = sum(abs(s.rows_before - s.rows_after) for s in steps)
            st.metric("Total Rows Changed", total_rows_changed)
        with col4:
            st.metric("Final Columns", steps[-1].columns_after if steps else 0)

        st.markdown("---")

        # Timeline display
        CATEGORY_COLORS = {
            "upload": "#3b82f6",
            "schema": "#8b5cf6",
            "clean": "#10b981",
            "pii": "#f59e0b",
            "kpi": "#eab308",
            "insights": "#ef4444",
            "report": "#6b7280",
        }

        for i, step in enumerate(steps):
            color = CATEGORY_COLORS.get(step.category, "#6b7280")

            row_change = step.rows_before - step.rows_after
            row_text = f"↓ {row_change} rows" if row_change > 0 else (f"↑ {abs(row_change)} rows" if row_change < 0 else f"{step.rows_after} rows")
            col_change = step.columns_before - step.columns_after
            col_text = f"↓ {col_change} cols" if col_change > 0 else (f"↑ {abs(col_change)} cols" if col_change < 0 else f"{step.columns_after} cols")

            st.markdown(f"""
            <div style="display:flex;gap:16px;margin-bottom:12px;align-items:stretch;">
                <div style="width:4px;background:{color};border-radius:2px;flex-shrink:0;"></div>
                <div style="flex:1;background:rgba(21,29,48,0.6);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:16px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <div>
                            <span style="font-size:11px;font-family:monospace;color:{color};background:{color}20;padding:1px 8px;border-radius:4px;margin-right:8px;">{step.step_id}</span>
                            <span style="font-weight:600;color:#ffffff;font-size:14px;">{step.step_name}</span>
                        </div>
                        <span style="font-size:10px;text-transform:uppercase;letter-spacing:0.5px;color:#94a3b8;">{step.category}</span>
                    </div>
                    <div style="font-size:13px;color:#94a3b8;margin-bottom:8px;">{step.description}</div>
                    <div style="display:flex;gap:16px;font-size:11px;color:#64748b;">
                        <span><span style="color:#94a3b8;">Cols:</span> {step.affected_columns if step.affected_columns else '*'}</span>
                        <span><span style="color:#94a3b8;">Rows:</span> {row_text}</span>
                        <span><span style="color:#94a3b8;">Columns:</span> {col_text}</span>
                        <span><span style="color:#94a3b8;">Duration:</span> {f'{step.duration_ms/1000:.1f}s' if step.duration_ms else '—'}</span>
                        <span><span style="color:#94a3b8;">Time:</span> {step.timestamp[:19] if step.timestamp else '—'}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
