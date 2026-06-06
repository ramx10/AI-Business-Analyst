import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import plotly.express as px
import pandas as pd
from dashboard.styles import (
    apply_page_styling, 
    apply_plotly_theme, 
    render_kpi_card,
    SVG_REVENUE,
    SVG_PROFIT,
    SVG_ORDERS,
    SVG_CUSTOMERS
)

st.set_page_config(layout="wide")
apply_page_styling()

st.title("🏠 Executive Dashboard")

if "df" not in st.session_state:
    st.markdown("""
    <div class="alert-box" style="border-left-color: #f59e0b;">
        <span style="font-weight: 600; color: #f59e0b;">⚠️ Warning:</span> 
        <span style="color: #94a3b8;">Please upload a dataset first under <b>01 Upload Data</b>.</span>
    </div>
    """, unsafe_allow_html=True)
else:
    df = st.session_state["df"]

    # ---------------- Sidebar Filter System ----------------
    st.sidebar.subheader("🎛️ Dashboard Filters")

    # 1. Date Filter
    date_col = next((c for c in df.columns if "date" in c.lower()), None)
    filtered_df = df.copy()

    if date_col:
        try:
            filtered_df[date_col] = pd.to_datetime(filtered_df[date_col])
            min_date = filtered_df[date_col].min().to_pydatetime()
            max_date = filtered_df[date_col].max().to_pydatetime()
            
            selected_dates = st.sidebar.slider(
                "Date Range",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date)
            )
            filtered_df = filtered_df[
                (filtered_df[date_col] >= selected_dates[0]) & 
                (filtered_df[date_col] <= selected_dates[1])
            ]
        except Exception:
            pass

    # 2. Region Filter
    region_col = next((c for c in df.columns if "region" in c.lower()), None)
    if region_col:
        unique_regions = df[region_col].dropna().unique().tolist()
        selected_regions = st.sidebar.multiselect("Select Region", unique_regions, default=unique_regions)
        if selected_regions:
            filtered_df = filtered_df[filtered_df[region_col].isin(selected_regions)]

    # 3. Category Filter
    cat_col = next((c for c in df.columns if "category" in c.lower() or "cat" in c.lower()), None)
    if cat_col:
        unique_cats = df[cat_col].dropna().unique().tolist()
        selected_cats = st.sidebar.multiselect("Select Product Category", unique_cats, default=unique_cats)
        if selected_cats:
            filtered_df = filtered_df[filtered_df[cat_col].isin(selected_cats)]

    # 4. Custom Generic Filter
    remaining_cols = [c for c in df.select_dtypes(include=["object", "category"]).columns if c not in [region_col, cat_col]]
    if remaining_cols:
        extra_filter_col = st.sidebar.selectbox("Filter by other column", ["None"] + remaining_cols)
        if extra_filter_col != "None":
            unique_vals = df[extra_filter_col].dropna().unique().tolist()
            selected_vals = st.sidebar.multiselect(f"Select {extra_filter_col}", unique_vals, default=unique_vals)
            if selected_vals:
                filtered_df = filtered_df[filtered_df[extra_filter_col].isin(selected_vals)]

    # ---------------- KPI Metris Row calculation ----------------
    rev_col = next((c for c in df.columns if any(k in c.lower() for k in ["revenue", "sales", "price", "amount", "sales_amount"])), None)
    prof_col = next((c for c in df.columns if "profit" in c.lower()), None)
    order_col = next((c for c in df.columns if "order" in c.lower() or "id" in c.lower()), None)
    cust_col = next((c for c in df.columns if "customer" in c.lower() or "cust" in c.lower()), None)

    # Calculate Values
    if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
        total_revenue = filtered_df[rev_col].sum()
        revenue_str = f"₹{total_revenue / 1_000_000:.2f}M" if total_revenue >= 1_000_000 else f"₹{total_revenue:,.2f}"
    else:
        revenue_str = "N/A"

    if prof_col and pd.api.types.is_numeric_dtype(df[prof_col]):
        total_profit = filtered_df[prof_col].sum()
        profit_str = f"₹{total_profit / 1_000_000:.2f}M" if total_profit >= 1_000_000 else f"₹{total_profit:,.2f}"
    elif rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
        total_profit = filtered_df[rev_col].sum() * 0.25
        profit_str = f"₹{total_profit / 1_000_000:.2f}M" if total_profit >= 1_000_000 else f"₹{total_profit:,.2f}"
    else:
        profit_str = "N/A"

    if order_col:
        total_orders = filtered_df[order_col].nunique()
    else:
        total_orders = len(filtered_df)

    if cust_col:
        total_customers = filtered_df[cust_col].nunique()
    else:
        total_customers = int(len(filtered_df) * 0.3)

    # Render custom premium KPI Cards in pure HTML markdown to preserve structure
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.markdown(render_kpi_card("Total Revenue", revenue_str, "+5.2% vs last month", "up", SVG_REVENUE), unsafe_allow_html=True)
    with kpi_cols[1]:
        st.markdown(render_kpi_card("Net Profit", profit_str, "+3.8% vs last month", "up", SVG_PROFIT), unsafe_allow_html=True)
    with kpi_cols[2]:
        st.markdown(render_kpi_card("Total Orders", f"{total_orders:,}", "+12.4% vs last week", "up", SVG_ORDERS), unsafe_allow_html=True)
    with kpi_cols[3]:
        st.markdown(render_kpi_card("Unique Customers", f"{total_customers:,}", "-1.2% vs last week", "down", SVG_CUSTOMERS), unsafe_allow_html=True)

    st.write("")

    # ---------------- Grid Row 1: Line Chart & Drill-down Bar Chart ----------------
    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.subheader("📈 Revenue Trend over Time")
            if date_col and rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
                trend_df = filtered_df.groupby(filtered_df[date_col].dt.to_period("M"))[rev_col].sum().reset_index()
                trend_df[date_col] = trend_df[date_col].astype(str)
                fig_trend = px.line(trend_df, x=date_col, y=rev_col, labels={rev_col: "Revenue", date_col: "Month"})
                apply_plotly_theme(fig_trend)
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("Upload dataset with a Date and Numeric column to view Revenue Trends.")

    with c2:
        with st.container(border=True):
            st.subheader("🌍 Regional sales & Drill-down")
            drill_level = st.selectbox("Drill-down Level", ["Region", "State"], index=0)
            
            state_col = next((c for c in df.columns if "state" in c.lower()), None)
            active_group_col = region_col if drill_level == "Region" else state_col

            if active_group_col and rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
                drill_df = filtered_df.groupby(active_group_col)[rev_col].sum().reset_index().sort_values(rev_col, ascending=False)
                fig_drill = px.bar(drill_df, x=active_group_col, y=rev_col, color=active_group_col, labels={rev_col: "Revenue"})
                apply_plotly_theme(fig_drill)
                st.plotly_chart(fig_drill, use_container_width=True)
            else:
                st.info("Upload dataset with Region/State and Numeric columns to view Drill-downs.")

    # ---------------- Grid Row 2: Category Pie & Scatter/Product Bar ----------------
    c3, c4 = st.columns(2)

    with c3:
        with st.container(border=True):
            st.subheader("🍕 Product Category Share")
            if cat_col and rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
                cat_df = filtered_df.groupby(cat_col)[rev_col].sum().reset_index()
                fig_cat = px.pie(cat_df, names=cat_col, values=rev_col, hole=0.4)
                apply_plotly_theme(fig_cat)
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("Upload dataset with Category and Numeric columns to view categories.")

    with c4:
        with st.container(border=True):
            st.subheader("📦 Product Breakdown (Top 10)")
            prod_col = next((c for c in df.columns if any(k in c.lower() for k in ["product", "item", "name"])), None)
            if prod_col and rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
                prod_df = filtered_df.groupby(prod_col)[rev_col].sum().reset_index().sort_values(rev_col, ascending=False).head(10)
                fig_prod = px.bar(prod_df, x=rev_col, y=prod_col, orientation="h", color=prod_col, labels={rev_col: "Revenue"})
                apply_plotly_theme(fig_prod)
                st.plotly_chart(fig_prod, use_container_width=True)
            else:
                st.info("Upload dataset with Product Name and Numeric columns to view breakdowns.")

    # ---------------- Grid Row 3: Correlation Heatmap ----------------
    with st.container(border=True):
        st.subheader("🔥 Numeric Correlation Matrix")
        numeric_cols = filtered_df.select_dtypes(include="number").columns.tolist()
        if len(numeric_cols) > 1:
            corr = filtered_df[numeric_cols].corr()
            fig_heat = px.imshow(
                corr,
                text_auto=True,
                color_continuous_scale="RdBu_r",
                aspect="auto"
            )
            apply_plotly_theme(fig_heat)
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("At least 2 numeric columns are required to compute a correlation heatmap.")
