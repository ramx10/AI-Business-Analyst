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
    n_rows = 2823
    
    start_date = datetime(2024, 1, 1)
    date_list = [start_date + timedelta(days=int(np.random.randint(0, 730))) for _ in range(n_rows)]
    
    sel_regions = np.random.choice(["EMEA", "APAC", "Japan"], n_rows, p=[0.80, 0.12, 0.08])
    
    categories = [
        "Classic Cars", "Vintage Cars", "Motorcycles", 
        "Trucks and Buses", "Planes", "Ships", "Trains"
    ]
    cat_p = [0.35, 0.22, 0.12, 0.11, 0.10, 0.07, 0.03]
    sel_cats = np.random.choice(categories, n_rows, p=cat_p)
    
    prod_pool = {
        "Classic Cars": ["S18_3232", "S10_1949", "S12_1108", "S18_2238", "S24_2887"],
        "Vintage Cars": ["S18_1342", "S18_2709", "S24_2011", "S24_3151"],
        "Motorcycles": ["S10_4698", "S12_2823", "S18_2625"],
        "Trucks and Buses": ["S12_1666", "S18_1097"],
        "Planes": ["S18_1662", "S24_3976"],
        "Ships": ["S700_2824", "S720_1697"],
        "Trains": ["S32_3207", "S50_1392"]
    }
    sel_prods = [np.random.choice(prod_pool[c]) for c in sel_cats]
    
    order_ids = [f"10{100 + np.random.randint(0, 300)}" for _ in range(n_rows)]
    
    customers = [
        "Land of Toys Inc.", "Reims Collectables", "Mini Gifts Distributors Ltd.", 
        "Havel & Collectables", "Scandinavian Gift Ideas", "Danish Wholesale Imports"
    ]
    sel_customers = np.random.choice(customers, n_rows)
    
    revenue = []
    for r in sel_regions:
        if r == "EMEA":
            val = np.random.normal(2175, 500)
        elif r == "APAC":
            val = np.random.normal(2200, 500)
        else: # Japan
            val = np.random.normal(2000, 400)
        revenue.append(round(max(300, val), 2))
    revenue = np.array(revenue)
    
    profit = (revenue * np.random.uniform(0.25, 0.35, n_rows)).round(2)
    
    postal_codes = []
    for i in range(n_rows):
        if len(postal_codes) < 465:
            postal_codes.append(None)
        else:
            postal_codes.append(str(np.random.randint(10000, 99999)))
    np.random.shuffle(postal_codes)
    
    sample_df = pd.DataFrame({
        "Date": date_list,
        "Order_ID": order_ids,
        "Customer_ID": sel_customers,
        "Region": sel_regions,
        "Product_Category": sel_cats,
        "Product": sel_prods,
        "Revenue": revenue,
        "Profit": profit,
        "PostalCode": postal_codes
    })
    
    sample_df = sample_df.sort_values("Date").reset_index(drop=True)
    
    st.session_state["df"] = sample_df
    st.balloons()
    st.success("🎉 Loaded sample retail sales dataset containing 2,823 records!")
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
