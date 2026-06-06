"""
utils/chart_utils.py — Reusable Plotly chart builders.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    """Return a Plotly bar chart figure."""
    return px.bar(df, x=x, y=y, title=title)


def line_chart(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    """Return a Plotly line chart figure."""
    return px.line(df, x=x, y=y, title=title)


def pie_chart(df: pd.DataFrame, names: str, values: str = None, title: str = "") -> go.Figure:
    """Return a Plotly pie chart figure."""
    return px.pie(df, names=names, values=values, title=title)


def histogram(df: pd.DataFrame, x: str, title: str = "") -> go.Figure:
    """Return a Plotly histogram figure."""
    return px.histogram(df, x=x, title=title)


def box_plot(df: pd.DataFrame, y: str, title: str = "") -> go.Figure:
    """Return a Plotly box plot figure."""
    return px.box(df, y=y, title=title)


def correlation_heatmap(df: pd.DataFrame, title: str = "Correlation Heatmap") -> go.Figure:
    """Return a Plotly correlation heatmap for numeric columns in *df*."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        raise ValueError("DataFrame has no numeric columns for a correlation heatmap.")
    corr = df[numeric_cols].corr()
    return px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        aspect="auto",
        title=title,
    )
