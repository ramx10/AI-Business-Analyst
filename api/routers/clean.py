import sys
import os
import threading
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from typing import Optional
import pandas as pd
from fastapi import APIRouter, HTTPException, Query, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.session_store import load_df, save_df, session_exists
from api.java_client import record_history
from agents.cleaning_agent import DataCleaningAgent
from utils.progress import get_progress, set_progress, clear_progress, ProgressTracker
from utils.large_dataset import estimate_memory as estimate_df_memory
from utils.lineage import LineageTracker


class SelectiveCleanRequest(BaseModel):
    steps: list[int]
    preview: Optional[bool] = False

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
async def clean_apply(
    session_id: str = Query(...),
    dataset_name: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None),
    x_user_email: Optional[str] = Header(None),
):
    """Run the full 15-step auto-cleaning pipeline and save the cleaned dataset."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        before_rows = len(df)
        before_cols = len(df.columns)
        before_missing = int(df.isnull().sum().sum())

        lineage_tracker = LineageTracker(session_id)
        cleaned_df, change_log = agent.full_clean(df, lineage_tracker=lineage_tracker)

        save_df(session_id, cleaned_df)

        email = user_email or x_user_email
        if email:
            summary = (
                f"Auto-cleaned {before_rows} rows \u2192 {len(cleaned_df)} rows; "
                f"missing values {before_missing} \u2192 {int(cleaned_df.isnull().sum().sum())}"
            )
            await record_history(
                user_email=email,
                dataset_name=dataset_name or session_id,
                row_count=len(cleaned_df),
                cleaning_summary=summary,
                session_id=session_id,
            )

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


@router.post("/clean/selective")
async def clean_selective(
    session_id: str = Query(...),
    body: SelectiveCleanRequest = None,
    dataset_name: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None),
    x_user_email: Optional[str] = Header(None),
):
    """Run a subset of cleaning steps selected by the user."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    if not body or not body.steps:
        raise HTTPException(status_code=400, detail="No steps provided.")
    try:
        df = load_df(session_id)
        before_rows = len(df)
        before_cols = len(df.columns)
        before_missing = int(df.isnull().sum().sum())

        lineage_tracker = LineageTracker(session_id)
        cleaned_df, change_log = agent.selective_clean(df, body.steps, lineage_tracker=lineage_tracker)

        is_preview = body.preview or False
        if not is_preview:
            save_df(session_id, cleaned_df)

        email = user_email or x_user_email
        if email and not is_preview:
            summary = (
                f"Selective clean ({len(body.steps)} steps): "
                f"{before_rows} rows \u2192 {len(cleaned_df)} rows; "
                f"missing values {before_missing} \u2192 {int(cleaned_df.isnull().sum().sum())}"
            )
            await record_history(
                user_email=email,
                dataset_name=dataset_name or session_id,
                row_count=len(cleaned_df),
                cleaning_summary=summary,
                session_id=session_id,
            )

        return JSONResponse({
            "success": True,
            "preview": is_preview,
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


@router.post("/clean/start")
async def clean_start(
    session_id: str = Query(...),
    dataset_name: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None),
    x_user_email: Optional[str] = Header(None),
):
    """Start async cleaning in a background thread. Returns immediately."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")

    existing = get_progress(session_id)
    if existing and existing.current < existing.total:
        raise HTTPException(status_code=409, detail="Cleaning already in progress.")

    clear_progress(session_id)
    thread = threading.Thread(
        target=_run_clean_background,
        args=(session_id, dataset_name, user_email or x_user_email),
        daemon=True,
    )
    thread.start()
    return {"session_id": session_id, "status": "started"}


@router.get("/clean/progress")
async def clean_progress(session_id: str = Query(...)):
    """Return current progress of the background cleaning task."""
    tracker = get_progress(session_id)
    if tracker is None:
        return JSONResponse({"current": 0, "total": 0, "percent": 0, "description": "No task running", "result": None, "error": None})
    return JSONResponse(tracker.get_status())


def _run_clean_background(session_id: str, dataset_name: Optional[str], email: Optional[str]):
    """Run cleaning in a background thread, updating progress along the way."""
    try:
        df = load_df(session_id)
        before_rows = len(df)
        before_cols = len(df.columns)
        before_missing = int(df.isnull().sum().sum())

        lineage_tracker = LineageTracker(session_id)
        cleaned_df, change_log = agent.full_clean_chunked(df, session_id=session_id)

        save_df(session_id, cleaned_df)

        result = {
            "success": True,
            "rows_before": before_rows,
            "rows_after": len(cleaned_df),
            "cols_before": before_cols,
            "cols_after": len(cleaned_df.columns),
            "missing_before": before_missing,
            "missing_after": int(cleaned_df.isnull().sum().sum()),
            "change_log": change_log,
        }

        tracker = get_progress(session_id)
        if tracker:
            tracker.result = result
            tracker.description = "Complete"

        if email:
            import asyncio
            summary = (
                f"Auto-cleaned {before_rows} rows -> {len(cleaned_df)} rows; "
                f"missing values {before_missing} -> {int(cleaned_df.isnull().sum().sum())}"
            )
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    record_history(
                        user_email=email,
                        dataset_name=dataset_name or session_id,
                        row_count=len(cleaned_df),
                        cleaning_summary=summary,
                        session_id=session_id,
                    )
                )
                loop.close()
            except Exception:
                pass

    except Exception as e:
        tracker = get_progress(session_id)
        if tracker:
            tracker.error = str(e)
            tracker.description = f"Error: {str(e)}"


@router.get("/clean/download")
async def clean_download(session_id: str = Query(...)):
    """Download the cleaned dataset as CSV."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        import io
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=cleaned_dataset.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
