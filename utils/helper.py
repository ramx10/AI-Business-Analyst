"""
utils/helper.py — General-purpose helper utilities.
"""
import pandas as pd


def safe_read_csv(file) -> pd.DataFrame:
    """Read a CSV file uploaded via Streamlit, trying common encodings."""
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            file.seek(0)
            return pd.read_csv(file, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not read the CSV file with any supported encoding.")


def truncate_dataframe(df: pd.DataFrame, max_rows: int = 10_000) -> pd.DataFrame:
    """Return the first *max_rows* rows of df to keep LLM prompts small."""
    if len(df) > max_rows:
        return df.head(max_rows)
    return df
