import os

import pandas as pd
import io
import pandas as pd
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse

from api.session_store import load_df, session_exists, SESSION_DIR, save_df, new_session_id
from agents.compare_agent import CompareAgent
from utils.session_history import get_recent, record_upload, load_parquet, parquet_exists, HISTORY_DIR

router = APIRouter()


def _build_stats(df: pd.DataFrame, label: str) -> dict:
    """Compute a rich stats dictionary for a DataFrame."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()

    numeric_summary = {}
    for col in numeric_cols:
        s = df[col].describe().round(2).fillna(0)
        numeric_summary[col] = {
            "count": int(s["count"]),
            "mean": round(float(s["mean"]), 2),
            "std": round(float(s["std"]), 2),
            "min": round(float(s["min"]), 2),
            "q1": round(float(s.get("25%", 0)), 2),
            "median": round(float(s.get("50%", 0)), 2),
            "q3": round(float(s.get("75%", 0)), 2),
            "max": round(float(s["max"]), 2),
            "sum": round(float(s["sum"]), 2) if "sum" in s else round(float(df[col].sum()), 2),
        }

    cat_summary = {}
    for col in cat_cols:
        top_vals = df[col].value_counts().head(5).to_dict()
        cat_summary[col] = {str(k): int(v) for k, v in top_vals.items()}

    column_info = {}
    for col in df.columns:
        column_info[col] = "numeric" if col in numeric_cols else "categorical"

    missing_values = {col: int(df[col].isnull().sum()) for col in df.columns}

    return {
        "label": label,
        "row_count": len(df),
        "column_count": len(df.columns),
        "column_info": column_info,
        "numeric_summary": numeric_summary,
        "cat_summary": cat_summary,
        "missing_values": missing_values,
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": df.columns.tolist(),
        "preview": df.head(10).fillna("").astype(str).to_dict(orient="records"),
    }


@router.get("/compare/history")
async def list_history():
    """Return the last N historical uploads available for comparison."""
    try:
        entries = get_recent()
        return JSONResponse({"history": entries})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read history: {e}")


@router.post("/compare/upload")
async def upload_to_history(file: UploadFile = File(...)):
    """Upload a CSV file directly into the history index without affecting the current session."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty.")
        session_id = new_session_id()
        # Save CSV as a new session first (so it gets a parquet copy)
        save_df(session_id, df)
        source = os.path.join(SESSION_DIR, f"{session_id}.parquet")
        record_upload(session_id, file.filename, len(df), len(df.columns), source)
        return JSONResponse({
            "success": True,
            "session_id": session_id,
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare/snapshot")
async def save_snapshot(data: dict):
    """Save the current session data as a history snapshot for future comparison."""
    session_id = data.get("session_id", "")
    filename = data.get("filename", "snapshot")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        source_path = os.path.join(SESSION_DIR, f"{session_id}.parquet")
        record_upload(session_id, filename, len(df), len(df.columns), source_path)
        return JSONResponse({"success": True, "message": "Snapshot saved."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare")
async def compare_datasets(
    session_id: str = Query(...),
    previous_id: str = Query(...),
):
    """Compare the current session dataset against a historical upload."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Current session not found.")

    if not parquet_exists(previous_id):
        # Fall back to session dir (in case history copy doesn't exist yet)
        if session_exists(previous_id):
            df_previous = load_df(previous_id)
        else:
            raise HTTPException(status_code=404, detail="Previous dataset not found in history.")
    else:
        try:
            df_previous = load_parquet(previous_id)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Previous dataset not found in history.")

    try:
        df_current = load_df(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load current dataset: {e}")

    if df_current.empty:
        raise HTTPException(status_code=400, detail="Current dataset is empty.")
    if df_previous.empty:
        raise HTTPException(status_code=400, detail="Previous dataset is empty.")

    stats_current = _build_stats(df_current, "Current")
    stats_previous = _build_stats(df_previous, "Previous")

    agent = CompareAgent()
    insights = agent.generate_comparison_insights(stats_current, stats_previous)

    return JSONResponse({
        "current": stats_current,
        "previous": stats_previous,
        "insights": insights,
    })
