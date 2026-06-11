from config.llm import llm
from utils.helper import truncate_dataframe


class AIInsightAgent:

    def generate_insights(
            self,
            schema_info,
            cleaning_info,
            kpi_info,
            mode="detailed"):

        summary = {
            "columns": len(schema_info),
            "missing_values": cleaning_info["missing_values"],
            "duplicate_rows": cleaning_info["duplicate_rows"],
            "rows": kpi_info["rows"],
            "columns_count": kpi_info["columns"]
        }

        if mode == "summary":
            prompt = f"""
You are a senior business analyst. Produce a VERY SHORT set of insights for an executive summary.

Dataset: {summary["rows"]} rows, {summary["columns_count"]} cols, {summary["missing_values"]} missing, {summary["duplicate_rows"]} duplicates

Output exactly 3 bullet points total:
- One key business insight
- One critical finding
- One urgent recommendation

Max 2 lines per bullet. No headers, no sections, no introduction.
"""
        else:
            prompt = f"""
You are a senior business analyst producing detailed insights.

Dataset Summary:
{summary}

Generate 5 sections with bullet points:

1. Key Business Insights — 3-4 data-backed observations
2. Trends & Patterns — 2-3 notable trends
3. Risks — 2-3 specific risks with business impact
4. Opportunities — 2-3 actionable opportunities
5. Recommendations — 3-4 prioritized recommendations

Be specific, mention column names, use numbers. Each bullet max 2 lines.
"""

        try:

            response = llm.invoke(prompt)

            return response.content

        except Exception as e:

            if "rate_limit" in str(e).lower() or "RESOURCE_EXHAUSTED" in str(e):

                return """
## Groq Rate Limit Exceeded

Possible solutions:

1. Wait 1 minute and try again.
2. Generate a new Groq API key at console.groq.com.
3. Reduce prompt size or dataset rows.
"""

            return f"Error:\n{str(e)}"