from config.llm import llm
from utils.helper import truncate_dataframe


class AIInsightAgent:

    def generate_insights(
            self,
            schema_info,
            cleaning_info,
            kpi_info):

        # Compress input
        summary = {
            "columns": len(schema_info),
            "missing_values": cleaning_info["missing_values"],
            "duplicate_rows": cleaning_info["duplicate_rows"],
            "rows": kpi_info["rows"],
            "columns_count": kpi_info["columns"]
        }

        prompt = f"""
You are a senior business analyst.

Dataset Summary:

{summary}

Generate:

1. Key Business Insights
2. Trends
3. Risks
4. Opportunities
5. Recommendations

Use bullet points and keep answers concise.
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