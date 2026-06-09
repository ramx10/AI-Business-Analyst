import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from agents.nlq_agent import NLQAgent
from dashboard.styles import apply_page_styling

apply_page_styling()

st.title("✦ Natural Language Query")
st.markdown("""
<div style="font-size: 16px; color: #94a3b8; margin-bottom: 25px;">
Ask questions about your dataset in plain English. The AI will analyze your data and return answers with optional charts.
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

    if "nlq_history" not in st.session_state:
        st.session_state["nlq_history"] = []

    agent = NLQAgent()

    with st.container():
        st.markdown("### Ask a Question")
        col1, col2 = st.columns([5, 1])
        with col1:
            question = st.text_input(
                "Question",
                placeholder="e.g. What is the total revenue? or Show me sales by region",
                label_visibility="collapsed",
            )
        with col2:
            ask = st.button("Ask", type="primary", use_container_width=True)

        examples = st.markdown("""
        <div style="font-size: 13px; color: #94a3b8; margin-bottom: 16px;">
        Try: <code>What is the average revenue per order?</code> 
        • <code>Show me sales by category</code> 
        • <code>Which region has the highest profit?</code>
        • <code>What are the top 5 products?</code>
        </div>
        """, unsafe_allow_html=True)

    if ask and question.strip():
        with st.spinner("Analyzing your data…"):
            result = agent.query(question.strip(), df)
        st.session_state["nlq_history"].append({
            "question": question.strip(),
            "answer": result.get("answer", ""),
            "confidence": result.get("confidence", "low"),
            "chart": result.get("chart"),
        })
        st.rerun()

    if st.session_state["nlq_history"]:
        st.markdown("### Conversation History")
        st.markdown("""
        <div style="margin-bottom: 16px;">
        <button onclick="document.querySelector('.clear-history-btn')?.click()" 
                style="background:transparent;border:1px solid var(--border);color:var(--text-secondary);
                       padding:6px 14px;border-radius:6px;cursor:pointer;font-size:13px;">
            Clear History
        </button>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Clear History", key="clear_nlq_history"):
            st.session_state["nlq_history"] = []
            st.rerun()

        for i, entry in enumerate(reversed(st.session_state["nlq_history"])):
            confidence = entry.get("confidence", "low")
            conf_color = {"high": "#22c55e", "medium": "#eab308", "low": "#ef4444"}.get(confidence, "#94a3b8")

            st.markdown(f"""
            <div style="background:var(--bg-elevated);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px;">
                <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:12px;">
                    <div style="background:var(--accent-muted);color:var(--accent);width:32px;height:32px;border-radius:50%;
                                display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;">Q</div>
                    <div style="flex:1;">
                        <div style="font-weight:600;font-size:14px;color:var(--text-primary);margin-bottom:4px;">{
                            entry['question']}</div>
                    </div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:12px;">
                    <div style="background:{conf_color}20;color:{conf_color};width:32px;height:32px;border-radius:50%;
                                display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;">A</div>
                    <div style="flex:1;">
                        <div style="font-size:14px;color:var(--text-secondary);line-height:1.6;margin-bottom:8px;">{
                            entry['answer']}</div>
                        <div style="font-size:11px;color:{conf_color};">Confidence: {confidence}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            chart = entry.get("chart")
            if chart and chart.get("type") and chart.get("type") != "table":
                import plotly.express as px
                import pandas as pd
                labels = chart.get("labels", [])
                values = chart.get("values", [])
                title = chart.get("title", "")
                if labels and values:
                    cdf = pd.DataFrame({"label": labels, "value": values})
                    chart_type = chart["type"]
                    if chart_type == "bar":
                        fig = px.bar(cdf, x="label", y="value", title=title)
                    elif chart_type == "line":
                        fig = px.line(cdf, x="label", y="value", title=title, markers=True)
                    elif chart_type in ("pie", "doughnut"):
                        fig = px.pie(cdf, names="label", values="value", title=title, hole=chart_type == "doughnut")
                    elif chart_type == "number":
                        fig = None
                        st.metric(label=title, value=cdf["value"].iloc[0] if len(cdf) > 0 else 0)
                    else:
                        fig = px.bar(cdf, x="label", y="value", title=title)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True, key=f"nlq_chart_{i}")
    else:
        st.info("✦ Ask a question above to get started. Try asking about revenue, trends, or breakdowns.")
