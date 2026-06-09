import json
import pandas as pd

from config.llm import llm
from utils.helper import truncate_dataframe


class NLQAgent:

    def _build_context(self, df: pd.DataFrame) -> str:
        buf = []
        buf.append(f"Dataset has {len(df)} rows and {len(df.columns)} columns.\n")
        buf.append("\nColumns:\n")
        for col in df.columns:
            dtype = df[col].dtype
            nunique = df[col].nunique()
            missing = int(df[col].isnull().sum())
            buf.append(f"  - {col} ({dtype}): {nunique} unique values, {missing} missing\n")

        sample = truncate_dataframe(df, max_rows=5)
        buf.append("\nSample rows (first 5):\n")
        buf.append(sample.to_string())
        buf.append("\n")

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            buf.append("\nNumeric summary:\n")
            desc = df[numeric_cols].describe().round(2).fillna(0)
            buf.append(desc.to_string())
            buf.append("\n")

        return "".join(buf)

    def query(self, question: str, df: pd.DataFrame) -> dict:
        context = self._build_context(df)

        prompt = f"""You are a senior business analyst. Answer the user's question about their dataset.

Dataset Context:
{context}

User Question: {question}

Provide a structured JSON response with these fields:
- "answer": a clear, concise natural language answer
- "confidence": "high", "medium", or "low"
- "chart": null if no chart is needed, otherwise an object with:
  - "type": "bar", "line", "pie", "doughnut", "table", or "number"
  - "title": chart title
  - "labels": array of strings (for x-axis or categories)
  - "values": array of numbers
  - "dataset_label": label for the dataset (optional)

Rules:
1. If the question asks for a single number (revenue, count, average), use chart type "number".
2. If the question asks for a comparison across categories, use chart type "bar" or "pie".
3. If the question asks for a trend over time, use chart type "line".
4. If the question asks for a breakdown or distribution, use chart type "doughnut".
5. If no chart is appropriate, set chart to null.
6. Base your answer only on the provided dataset context.
7. Be specific and reference actual column names and values from the data.

Return ONLY valid JSON, no other text.
"""
        try:
            response = llm.invoke(prompt)
            raw = response.content.strip()
            if raw.startswith("```"):
                raw = raw.strip("`").strip()
                if raw.startswith("json"):
                    raw = raw[4:].strip()
            result = json.loads(raw)
            if not isinstance(result, dict):
                return {"answer": str(result), "confidence": "low", "chart": None}
            return {
                "answer": result.get("answer", raw),
                "confidence": result.get("confidence", "low"),
                "chart": result.get("chart"),
            }
        except json.JSONDecodeError:
            return {"answer": raw if 'raw' in dir() else response.content, "confidence": "low", "chart": None}
        except Exception as e:
            if "rate_limit" in str(e).lower() or "RESOURCE_EXHAUSTED" in str(e):
                return {
                    "answer": "Groq API rate limit exceeded. Please wait a minute and try again, or check your API key at console.groq.com.",
                    "confidence": "low",
                    "chart": None,
                }
            return {"answer": f"Error: {str(e)}", "confidence": "low", "chart": None}
