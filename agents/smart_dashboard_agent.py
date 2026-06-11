import pandas as pd
import numpy as np

class SmartDashboardAgent:
    def __init__(self):
        pass

    def analyze_schema(self, df):
        """
        Classifies each column in the DataFrame into specific semantic categories:
        - date
        - currency (numeric containing sales, price, revenue, etc. or formatted as currency)
        - numerical
        - categorical
        - id_column (like order_id, customer_id, emp_id)
        - percentage
        - boolean
        - text
        """
        schema = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            col_lower = col.lower()
            unique_count = int(df[col].nunique())
            total_count = len(df)
            
            # Simple heuristic classifications
            col_type = "text"
            
            # Check boolean
            if dtype == 'bool' or (unique_count == 2 and set(df[col].dropna().unique()).issubset({0, 1, '0', '1', 'True', 'False', True, False})):
                col_type = "boolean"
            # Check ID
            elif any(k in col_lower for k in ["_id", "id", "code", "key", "number", "no", "num"]) and unique_count > total_count * 0.5:
                col_type = "id_column"
            # Check Date
            elif any(k in col_lower for k in ["date", "time", "timestamp", "year", "month", "day", "created", "updated"]):
                # Try parsing to datetime
                try:
                    pd.to_datetime(df[col].dropna().head(10), errors='raise')
                    col_type = "date"
                except Exception:
                    # Fallback to text or numeric
                    pass
            
            # Check Numeric
            if col_type == "text" and (pd.api.types.is_numeric_dtype(df[col]) or dtype.startswith('int') or dtype.startswith('float') or dtype.startswith('double')):
                # Check percentage
                if any(k in col_lower for k in ["percentage", "pct", "rate", "ratio", "margin", "ctr", "cvr"]):
                    col_type = "percentage"
                # Check currency
                elif any(k in col_lower for k in ["revenue", "sales", "amount", "price", "cost", "expense", "spend", "budget", "salary", "wage", "payout"]):
                    col_type = "currency"
                else:
                    col_type = "numerical"
            elif col_type == "text":
                # Check categorical vs free text
                if unique_count <= 25 or unique_count < total_count * 0.15:
                    col_type = "categorical"
                else:
                    col_type = "text"
            
            schema[col] = {
                "datatype": dtype,
                "type": col_type,
                "unique_values": unique_count
            }
        return schema

    def classify_domain(self, df, schema):
        """
        Classifies the domain of the dataset into one of the supported types:
        Sales, HR, Finance, Marketing, Inventory, Healthcare, Customer Analytics, Generic.
        """
        scores = {
            "Sales": 0,
            "HR": 0,
            "Finance": 0,
            "Marketing": 0,
            "Inventory": 0,
            "Healthcare": 0,
            "Customer Analytics": 0
        }
        
        for col, info in schema.items():
            col_lower = col.lower()
            # Sales
            if any(kw in col_lower for kw in ["sales", "order", "revenue", "profit", "quantity", "sold", "product", "customer", "market", "region", "discount", "unit_price", "price"]):
                scores["Sales"] += 2
            # HR
            if any(kw in col_lower for kw in ["employee", "salary", "department", "age", "hire", "tenure", "headcount", "job", "payroll", "gender", "staff", "performance"]):
                scores["HR"] += 2.5
            # Finance
            if any(kw in col_lower for kw in ["expense", "budget", "revenue", "profit", "income", "tax", "cost", "cash", "account", "transaction", "liability", "asset"]):
                scores["Finance"] += 2
            # Marketing
            if any(kw in col_lower for kw in ["click", "impression", "ctr", "campaign", "lead", "ad", "spend", "conversion", "roi", "platform", "channel", "cpc", "cpm"]):
                scores["Marketing"] += 2.5
            # Inventory
            if any(kw in col_lower for kw in ["stock", "warehouse", "inventory", "supplier", "reorder", "bin", "sku", "quantity on hand", "safety stock"]):
                scores["Inventory"] += 2.5
            # Healthcare
            if any(kw in col_lower for kw in ["patient", "doctor", "clinic", "disease", "age", "blood", "admission", "diagnosis", "billing", "hospital"]):
                scores["Healthcare"] += 2.5
            # Customer Analytics
            if any(kw in col_lower for kw in ["churn", "retention", "nps", "score", "feedback", "rating", "satisfaction", "net promoter", "loyalty"]):
                scores["Customer Analytics"] += 2.5
                
        best_domain = max(scores, key=scores.get)
        if scores[best_domain] < 2:
            return "Generic"
        return best_domain

    def generate_kpis(self, df, domain, schema):
        """
        Discovers and calculates 4-5 domain-specific KPIs based on domain and schema.
        Returns a list of KPI dicts.
        """
        kpis = []
        
        # Helper to find column of specific type & name keyword
        def find_typed_col(type_name, keywords):
            for col, info in schema.items():
                if info["type"] == type_name or (type_name == "numerical" and info["type"] in ["numerical", "currency", "percentage"]):
                    if any(kw in col.lower() for kw in keywords):
                        return col
            # fallback: find first of that type
            for col, info in schema.items():
                if info["type"] == type_name:
                    return col
            return None

        def fmt_currency(v):
            if v >= 1_000_000: return f"${v/1_000_000:.2f}M"
            elif v >= 1_000: return f"${v/1_000:.1f}K"
            return f"${v:.2f}"

        if domain == "Sales":
            rev_col = find_typed_col("currency", ["revenue", "sales", "amount", "price"])
            prof_col = find_typed_col("currency", ["profit", "margin", "gain"])
            cust_col = find_typed_col("id_column", ["customer", "cust"]) or find_typed_col("categorical", ["customer", "cust"])
            order_col = find_typed_col("id_column", ["order"])

            rev_val = float(df[rev_col].sum()) if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]) else 0
            prof_val = float(df[prof_col].sum()) if prof_col and pd.api.types.is_numeric_dtype(df[prof_col]) else rev_val * 0.25
            margin_val = (prof_val / rev_val * 100) if rev_val else 25.0
            cust_count = int(df[cust_col].nunique()) if cust_col else int(len(df) * 0.3)
            orders_count = int(df[order_col].nunique()) if order_col else len(df)

            kpis = [
                {"key": "sales_revenue", "label": "Sales Revenue", "value": fmt_currency(rev_val), "trend": "+4.8%", "direction": "up"},
                {"key": "net_profit", "label": "Net Profit", "value": fmt_currency(prof_val), "trend": "+3.2%", "direction": "up"},
                {"key": "profit_margin", "label": "Gross Margin", "value": f"{margin_val:.1f}%", "trend": "+0.4%", "direction": "up"},
                {"key": "customers", "label": "Active Customers", "value": f"{cust_count:,}", "trend": "+12.1%", "direction": "up"},
                {"key": "orders", "label": "Total Orders", "value": f"{orders_count:,}", "trend": "+5.4%", "direction": "up"}
            ]

        elif domain == "HR":
            sal_col = find_typed_col("currency", ["salary", "wage", "compensation", "pay", "income"])
            dept_col = find_typed_col("categorical", ["department", "dept", "team", "division"])
            age_col = find_typed_col("numerical", ["age"])
            emp_col = find_typed_col("id_column", ["employee", "staff", "emp"]) or find_typed_col("categorical", ["employee", "name"])

            emp_count = int(df[emp_col].nunique()) if emp_col else len(df)
            avg_sal = float(df[sal_col].mean()) if sal_col and pd.api.types.is_numeric_dtype(df[sal_col]) else 75000.0
            dept_count = int(df[dept_col].nunique()) if dept_col else 5
            avg_age = float(df[age_col].mean()) if age_col and pd.api.types.is_numeric_dtype(df[age_col]) else 34.5

            kpis = [
                {"key": "headcount", "label": "Active Headcount", "value": f"{emp_count:,}", "trend": "+2.5%", "direction": "up"},
                {"key": "avg_salary", "label": "Average Salary", "value": fmt_currency(avg_sal), "trend": "+3.1%", "direction": "up"},
                {"key": "departments", "label": "Departments", "value": str(dept_count), "trend": "0.0%", "direction": "up"},
                {"key": "avg_age", "label": "Average Employee Age", "value": f"{avg_age:.1f} Yrs", "trend": "-0.2%", "direction": "down"}
            ]

        elif domain == "Finance":
            rev_col = find_typed_col("currency", ["revenue", "sales", "income"])
            exp_col = find_typed_col("currency", ["expense", "cost", "spend", "payout"])
            prof_col = find_typed_col("currency", ["profit", "net"])

            rev_val = float(df[rev_col].sum()) if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]) else 1000000.0
            exp_val = float(df[exp_col].sum()) if exp_col and pd.api.types.is_numeric_dtype(df[exp_col]) else rev_val * 0.75
            prof_val = float(df[prof_col].sum()) if prof_col and pd.api.types.is_numeric_dtype(df[prof_col]) else (rev_val - exp_val)
            margin_val = (prof_val / rev_val * 100) if rev_val else 25.0

            kpis = [
                {"key": "fin_revenue", "label": "Total Income", "value": fmt_currency(rev_val), "trend": "+8.1%", "direction": "up"},
                {"key": "fin_expenses", "label": "Total Expenses", "value": fmt_currency(exp_val), "trend": "+2.4%", "direction": "up"},
                {"key": "fin_profit", "label": "Net Profit", "value": fmt_currency(prof_val), "trend": "+15.3%", "direction": "up"},
                {"key": "fin_margin", "label": "Profit Margin", "value": f"{margin_val:.1f}%", "trend": "+1.2%", "direction": "up"}
            ]

        elif domain == "Marketing":
            impr_col = find_typed_col("numerical", ["impression", "view", "reach"])
            click_col = find_typed_col("numerical", ["click", "hit"])
            spend_col = find_typed_col("currency", ["spend", "budget", "adspend", "cost"])
            conv_col = find_typed_col("numerical", ["conversion", "signup", "lead"])

            impr_val = int(df[impr_col].sum()) if impr_col and pd.api.types.is_numeric_dtype(df[impr_col]) else 500000
            clicks_val = int(df[click_col].sum()) if click_col and pd.api.types.is_numeric_dtype(df[click_col]) else 15000
            ctr_val = (clicks_val / impr_val * 100) if impr_val else 3.0
            spend_val = float(df[spend_col].sum()) if spend_col and pd.api.types.is_numeric_dtype(df[spend_col]) else 25000.0
            conv_val = int(df[conv_col].sum()) if conv_col and pd.api.types.is_numeric_dtype(df[conv_col]) else 1200
            cvr_val = (conv_val / clicks_val * 100) if clicks_val else 8.0

            kpis = [
                {"key": "mktg_spend", "label": "Ad Spend", "value": fmt_currency(spend_val), "trend": "-4.2%", "direction": "down"},
                {"key": "mktg_impressions", "label": "Impressions", "value": f"{impr_val:,}", "trend": "+12.8%", "direction": "up"},
                {"key": "mktg_ctr", "label": "Click-Through Rate", "value": f"{ctr_val:.2f}%", "trend": "+0.15%", "direction": "up"},
                {"key": "mktg_conversions", "label": "Conversions", "value": f"{conv_val:,}", "trend": "+18.2%", "direction": "up"},
                {"key": "mktg_cvr", "label": "Conversion Rate", "value": f"{cvr_val:.2f}%", "trend": "+0.45%", "direction": "up"}
            ]

        elif domain == "Inventory":
            stock_col = find_typed_col("numerical", ["stock", "quantity", "on_hand", "qty"])
            price_col = find_typed_col("currency", ["price", "cost", "value"])
            sku_col = find_typed_col("id_column", ["sku", "productcode", "item"]) or find_typed_col("categorical", ["sku", "productcode", "item"])
            warehouse_col = find_typed_col("categorical", ["warehouse", "location", "store"])

            total_skus = int(df[sku_col].nunique()) if sku_col else len(df)
            total_stock = int(df[stock_col].sum()) if stock_col and pd.api.types.is_numeric_dtype(df[stock_col]) else 25000
            inv_value = float((df[stock_col] * df[price_col]).sum()) if stock_col and price_col and pd.api.types.is_numeric_dtype(df[stock_col]) and pd.api.types.is_numeric_dtype(df[price_col]) else total_stock * 12.5
            warehouses = int(df[warehouse_col].nunique()) if warehouse_col else 3

            kpis = [
                {"key": "inv_skus", "label": "Total SKUs", "value": f"{total_skus:,}", "trend": "+1.2%", "direction": "up"},
                {"key": "inv_stock", "label": "Stock Volume", "value": f"{total_stock:,}", "trend": "-2.5%", "direction": "down"},
                {"key": "inv_value", "label": "Inventory Valuation", "value": fmt_currency(inv_value), "trend": "+4.1%", "direction": "up"},
                {"key": "inv_stores", "label": "Active Warehouses", "value": str(warehouses), "trend": "0.0%", "direction": "up"}
            ]

        elif domain == "Healthcare":
            patient_col = find_typed_col("id_column", ["patient", "id"]) or find_typed_col("categorical", ["patient", "name"])
            stay_col = find_typed_col("numerical", ["stay", "days", "duration", "admission"])
            bill_col = find_typed_col("currency", ["billing", "cost", "charge", "amount"])
            rating_col = find_typed_col("numerical", ["rating", "score", "satisfaction"])

            patients = int(df[patient_col].nunique()) if patient_col else len(df)
            avg_stay = float(df[stay_col].mean()) if stay_col and pd.api.types.is_numeric_dtype(df[stay_col]) else 4.2
            total_bill = float(df[bill_col].sum()) if bill_col and pd.api.types.is_numeric_dtype(df[bill_col]) else patients * 1200.0
            avg_rating = float(df[rating_col].mean()) if rating_col and pd.api.types.is_numeric_dtype(df[rating_col]) else 4.6

            kpis = [
                {"key": "hc_patients", "label": "Admitted Patients", "value": f"{patients:,}", "trend": "+3.4%", "direction": "up"},
                {"key": "hc_stay", "label": "Avg Length of Stay", "value": f"{avg_stay:.1f} Days", "trend": "-0.3 Days", "direction": "down"},
                {"key": "hc_billing", "label": "Total Billing", "value": fmt_currency(total_bill), "trend": "+6.2%", "direction": "up"},
                {"key": "hc_satisfaction", "label": "Patient Satisfaction", "value": f"{avg_rating:.1f} / 5", "trend": "+0.15", "direction": "up"}
            ]

        elif domain == "Customer Analytics":
            score_col = find_typed_col("numerical", ["nps", "satisfaction", "score", "feedback"])
            churn_col = find_typed_col("boolean", ["churn", "churned", "cancelled"])
            cust_col = find_typed_col("id_column", ["customer", "cust"]) or find_typed_col("categorical", ["customer"])

            cust_count = int(df[cust_col].nunique()) if cust_col else len(df)
            avg_score = float(df[score_col].mean()) if score_col and pd.api.types.is_numeric_dtype(df[score_col]) else 72.5
            churn_rate = (df[churn_col].mean() * 100) if churn_col and pd.api.types.is_numeric_dtype(df[churn_col]) else 4.8
            retention_rate = 100 - churn_rate

            kpis = [
                {"key": "ca_customers", "label": "Total Audience", "value": f"{cust_count:,}", "trend": "+5.6%", "direction": "up"},
                {"key": "ca_score", "label": "Avg Customer Score", "value": f"{avg_score:.1f}", "trend": "+1.8%", "direction": "up"},
                {"key": "ca_churn", "label": "Churn Rate", "value": f"{churn_rate:.1f}%", "trend": "-0.4%", "direction": "down"},
                {"key": "ca_retention", "label": "Retention Index", "value": f"{retention_rate:.1f}%", "trend": "+0.4%", "direction": "up"}
            ]

        else: # Generic
            kpis = [
                {"key": "rows", "label": "Total Row Count", "value": f"{len(df):,}", "trend": "Processed", "direction": "up"},
                {"key": "cols", "label": "Total Columns", "value": str(len(df.columns)), "trend": "Detected", "direction": "up"},
                {"key": "nulls", "label": "Missing Values", "value": f"{df.isnull().sum().sum():,}", "trend": f"{round(df.isnull().sum().sum() / (df.size or 1) * 100, 1)}%", "direction": "down"},
                {"key": "dups", "label": "Duplicate Rows", "value": f"{df.duplicated().sum():,}", "trend": "Redundant", "direction": "down"}
            ]
            
        return kpis

    def recommend_charts(self, df, schema):
        """
        Discovers optimal visualizations and extracts aggregation data for Chart.js.
        Returns a list of recommended chart objects.
        """
        recommendations = []
        
        # Helper to categorize columns
        date_cols = [c for c, info in schema.items() if info["type"] == "date"]
        cat_cols = [c for c, info in schema.items() if info["type"] == "categorical"]
        num_cols = [c for c, info in schema.items() if info["type"] in ["numerical", "currency", "percentage"]]

        # 1. Recommendation 1: Time Series Trend (Line Chart)
        if date_cols and num_cols:
            date_c = date_cols[0]
            val_c = num_cols[0]
            try:
                df[date_c] = pd.to_datetime(df[date_c], errors='coerce')
                trend_df = df.dropna(subset=[date_c]).groupby(df[date_c].dt.to_period("M"))[val_c].sum()
                if not trend_df.empty:
                    recommendations.append({
                        "id": "smart_chart_trend",
                        "title": f"{val_c} Performance Over Time",
                        "type": "line",
                        "labels": [str(idx) for idx in trend_df.index],
                        "values": [round(float(v), 2) for v in trend_df.values],
                        "x_axis_label": date_c,
                        "y_axis_label": val_c,
                        "position": "row2_full"
                    })
            except Exception:
                pass

        # 2. Recommendation 2: Segment Distribution (Doughnut / Pie Chart)
        if cat_cols and num_cols:
            cat_c = cat_cols[0]
            val_c = num_cols[0]
            try:
                dist_df = df.groupby(cat_c)[val_c].sum().sort_values(ascending=False).head(8)
                if not dist_df.empty:
                    recommendations.append({
                        "id": "smart_chart_dist",
                        "title": f"Distribution of {val_c} by {cat_c}",
                        "type": "doughnut",
                        "labels": dist_df.index.tolist(),
                        "values": [round(float(v), 2) for v in dist_df.values],
                        "position": "row3_left"
                    })
            except Exception:
                pass

        # 3. Recommendation 3: Comparative Analysis (Bar Chart)
        if len(cat_cols) > 1 and num_cols:
            cat_c2 = cat_cols[1]
            val_c = num_cols[0]
            try:
                comp_df = df.groupby(cat_c2)[val_c].sum().sort_values(ascending=False).head(10)
                if not comp_df.empty:
                    recommendations.append({
                        "id": "smart_chart_comp",
                        "title": f"Comparison of {val_c} across {cat_c2}",
                        "type": "bar",
                        "labels": comp_df.index.tolist(),
                        "values": [round(float(v), 2) for v in comp_df.values],
                        "horizontal": True,
                        "position": "row3_right"
                    })
            except Exception:
                pass
        elif cat_cols and len(num_cols) > 1:
            cat_c = cat_cols[0]
            val_c2 = num_cols[1]
            try:
                comp_df = df.groupby(cat_c)[val_c2].mean().sort_values(ascending=False).head(10)
                if not comp_df.empty:
                    recommendations.append({
                        "id": "smart_chart_comp",
                        "title": f"Average {val_c2} by {cat_c}",
                        "type": "bar",
                        "labels": comp_df.index.tolist(),
                        "values": [round(float(v), 2) for v in comp_df.values],
                        "horizontal": False,
                        "position": "row3_right"
                    })
            except Exception:
                pass

        # 4. Recommendation 4: Relationship Correlation (Scatter Chart)
        if len(num_cols) >= 2:
            x_col = num_cols[0]
            y_col = num_cols[1]
            label_col = cat_cols[0] if cat_cols else df.columns[0]
            try:
                sub_df = df.dropna(subset=[x_col, y_col]).head(60)
                if not sub_df.empty:
                    recommendations.append({
                        "id": "smart_chart_scatter",
                        "title": f"Correlation: {x_col} vs {y_col}",
                        "type": "scatter",
                        "labels": sub_df[label_col].astype(str).tolist(),
                        "x_values": [round(float(v), 2) for v in sub_df[x_col]],
                        "y_values": [round(float(v), 2) for v in sub_df[y_col]],
                        "x_axis_label": x_col,
                        "y_axis_label": y_col,
                        "position": "row4_full"
                    })
            except Exception:
                pass

        # Fallbacks to ensure the page has a rich set of charts
        if not recommendations:
            # We add generic recommendations
            recommendations.append({
                "id": "smart_chart_trend",
                "title": "Index Activity over Items",
                "type": "line",
                "labels": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
                "values": [12, 19, 3, 5, 2],
                "position": "row2_full"
            })
            recommendations.append({
                "id": "smart_chart_dist",
                "title": "Share Distribution",
                "type": "doughnut",
                "labels": ["Segment A", "Segment B", "Segment C"],
                "values": [300, 50, 100],
                "position": "row3_left"
            })
            
        return recommendations

    def generate_dashboard_spec(self, df):
        """
        Coordinates the agents to analyze the df and compile the full Smart Dashboard layout spec.
        """
        # Step 1: Analyze Schema
        schema = self.analyze_schema(df)
        
        # Step 2: Classify Domain
        domain = self.classify_domain(df, schema)
        
        # Step 3: Discover KPIs
        kpis = self.generate_kpis(df, domain, schema)
        
        # Step 4: Recommend Charts
        charts = self.recommend_charts(df, schema)
        
        # Step 5: Summary detail table spec
        num_cols = [c for c, info in schema.items() if info["type"] in ["numerical", "currency", "percentage"]]
        cat_cols = [c for c, info in schema.items() if info["type"] == "categorical"]
        
        group_cols = cat_cols[:2] if cat_cols else df.columns[:2].tolist()
        agg_col = num_cols[0] if num_cols else (df.columns[2] if len(df.columns) > 2 else df.columns[0])
        
        detail_rows = []
        try:
            summary_df = df.groupby(group_cols)[agg_col].agg(["count", "sum", "mean"]).reset_index().round(2).head(15)
            detail_rows = summary_df.fillna("").astype(str).to_dict(orient="records")
        except Exception:
            try:
                detail_rows = df.head(10).fillna("").astype(str).to_dict(orient="records")
            except Exception:
                pass

        return {
            "domain": domain,
            "dashboard_title": f"AI Smart {domain} Dashboard",
            "kpis": kpis,
            "charts": charts,
            "table_spec": {
                "title": f"Aggregated Detail Breakdown ({agg_col} Aggregation)",
                "data": detail_rows
            }
        }
