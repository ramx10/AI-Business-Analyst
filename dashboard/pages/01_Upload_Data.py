import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
from utils.helper import read_dataset
from utils.sample_data import generate_sample_sales_df
from utils.large_dataset import estimate_memory
from dashboard.styles import apply_page_styling

apply_page_styling()

st.title("➔ Upload Dataset")

st.markdown("""
<div style="font-size: 16px; color: #94a3b8; margin-bottom: 25px;">
Upload your business dataset (CSV, Excel, JSON, or Parquet) to begin the automated analysis pipeline, or load our pre-configured retail sales dataset to preview the dashboard immediately.
</div>
""", unsafe_allow_html=True)

# ---------------- Sample Sales Dataset Generator ----------------
st.subheader("✦ No Data? Try Our Demo Dataset")
if st.button("➔ Load Sample Sales Dataset", type="primary", use_container_width=True):
    sample_df = generate_sample_sales_df()
    st.session_state["df"] = sample_df
    st.balloons()
    st.success("✦ Loaded sample retail sales dataset containing 2,823 records!")
    st.rerun()

st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 30px 0;' />", unsafe_allow_html=True)
st.subheader("↓ Upload Your Dataset")

uploaded_file = st.file_uploader(
    "Choose a CSV, Excel, JSON, or Parquet file",
    type=["csv", "xlsx", "json", "parquet"]
)

if uploaded_file is not None:
    try:
        df = read_dataset(uploaded_file)
        
        # Save dataframe for all pages
        st.session_state["df"] = df
        
        st.success("✦ Dataset uploaded and processed successfully!")

        st.subheader("▣ Dataset Overview")
        rows, cols = df.shape
        
        mem_mb = estimate_memory(df)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center;">
                <div style="font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Total Rows</div>
                <div style="font-size: 36px; font-weight: 700; color: #60a5fa;">{rows:,}</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center;">
                <div style="font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Total Columns</div>
                <div style="font-size: 36px; font-weight: 700; color: #10b981;">{cols}</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            mem_color = "#e67e22" if mem_mb > 200 else "#60a5fa"
            st.markdown(f"""
            <div class="custom-card" style="text-align: center;">
                <div style="font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Memory Usage</div>
                <div style="font-size: 36px; font-weight: 700; color: {mem_color};">{mem_mb:.2f} MB</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.subheader("◉ Preview (First 5 Rows)")
        st.dataframe(df.head(), use_container_width=True)

    except Exception as e:
        st.error(f"Failed to read dataset: {str(e)}")
