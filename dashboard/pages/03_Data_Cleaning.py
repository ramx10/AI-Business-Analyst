import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
from agents.cleaning_agent import DataCleaningAgent
from utils.metrics import missing_value_summary
from dashboard.styles import apply_page_styling

st.set_page_config(layout="wide")
apply_page_styling()

st.title("🧹 Data Cleaning & Quality")

if "df" not in st.session_state:
    st.markdown("""
    <div class="alert-box" style="border-left-color: #f59e0b;">
        <span style="font-weight: 600; color: #f59e0b;">⚠️ Warning:</span> 
        <span style="color: #94a3b8;">Please upload a dataset first under <b>01 Upload Data</b>.</span>
    </div>
    """, unsafe_allow_html=True)
else:
    df = st.session_state["df"]
    agent = DataCleaningAgent()

    with st.spinner("Analyzing dataset quality..."):
        result = agent.analyze_data_quality(df)

    st.success("Data quality analysis completed.")

    # Show metrics in elegant cards
    total_missing = sum(result["missing_values"].values())
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
    st.subheader("🔍 Missing Values Table")
    
    missing_sum_df = missing_value_summary(df)
    if not missing_sum_df.empty:
        st.dataframe(missing_sum_df, use_container_width=True)
    else:
        st.info("No missing values found in the dataset.")

    # ---------------- Interactive Auto-Cleaning ----------------
    st.write("")
    st.subheader("🛠️ Automated Data Cleaning")
    st.write("Perform automated cleaning on the dataset. This will:")
    st.markdown("- Drop all duplicate rows.")
    st.markdown("- Impute missing **numerical** values with the column **median**.")
    st.markdown("- Impute missing **categorical** values with the column **mode**.")

    if st.button("🧼 Run Auto-Clean & Apply in Place", type="primary"):
        cleaned_df = df.copy()
        
        # 1. Drop duplicates
        cleaned_df = cleaned_df.drop_duplicates()
        
        # 2. Impute missing values
        for col in cleaned_df.columns:
            if cleaned_df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    median_val = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(median_val)
                else:
                    mode_val = cleaned_df[col].mode()
                    if not mode_val.empty:
                        cleaned_df[col] = cleaned_df[col].fillna(mode_val[0])
                    else:
                        cleaned_df[col] = cleaned_df[col].fillna("Unknown")

        # Save back to session state
        st.session_state["df"] = cleaned_df
        
        st.balloons()
        st.success("🧼 Dataset successfully cleaned! All other tabs will now use the cleaned dataset.")
        st.rerun()
