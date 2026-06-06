import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.helper import safe_read_csv
from dashboard.styles import apply_page_styling

st.set_page_config(layout="wide")
apply_page_styling()

st.title("📂 Upload Dataset")

st.markdown("""
<div style="font-size: 16px; color: #94a3b8; margin-bottom: 25px;">
Upload your business dataset (CSV format) to begin the automated analysis pipeline, or load our pre-configured retail sales dataset to preview the dashboard immediately.
</div>
""", unsafe_allow_html=True)

# ---------------- Sample Sales Dataset Generator ----------------
st.subheader("💡 No Data? Try Our Demo Dataset")
if st.button("🚀 Load Sample Sales Dataset", type="primary", use_container_width=True):
    np.random.seed(42)
    n_rows = 1500
    
    # Generate random dates
    start_date = datetime(2025, 1, 1)
    date_list = [start_date + timedelta(days=int(np.random.randint(0, 365))) for _ in range(n_rows)]
    
    # Regions & States
    regions_states = {
        "North": ["New York", "Ohio", "Michigan", "Pennsylvania"],
        "South": ["Florida", "Georgia", "North Carolina", "Texas"],
        "East": ["Massachusetts", "Maryland", "New Jersey"],
        "West": ["California", "Washington", "Colorado", "Oregon"]
    }
    regions = list(regions_states.keys())
    selected_regions = np.random.choice(regions, n_rows)
    selected_states = [np.random.choice(regions_states[r]) for r in selected_regions]
    
    # Categories & Products
    cats_prods = {
        "Technology": ["Laptop", "Smartphone", "Tablet", "Monitor", "Keyboard"],
        "Office Supplies": ["Paper Reams", "Gel Pens", "Notebooks", "Calculators"],
        "Furniture": ["Desk Chair", "Dining Table", "Bookshelf", "Office Desk"]
    }
    categories = list(cats_prods.keys())
    selected_cats = np.random.choice(categories, n_rows, p=[0.4, 0.35, 0.25])
    selected_prods = [np.random.choice(cats_prods[c]) for c in selected_cats]
    
    # Revenue & Profit
    revenue = np.random.normal(4500, 2500, n_rows).clip(300, 25000).round(2)
    profit = (revenue * np.random.uniform(0.1, 0.45, n_rows)).round(2)
    
    # IDs
    cust_ids = [f"C-{np.random.randint(1001, 1250)}" for _ in range(n_rows)]
    order_ids = [f"O-{np.random.randint(5001, 6200)}" for _ in range(n_rows)]
    
    # Construct DataFrame
    sample_df = pd.DataFrame({
        "Date": date_list,
        "Order_ID": order_ids,
        "Customer_ID": cust_ids,
        "Region": selected_regions,
        "State": selected_states,
        "Product_Category": selected_cats,
        "Product": selected_prods,
        "Revenue": revenue,
        "Profit": profit
    })
    
    # Sort by Date
    sample_df = sample_df.sort_values("Date").reset_index(drop=True)
    
    st.session_state["df"] = sample_df
    st.balloons()
    st.success("🎉 Loaded sample retail sales dataset containing 1,500 records!")
    st.rerun()

st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 30px 0;' />", unsafe_allow_html=True)
st.subheader("📥 Upload Your Own CSV File")

# Let's wrap the file uploader in a nice layout
uploaded_file = st.file_uploader(
    "Choose a CSV file from your computer",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = safe_read_csv(uploaded_file)
        
        # Save dataframe for all pages
        st.session_state["df"] = df
        
        st.success("🎉 Dataset uploaded and processed successfully!")

        st.subheader("📊 Dataset Overview")
        rows, cols = df.shape
        
        c1, c2 = st.columns(2)
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

        st.write("")
        st.subheader("🔍 Preview (First 5 Rows)")
        st.dataframe(df.head(), use_container_width=True)

    except Exception as e:
        st.error(f"Failed to read dataset: {str(e)}")
