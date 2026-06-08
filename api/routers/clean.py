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
    """Return comprehensive data quality metrics without modifying the dataset."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        report = agent.analyze_data_quality(df)
        return JSONResponse(report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clean/apply")
async def clean_apply(session_id: str = Query(...)):
    """Run the full 15-step auto-cleaning pipeline and save the cleaned dataset."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        before_rows = len(df)
        before_cols = len(df.columns)
        before_missing = int(df.isnull().sum().sum())

        cleaned_df, change_log = agent.full_clean(df)

        save_df(session_id, cleaned_df)

        return JSONResponse({
            "success": True,
            "rows_before": before_rows,
            "rows_after": len(cleaned_df),
            "cols_before": before_cols,
            "cols_after": len(cleaned_df.columns),
            "missing_before": before_missing,
            "missing_after": int(cleaned_df.isnull().sum().sum()),
            "change_log": change_log,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clean/ml-prep")
async def clean_ml_prep(session_id: str = Query(...)):
    """Apply ML preparation steps (encode categoricals + scale numericals)."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        prepared_df, change_log = agent.ml_prep(df)
        save_df(session_id, prepared_df)

        return JSONResponse({
            "success": True,
            "change_log": change_log,
            "columns": len(prepared_df.columns),
            "rows": len(prepared_df),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
