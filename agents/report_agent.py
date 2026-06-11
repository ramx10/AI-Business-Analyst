from config.llm import llm
from utils.helper import truncate_dataframe
import time


class ReportAgent:

    def generate_report(
            self,
            schema_info,
            cleaning_info,
            kpi_info,
            insights,
            mode="detailed"):

        rows = kpi_info.get("rows", "N/A")
        cols = kpi_info.get("columns", "N/A")
        missing = cleaning_info.get("missing_values", "N/A") if isinstance(cleaning_info, dict) else "N/A"
        duplicates = cleaning_info.get("duplicate_rows", "N/A") if isinstance(cleaning_info, dict) else "N/A"

        if mode == "summary":
            prompt = f"""
You are a senior business analyst producing an executive summary. CRITICAL: output MUST be strictly formatted.

Dataset: {rows} rows × {cols} columns
Missing values: {missing}  |  Duplicate rows: {duplicates}

Insights:
{insights}

Generate exactly these 4 sections. Use **bold** for headers only. Every line must be a bullet point starting with "-". No paragraphs, no numbered lists.

**EXECUTIVE SUMMARY**
- {rows} rows × {cols} cols — {missing} missing, {duplicates} duplicates — [one-line data quality verdict]
- [one-line key business insight from the data]
- [one-line overall assessment]

**KEY METRICS**
- Rows: {rows} | Columns: {cols} | Missing: {missing} | Duplicates: {duplicates}
- [one additional metric insight]

**TOP FINDINGS**
- [finding 1 — include specific number]
- [finding 2 — include specific number]
- [finding 3 — include specific number]

**RECOMMENDATIONS**
- [recommendation 1 — priority action]
- [recommendation 2 — secondary action]

Total output: max 12 lines. Each bullet max 120 characters. No extra text, no introduction, no conclusion.
"""
        else:
            prompt = f"""
You are a senior business analyst. CRITICAL: output MUST be strictly formatted.

Dataset: {rows} rows × {cols} columns
Missing values: {missing}  |  Duplicate rows: {duplicates}

Detailed Insights:
{insights}

Generate exactly these 6 sections. Use **bold** for headers. Every line must be a bullet point starting with "-". No paragraphs.

**EXECUTIVE SUMMARY**
- [overall data quality assessment — mention {rows} rows, {cols} cols, {missing} missing, {duplicates} duplicates]
- [primary business insight from the analysis]
- [business impact — what this means for the organization]
- [key takeaway]

**DATASET OVERVIEW**
- Dimensions: {rows} rows × {cols} columns
- Completeness: {missing} missing values, {duplicates} duplicate rows
- [schema characteristic — data types, key columns]
- [data quality implication for analysis]

**KEY FINDINGS**
- [finding 1 — specific number-driven observation]
- [finding 2 — trend or pattern with data reference]
- [finding 3 — correlation or relationship found]
- [finding 4 — outlier or notable data point]
- [finding 5 — business-relevant insight]
- [finding 6 — additional data-backed discovery]

**RISKS & CHALLENGES**
- [risk 1 — missing/incomplete data impact]
- [risk 2 — data quality concern]
- [risk 3 — business implication of findings]
- [risk 4 — analytical limitation]

**STRATEGIC RECOMMENDATIONS**
- [recommendation 1 — tied to a specific finding]
- [recommendation 2 — tied to a specific risk]
- [recommendation 3 — process improvement]
- [recommendation 4 — data quality action]
- [recommendation 5 — long-term strategy]

**CONCLUSION**
- [summary of most important insight]
- [call to action]
- [expected business outcome]

Every bullet must be substantive. Include specific numbers where available. No placeholder text. No filler.
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