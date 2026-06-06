import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from dashboard.styles import apply_page_styling

st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide"
)

# Apply premium page styling
apply_page_styling()

# Custom styles specific to the home banner
st.markdown("""
<style>
    .hero-container {
        background: linear-gradient(135deg, #4f46e5 0%, #1e1b4b 100%);
        border-radius: 12px;
        padding: 50px 40px;
        color: white;
        text-align: left;
        margin-bottom: 35px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .hero-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 15px;
        letter-spacing: -1px;
        color: #ffffff !important;
    }
    
    .hero-subtitle {
        font-size: 19px;
        font-weight: 400;
        color: #c7d2fe;
        opacity: 0.9;
        margin-bottom: 0px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Styled Hero Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-title">📊 AI Business Analyst</div>
    <div class="hero-subtitle">A state-of-the-art business intelligence platform. Clean your datasets, generate interactive dashboards, discover insights, and build executive summaries instantly using multi-agent intelligence.</div>
</div>
""", unsafe_allow_html=True)

st.write("")
st.subheader("🏁 Data Pipeline Journey")

# Grid of Feature Cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="custom-card" style="min-height: 200px;">
        <div style="font-size: 32px; margin-bottom: 12px;">📂</div>
        <div style="font-size: 18px; font-weight: 600; color: #ffffff; margin-bottom: 8px;">1. Upload & Ingest</div>
        <div style="font-size: 14px; color: #94a3b8; line-height: 1.5;">Ingest raw data securely. Detect local character encodings automatically, or load our retail sales demo dataset with a single click.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="custom-card" style="min-height: 200px;">
        <div style="font-size: 32px; margin-bottom: 12px;">📋</div>
        <div style="font-size: 18px; font-weight: 600; color: #ffffff; margin-bottom: 8px;">2. Schema Analysis</div>
        <div style="font-size: 14px; color: #94a3b8; line-height: 1.5;">Map and isolate numerical versus categorical attributes. Understand dataset shapes, null rates, and unique key distributions.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="custom-card" style="min-height: 200px;">
        <div style="font-size: 32px; margin-bottom: 12px;">🧹</div>
        <div style="font-size: 18px; font-weight: 600; color: #ffffff; margin-bottom: 8px;">3. Data Cleaning</div>
        <div style="font-size: 14px; color: #94a3b8; line-height: 1.5;">Uncover missing columns or row duplications. Impute values using median/mode and clean the entire dataset in place.</div>
    </div>
    """, unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div class="custom-card" style="min-height: 200px;">
        <div style="font-size: 32px; margin-bottom: 12px;">🏠</div>
        <div style="font-size: 18px; font-weight: 600; color: #ffffff; margin-bottom: 8px;">4. Executive Dashboard</div>
        <div style="font-size: 14px; color: #94a3b8; line-height: 1.5;">Browse responsive KPI cards, state-level breakdowns, and category share charts. Supports multi-select filters and regional drill-downs.</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="custom-card" style="min-height: 200px;">
        <div style="font-size: 32px; margin-bottom: 12px;">📈</div>
        <div style="font-size: 18px; font-weight: 600; color: #ffffff; margin-bottom: 8px;">5. Business Insights</div>
        <div style="font-size: 14px; color: #94a3b8; line-height: 1.5;">Examine automated Llama-generated findings on business trends, revenue drivers, market segments, and operational risks.</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown("""
    <div class="custom-card" style="min-height: 200px;">
        <div style="font-size: 32px; margin-bottom: 12px;">📄</div>
        <div style="font-size: 18px; font-weight: 600; color: #ffffff; margin-bottom: 8px;">6. AI Report</div>
        <div style="font-size: 14px; color: #94a3b8; line-height: 1.5;">Compile a formal executive summary and complete markdown business report via our supervisor agent. Save and download instantly.</div>
    </div>
    """, unsafe_allow_html=True)

# Guidance callout
st.write("")
st.markdown("""
<div class="alert-box">
    <span style="font-weight: 600; color: #60a5fa;">💡 Getting Started:</span> 
    <span style="color: #94a3b8;">Select <b>01 Upload Data</b> in the sidebar to feed data into the analytical pipeline!</span>
</div>
""", unsafe_allow_html=True)