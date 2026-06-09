import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import io
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from api.session_store import new_session_id, save_df
from utils.sample_data import generate_sample_sales_df
from utils.helper import read_excel, read_json, read_parquet
from utils.large_dataset import estimate_memory
from utils.lineage import LineageTracker, LineageStep
from datetime import datetime

router = APIRouter()

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json", ".parquet"}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Accept a file upload (CSV, Excel, JSON, Parquet), save to session, return session_id."""
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    try:
        contents = await file.read()
        if ext == ".csv":
            df = pd.read_csv(io.BytesIO(contents), encoding_errors="replace")
        elif ext == ".xlsx":
            df = read_excel(io.BytesIO(contents))
        elif ext == ".json":
            df = read_json(io.BytesIO(contents))
        elif ext == ".parquet":
            df = read_parquet(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")
        session_id = new_session_id()
        save_df(session_id, df)

        tracker = LineageTracker(session_id)
        tracker.add_step(LineageStep(
            step_id="upload",
            step_name="File Upload",
            category="upload",
            description=f"Uploaded {file.filename} ({ext.lstrip('.')})",
            affected_columns=df.columns.tolist(),
            rows_before=0,
            rows_after=len(df),
            columns_before=0,
            columns_after=len(df.columns),
            duration_ms=0,
            timestamp=datetime.now().isoformat(),
        ))

        return JSONResponse({
            "session_id": session_id,
            "filename": file.filename,
            "format": ext.lstrip("."),
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "memory_mb": round(estimate_memory(df), 2),
            "preview": df.head(5).fillna("").astype(str).to_dict(orient="records"),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/sample")
async def load_sample():
    """Generate and return a sample retail sales dataset."""
    try:
        df = generate_sample_sales_df()
        session_id = new_session_id()
        save_df(session_id, df)

        tracker = LineageTracker(session_id)
        tracker.add_step(LineageStep(
            step_id="upload",
            step_name="Sample Data Load",
            category="upload",
            description="Loaded sample retail sales dataset",
            affected_columns=df.columns.tolist(),
            rows_before=0,
            rows_after=len(df),
            columns_before=0,
            columns_after=len(df.columns),
            duration_ms=0,
            timestamp=datetime.now().isoformat(),
        ))

        return JSONResponse({
            "session_id": session_id,
            "filename": "sample_retail_sales.csv",
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "memory_mb": round(estimate_memory(df), 2),
            "preview": df.head(5).fillna("").astype(str).to_dict(orient="records"),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
