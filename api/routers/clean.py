import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from api.session_store import load_df, save_df, session_exists
from agents.cleaning_agent import DataCleaningAgent

router = APIRouter()
agent = DataCleaningAgent()


@router.get("/clean/preview")
async def clean_preview(session_id: str = Query(...)):
    """Return data quality metrics without modifying the dataset."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        result = agent.analyze_data_quality(df)

        missing_by_col = {
            col: int(df[col].isnull().sum())
            for col in df.columns
            if df[col].isnull().sum() > 0
        }
        missing_pct_by_col = {
            col: round(df[col].isnull().mean() * 100, 2)
            for col in missing_by_col
        }

        return JSONResponse({
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "total_missing": int(df.isnull().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "missing_by_column": missing_by_col,
            "missing_pct_by_column": missing_pct_by_col,
            "completeness_pct": round((1 - df.isnull().mean().mean()) * 100, 2),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clean/apply")
async def clean_apply(session_id: str = Query(...)):
    """Apply auto-cleaning (drop duplicates + median/mode imputation) and save."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        before_rows = len(df)
        before_missing = int(df.isnull().sum().sum())

        # Drop duplicates
        df = df.drop_duplicates()

        # Impute missing
        for col in df.columns:
            if df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
                else:
                    mode_val = df[col].mode()
                    df[col] = df[col].fillna(mode_val[0] if not mode_val.empty else "Unknown")

        save_df(session_id, df)

        return JSONResponse({
            "success": True,
            "rows_before": before_rows,
            "rows_after": len(df),
            "duplicates_removed": before_rows - len(df),
            "missing_before": before_missing,
            "missing_after": int(df.isnull().sum().sum()),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
