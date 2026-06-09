import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
from agents.cleaning_agent import DataCleaningAgent
from utils.metrics import missing_value_summary
from dashboard.styles import apply_page_styling

apply_page_styling()

st.title("◈ Data Cleaning & Pipeline Builder")

if "df" not in st.session_state:
    uploaded_file = st.file_uploader("Upload a dataset first", type=["csv", "xlsx", "xls", "parquet"])
    if uploaded_file:
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(uploaded_file)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_parquet(uploaded_file)
        st.session_state["df"] = df
        st.rerun()
    st.markdown("""
    <div class="alert-box" style="border-left-color: #f59e0b;">
        <span style="font-weight: 600; color: #f59e0b;">⚠ Warning:</span>
        <span style="color: #94a3b8;">Please upload a dataset first under <b>01 Upload Data</b>.</span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df = st.session_state["df"]
agent = DataCleaningAgent()

with st.spinner("Analyzing dataset quality..."):
    result = agent.analyze_data_quality(df)

st.success("Data quality analysis completed.")

total_missing = result["missing_values"]
dup_rows = result["duplicate_rows"]

c1, c2 = st.columns(2)
with c1:
    if total_missing > 0:
        st.markdown(f"""
        <div class="custom-card" style="border-left: 4px solid #ef4444;">
            <div style="font-size: 14px; color: #fca5a5; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Missing Values Found</div>
            <div style="font-size: 32px; font-weight: 700; color: #f87171;">{total_missing:,}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="custom-card" style="border-left: 4px solid #10b981;">
            <div style="font-size: 14px; color: #a7f3d0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Missing Values</div>
            <div style="font-size: 32px; font-weight: 700; color: #34d399;">0 (Clean)</div>
        </div>
        """, unsafe_allow_html=True)

with c2:
    if dup_rows > 0:
        st.markdown(f"""
        <div class="custom-card" style="border-left: 4px solid #ef4444;">
            <div style="font-size: 14px; color: #fca5a5; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Duplicate Rows Found</div>
            <div style="font-size: 32px; font-weight: 700; color: #f87171;">{dup_rows:,}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="custom-card" style="border-left: 4px solid #10b981;">
            <div style="font-size: 14px; color: #a7f3d0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Duplicate Rows</div>
            <div style="font-size: 32px; font-weight: 700; color: #34d399;">0 (Clean)</div>
        </div>
        """, unsafe_allow_html=True)

st.write("")
st.subheader("◉ Missing Values Table")

missing_sum_df = missing_value_summary(df)
if not missing_sum_df.empty:
    st.dataframe(missing_sum_df, use_container_width=True)
else:
    st.info("No missing values found in the dataset.")

st.markdown("""
<style>
div[data-testid="column"] {
    max-height: 600px;
    overflow-y: auto;
    padding-right: 6px;
    align-self: start;
}
div[data-testid="column"]::-webkit-scrollbar {
    width: 5px;
}
div[data-testid="column"]::-webkit-scrollbar-track {
    background: transparent;
}
div[data-testid="column"]::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.15);
    border-radius: 3px;
}
</style>
""", unsafe_allow_html=True)

st.write("")
left_col, right_col = st.columns(2)

# ─── Auto-Cleaning Section ──────────────────────────────────────────────
with left_col:
    st.subheader("✦ Automated Data Cleaning")
    st.write("Perform automated cleaning on the dataset. This will:")
    st.markdown("- Drop all duplicate rows.")
    st.markdown("- Impute missing **numerical** values with the column **median**.")
    st.markdown("- Impute missing **categorical** values with the column **mode**.")

    if st.button("◈ Run Auto-Clean & Apply in Place", type="primary"):
        cleaned_df, change_log = agent.full_clean(df)

        st.session_state["df"] = cleaned_df

        st.balloons()
        st.success(f"◈ Dataset successfully cleaned! {len(change_log)} steps applied. All other tabs will now use the cleaned dataset.")

        st.subheader("↓ Download Cleaned Data")
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                label="↓ Download Cleaned Dataset (.csv)",
                data=cleaned_df.to_csv(index=False),
                file_name="cleaned_dataset.csv",
                mime="text/csv",
                use_container_width=True
            )
        with dl_col2:
            try:
                import io
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    cleaned_df.to_excel(writer, index=False, sheet_name='CleanedData')
                xlsx_data = output.getvalue()
                st.download_button(
                    label="↓ Download Cleaned Dataset (.xlsx)",
                    data=xlsx_data,
                    file_name="cleaned_dataset.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except ImportError:
                st.info("Install `openpyxl` to enable .xlsx export: `pip install openpyxl`")
        st.rerun()

# ─── Pipeline Builder Section ───────────────────────────────────────────
with right_col:
    st.subheader("≡ Selective Pipeline Builder")
    st.markdown("Choose individual cleaning steps to run instead of the full auto-clean pipeline.")

    STEPS = [
        (1, "Correct Data Types", "Auto-detect and fix numeric/date columns stored as strings"),
        (2, "Handle Missing Values", "Drop rows >50% null, fill remaining with median/mode"),
        (3, "Remove Duplicate Records", "Drop fully duplicate rows"),
        (4, "Standardize Formats", "Title-case categorical columns with few unique values"),
        (5, "Fix Inconsistent Entries", "Fuzzy-merge near-duplicate categorical variants"),
        (6, "Remove Unnecessary Columns", "Drop columns >90% null or zero variance"),
        (7, "Handle Outliers (IQR Capping)", "Clip extreme values using the IQR method"),
        (8, "Remove Extra Whitespace", "Strip leading/trailing whitespace from string columns"),
        (9, "Validate Data", "Clamp negative values and unreasonable ages"),
        (10, "Rename Columns", "Convert to lowercase_with_underscores"),
    ]

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### Steps 1-5")
        selected = {}
        for num, title, desc in STEPS[:5]:
            selected[num] = st.checkbox(f"**Step {num}:** {title}", value=True, key=f"step_{num}",
                                        help=desc)

    with col_right:
        st.markdown("#### Steps 6-10")
        for num, title, desc in STEPS[5:]:
            selected[num] = st.checkbox(f"**Step {num}:** {title}", value=True, key=f"step_{num}",
                                        help=desc)

    cols = st.columns(4)
    with cols[0]:
        preview_btn = st.button("◉ Preview Changes", type="secondary", use_container_width=True)
    with cols[1]:
        run_btn = st.button("⚡ Run Pipeline", type="primary", use_container_width=True)
    with cols[2]:
        reset_btn = st.button("↺ Reset to Original", use_container_width=True)
    with cols[3]:
        pass

    selected_step_nums = [num for num, checked in selected.items() if checked]

    if reset_btn:
        if "pipeline_original_df" in st.session_state:
            st.session_state["df"] = st.session_state["pipeline_original_df"].copy()
            st.success("Reset to original dataset.")
            st.rerun()
        else:
            st.info("No original snapshot to reset to. Run the pipeline first.")

    if preview_btn:
        if not selected_step_nums:
            st.warning("Select at least one step to preview.")
        else:
            preview_df = df.copy()
            with st.spinner("Running preview..."):
                preview_result, preview_log = agent.selective_clean(preview_df, selected_step_nums)
            st.success(f"Preview complete — {len(preview_log)} step(s) will be applied.")
            for entry in preview_log:
                snum = entry["step"]
                title = entry["title"]
                details = entry["details"]
                st.markdown(f"""
                <div class="custom-card" style="margin-bottom: 8px; padding: 12px 16px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="background: #6366f1; color: #fff; width: 26px; height: 26px; border-radius: 50%;
                                   display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0;">
                            {snum}
                        </span>
                        <div>
                            <div style="font-weight: 600; color: #ffffff; font-size: 14px;">{title}</div>
                            <div style="color: #94a3b8; font-size: 12px; margin-top: 2px;">{details}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    if run_btn:
        if not selected_step_nums:
            st.warning("Select at least one step to run.")
        else:
            if "pipeline_original_df" not in st.session_state:
                st.session_state["pipeline_original_df"] = df.copy()

            with st.spinner("Running selected cleaning steps..."):
                cleaned_df, change_log = agent.selective_clean(df.copy(), selected_step_nums)

            st.session_state["df"] = cleaned_df

            st.balloons()
            st.success(f"✓ Pipeline executed! {len(change_log)} step(s) applied.")

            st.subheader("✦ Change Log")
            for entry in change_log:
                snum = entry["step"]
                title = entry["title"]
                details = entry["details"]
                st.markdown(f"""
                <div class="custom-card" style="margin-bottom: 8px; padding: 12px 16px;
                            border-left: 3px solid #10b981;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="background: #10b981; color: #fff; width: 26px; height: 26px; border-radius: 50%;
                                   display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0;">
                            {snum}
                        </span>
                        <div>
                            <div style="font-weight: 600; color: #ffffff; font-size: 14px;">{title}</div>
                            <div style="color: #94a3b8; font-size: 12px; margin-top: 2px;">{details}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            csv = cleaned_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="↓ Download Cleaned Dataset (CSV)",
                data=csv,
                file_name="cleaned_dataset.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)

df_current = st.session_state["df"]
st.markdown(f"""
<div style="display: flex; gap: 16px; font-size: 13px; color: #94a3b8; margin-top: 12px;">
    <span>▣ <b style="color:#fff;">{df_current.shape[0]:,}</b> rows</span>
    <span>≡ <b style="color:#fff;">{df_current.shape[1]}</b> columns</span>
</div>
""", unsafe_allow_html=True)
