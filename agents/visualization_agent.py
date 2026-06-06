import pandas as pd
import plotly.express as px


class VisualizationAgent:

    def create_visualizations(self, df: pd.DataFrame):

        charts = {}

        # Revenue by Region
        if "region" in df.columns and "revenue" in df.columns:

            region_revenue = (
                df.groupby("region")["revenue"]
                .sum()
                .reset_index()
            )

            fig1 = px.bar(
                region_revenue,
                x="region",
                y="revenue",
                title="Revenue by Region"
            )

            charts["region_bar"] = fig1

        # Revenue by Product Category
        if "product_category" in df.columns and "revenue" in df.columns:

            category_revenue = (
                df.groupby("product_category")["revenue"]
                .sum()
                .reset_index()
            )

            fig2 = px.pie(
                category_revenue,
                names="product_category",
                values="revenue",
                title="Revenue by Product Category"
            )

            charts["category_pie"] = fig2

        return charts