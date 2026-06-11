from config.llm import llm


class CompareAgent:

    def generate_comparison_insights(self, stats_current, stats_previous):
        prompt = f"""
You are a senior business analyst comparing two versions of a dataset:
- CURRENT (newest period)
- PREVIOUS (older period)

Analyze the raw statistics below and generate insights about what CHANGED between the two periods.

CURRENT Dataset:
- Rows: {stats_current['row_count']}
- Columns: {stats_current['column_count']}
- Column names and types: {stats_current['column_info']}
- Numeric column stats (count, mean, min, max, sum): {stats_current['numeric_summary']}
- Categorical column value_counts: {stats_current['cat_summary']}
- Missing values: {stats_current['missing_values']}
- Duplicate rows: {stats_current['duplicate_rows']}

PREVIOUS Dataset:
- Rows: {stats_previous['row_count']}
- Columns: {stats_previous['column_count']}
- Column names and types: {stats_previous['column_info']}
- Numeric column stats (count, mean, min, max, sum): {stats_previous['numeric_summary']}
- Categorical column value_counts: {stats_previous['cat_summary']}
- Missing values: {stats_previous['missing_values']}
- Duplicate rows: {stats_previous['duplicate_rows']}

Generate 5-8 bullet-point insights. Follow these rules:
1. For each numeric column common to both datasets, calculate the % change (current vs previous) and absolute change.
2. Identify columns whose names suggest business meaning (profit, revenue, sales, cost, expense, income, growth, count, volume, price, rate, score, rating, quantity, amount, margin, etc.) and prioritize them.
3. If the column has a date/time interpretation, mention the implied time period comparison.
4. For categorical columns, note if the distribution changed significantly.
5. Highlight the most important business-relevant changes with specific numbers.
6. Note data quality changes (missing values, duplicates, row count).
7. End with a bottom-line assessment.

Output format: each bullet starts with "- " and is a single sentence with specific numbers. No headers, no markdown formatting beyond bullets. Max 8 bullets.
"""
        try:
            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            if "rate_limit" in str(e).lower() or "RESOURCE_EXHAUSTED" in str(e):
                return "- Rate limit exceeded. Please wait and try again."
            return f"- Error generating insights: {str(e)}"
