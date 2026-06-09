import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st

from agents.schema_agent import SchemaAgent
from agents.cleaning_agent import DataCleaningAgent
from agents.kpi_agent import KPIAgent
from agents.ai_insight_agent import AIInsightAgent
from dashboard.styles import apply_page_styling

apply_page_styling()

st.title("↑ Business Insights")

st.markdown("""
<div style="font-size: 16px; color: #94a3b8; margin-bottom: 25px;">
AI-generated analysis detailing key business insights, trends, risks, opportunities, and recommended next steps based on the uploaded dataset.
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("Settings")
    if st.button("↻ Clear Insights Cache", type="secondary", use_container_width=True):
        st.cache_data.clear()
        st.success("Cache cleared!")
        st.rerun()

if "df" not in st.session_state:
    st.markdown("""
    <div class="alert-box" style="border-left-color: #f59e0b;">
        <span style="font-weight: 600; color: #f59e0b;">⚠ Warning:</span> 
        <span style="color: #94a3b8;">Please upload a dataset first under <b>01 Upload Data</b>.</span>
    </div>
    """, unsafe_allow_html=True)
else:
    df = st.session_state["df"]

    @st.cache_data
    def _generate_insights(df_local):
        s_agent = SchemaAgent()
        c_agent = DataCleaningAgent()
        k_agent = KPIAgent()
        ai_agent = AIInsightAgent()
        s_info = s_agent.analyze_schema(df_local)
        c_info = c_agent.analyze_data_quality(df_local)
        k_info = k_agent.generate_kpis(df_local)
        insights = ai_agent.generate_insights(s_info, c_info, k_info)
        if insights.startswith("Error:") or "Limit Exceeded" in insights or "Quota Exceeded" in insights:
            raise RuntimeError(insights)
        return insights

    try:
        with st.spinner("Generating business insights... (Executing Groq inference)"):
            result = _generate_insights(df)
        st.success("✦ Business analysis completed successfully!")
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.markdown(result)
        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as err:
        st.error(f"Analysis failed: {str(err)}")
        st.info("✦ Try clicking 'Clear Insights Cache' in the sidebar or verifying your Groq API key configuration in .env.")
