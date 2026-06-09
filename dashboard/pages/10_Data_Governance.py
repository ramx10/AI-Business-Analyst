import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
from agents.pii_agent import PIIAgent
from dashboard.styles import apply_page_styling

apply_page_styling()

st.title("⊡ Data Governance")
st.markdown("""
<div style="font-size: 16px; color: #94a3b8; margin-bottom: 25px;">
Detect and mask personally identifiable information (PII) in your dataset.
</div>
""", unsafe_allow_html=True)

if "df" not in st.session_state:
    st.markdown("""
    <div class="alert-box" style="border-left-color: #f59e0b;">
        <span style="font-weight: 600; color: #f59e0b;">⚠ Warning:</span> 
        <span style="color: #94a3b8;">Please upload a dataset first under <b>01 Upload Data</b>.</span>
    </div>
    """, unsafe_allow_html=True)
else:
    df = st.session_state["df"]
    agent = PIIAgent()

    # ── Scan for PII ──────────────────────────────────────────────
    st.subheader("◉ Scan for PII")

    if st.button("Scan Dataset", type="primary"):
        with st.spinner("Scanning for PII..."):
            findings = agent.detect_pii(df)

        if not findings:
            st.success("✓ No PII detected in this dataset.")
        else:
            st.info(f"Found **{len(findings)}** PII columns.")

            findings_df = pd.DataFrame(findings)
            findings_df["risk"] = findings_df["risk"].astype(str)
            findings_df["sample_values"] = findings_df["sample_values"].apply(
                lambda vals: ", ".join(str(v) for v in vals[:3])
            )

            def color_risk(val):
                colors = {"high": "color: #ef4444;", "critical": "color: #ef4444; font-weight: bold;",
                          "medium": "color: #eab308;", "low": "color: #22c55e;"}
                return colors.get(val, "")

            st.dataframe(
                findings_df[["column", "type", "sample_values", "count", "risk"]].style.applymap(
                    color_risk, subset=["risk"]
                ),
                use_container_width=True,
                column_config={
                    "column": "Column",
                    "type": "PII Type",
                    "sample_values": "Sample Values",
                    "count": "Count",
                    "risk": "Risk",
                }
            )

            # ── Mask PII ──────────────────────────────────────────
            st.subheader("⊡ Mask PII")

            col_names = [f["column"] for f in findings]
            selected_cols = []
            for col in col_names:
                checked = st.checkbox(f"**{col}**", value=True, key=f"mask_{col}")
                if checked:
                    selected_cols.append(col)

            if st.button("Mask Selected", type="primary"):
                with st.spinner("Masking PII..."):
                    masked_df, change_log = agent.mask_pii(df, selected_cols)

                st.session_state["df"] = masked_df

                st.success(f"✓ {len(change_log)} column(s) masked.")
                for entry in change_log:
                    st.markdown(
                        f"- **{entry['column']}** ({entry['type']}): {entry['values_masked']} values masked"
                    )

                st.subheader("Preview (first 10 rows)")
                st.dataframe(masked_df.head(10), use_container_width=True)
    else:
        st.info("Click **Scan Dataset** to detect PII in your data.")
