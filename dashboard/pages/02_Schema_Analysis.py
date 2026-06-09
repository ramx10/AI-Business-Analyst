import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
from agents.schema_agent import SchemaAgent
from dashboard.styles import apply_page_styling

apply_page_styling()

st.title("≡ Schema Analysis")

if "df" not in st.session_state:
    st.markdown("""
    <div class="alert-box" style="border-left-color: #f59e0b;">
        <span style="font-weight: 600; color: #f59e0b;">⚠ Warning:</span> 
        <span style="color: #94a3b8;">Please upload a dataset first under <b>01 Upload Data</b>.</span>
    </div>
    """, unsafe_allow_html=True)
else:
    df = st.session_state["df"]
    agent = SchemaAgent()

    with st.spinner("Analyzing schema..."):
        schema_info = agent.analyze_schema(df)

    st.subheader("◉ Schema Overview Table")

    # Convert schema_info dict into a clean pandas DataFrame for presentation
    schema_rows = []
    for col, info in schema_info.items():
        schema_rows.append({
            "Column Name": col,
            "Data Type": info["datatype"],
            "Unique Count": info["unique_values"]
        })
    schema_df = pd.DataFrame(schema_rows)

    # Let the user search and sort the columns easily
    st.dataframe(schema_df, use_container_width=True, hide_index=True)

    # ---------------- Grouped Columns Breakdown ----------------
    st.write("")
    st.subheader("▣ Columns by DataType Group")
    
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist()
    
    tab1, tab2 = st.tabs(["# Numeric Columns", "A Categorical / Text Columns"])
    
    with tab1:
        if numeric_cols:
            st.markdown(f"Found <span style='color: #60a5fa; font-weight: 600;'>{len(numeric_cols)}</span> numeric columns:", unsafe_allow_html=True)
            st.code(", ".join(numeric_cols), language="text")
            st.write("")
            st.write("▣ Basic Numeric Summary Metrics:")
            st.dataframe(df[numeric_cols].describe().T, use_container_width=True)
        else:
            st.info("No numeric columns found in the dataset.")
            
    with tab2:
        if categorical_cols:
            st.markdown(f"Found <span style='color: #10b981; font-weight: 600;'>{len(categorical_cols)}</span> categorical or text columns:", unsafe_allow_html=True)
            st.code(", ".join(categorical_cols), language="text")
            st.write("")
            st.write("▣ Basic Categorical Summary Metrics:")
            st.dataframe(df[categorical_cols].describe(include="object").T, use_container_width=True)
        else:
            st.info("No categorical/text columns found in the dataset.")
