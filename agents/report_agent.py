from config.llm import llm
from utils.helper import truncate_dataframe
import time


class ReportAgent:

    def generate_report(
            self,
            schema_info,
            cleaning_info,
            insights):

        prompt = f"""
You are a senior business analyst.

Business Insights:

{insights}

Generate:

1. Executive Summary
2. Dataset Overview
3. Key Findings
4. Risks
5. Recommendations
6. Conclusion

Keep the report concise and professional.
"""

        start = time.time()

        try:

            response = llm.invoke(prompt)

            print(
                f"Report Agent Time: {time.time()-start:.2f} sec"
            )

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