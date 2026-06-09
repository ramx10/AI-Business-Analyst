"""
utils/helper.py — General-purpose helper utilities.
"""
import io
from pathlib import Path

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


def read_excel(file) -> pd.DataFrame:
    """Read an Excel file (.xlsx)."""
    return pd.read_excel(file, engine="openpyxl")


def read_json(file) -> pd.DataFrame:
    """Read a JSON file."""
    return pd.read_json(file)


def read_parquet(file) -> pd.DataFrame:
    """Read a Parquet file."""
    return pd.read_parquet(file, engine="pyarrow")


def read_dataset(file, filename: str = "") -> pd.DataFrame:
    """Auto-detect format from filename and read accordingly."""
    name = filename or getattr(file, "name", "")
    ext = Path(name).suffix.lower()
    if ext == ".csv":
        return safe_read_csv(file)
    elif ext == ".xlsx":
        return read_excel(file)
    elif ext == ".json":
        return read_json(file)
    elif ext == ".parquet":
        return read_parquet(file)
    else:
        raise ValueError(
            f"Unsupported file format '{ext}'. Supported: .csv, .xlsx, .json, .parquet"
        )


def truncate_dataframe(df: pd.DataFrame, max_rows: int = 10_000) -> pd.DataFrame:
    """Return the first *max_rows* rows of df to keep LLM prompts small."""
    if len(df) > max_rows:
        return df.head(max_rows)
    return df
