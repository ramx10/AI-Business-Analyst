"""
utils/metrics.py — DataFrame metric helpers.
"""
import pandas as pd


def basic_stats(df: pd.DataFrame) -> dict:
    """Return a dict of basic statistics about *df*."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "numeric_columns": df.select_dtypes(include="number").columns.tolist(),
        "categorical_columns": df.select_dtypes(include="object").columns.tolist(),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 ** 2, 2),
    }


def missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame showing missing value counts and percentages per column."""
    missing = df.isnull().sum()
    pct = (missing / len(df) * 100).round(2)
    summary = pd.DataFrame({"missing_count": missing, "missing_pct": pct})
    return summary[summary["missing_count"] > 0].sort_values("missing_count", ascending=False)
