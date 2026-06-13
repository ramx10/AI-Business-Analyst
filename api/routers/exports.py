import os
import tempfile

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

from api.session_store import load_df, session_exists
from utils.exports import (
    export_to_csv,
    export_to_excel,
    export_to_parquet,
    export_to_json,
    export_to_tableau_hyper,
    export_to_powerbi,
    export_to_google_sheets,
    get_export_formats,
)

router = APIRouter()

EXTENSION_MAP = {
    "csv": ".csv",
    "excel": ".xlsx",
    "parquet": ".parquet",
    "json": ".json",
    "tableau_hyper": ".hyper",
    "powerbi": ".parquet",
}

FORMAT_MAP = {
    "csv": export_to_csv,
    "excel": export_to_excel,
    "parquet": export_to_parquet,
    "json": export_to_json,
    "tableau_hyper": export_to_tableau_hyper,
    "powerbi": export_to_powerbi,
}

MIME_MAP = {
    "csv": "text/csv",
    "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "parquet": "application/octet-stream",
    "json": "application/json",
    "tableau_hyper": "application/octet-stream",
    "powerbi": "application/octet-stream",
}


class ExportDataRequest(BaseModel):
    session_id: str
    format: str


class ExportDashboardRequest(BaseModel):
    session_id: str
    format: str


class ExportGoogleSheetsRequest(BaseModel):
    session_id: str
    credentials_json: str
    spreadsheet_id: str
    sheet_name: str = "Export"


@router.get("/export/formats")
async def list_formats():
    return JSONResponse(get_export_formats())


@router.post("/export/data")
async def export_data(req: ExportDataRequest):
    if not session_exists(req.session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    if req.format not in FORMAT_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {req.format}")

    df = load_df(req.session_id)
    ext = EXTENSION_MAP[req.format]
    export_fn = FORMAT_MAP[req.format]
    mime = MIME_MAP[req.format]

    fd, tmp_path = tempfile.mkstemp(suffix=ext)
    os.close(fd)

    try:
        export_fn(df, tmp_path)
        return FileResponse(
            path=tmp_path,
            media_type=mime,
            filename=f"export_{req.session_id[:8]}{ext}",
            headers={"Content-Disposition": f'attachment; filename="export_{req.session_id[:8]}{ext}"'},
        )
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/dashboard")
async def export_dashboard(req: ExportDashboardRequest):
    if not session_exists(req.session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    if req.format not in FORMAT_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {req.format}")

    df = load_df(req.session_id)
    ext = EXTENSION_MAP[req.format]
    export_fn = FORMAT_MAP[req.format]
    mime = MIME_MAP[req.format]

    fd, tmp_path = tempfile.mkstemp(suffix=ext)
    os.close(fd)

    try:
        export_fn(df, tmp_path)
        return FileResponse(
            path=tmp_path,
            media_type=mime,
            filename=f"dashboard_{req.session_id[:8]}{ext}",
            headers={"Content-Disposition": f'attachment; filename="dashboard_{req.session_id[:8]}{ext}"'},
        )
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/google-sheets")
async def export_google_sheets(req: ExportGoogleSheetsRequest):
    if not session_exists(req.session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(req.session_id)
        export_to_google_sheets(df, req.credentials_json, req.spreadsheet_id, req.sheet_name)
        return JSONResponse({"status": "ok", "message": f"Data pushed to sheet '{req.sheet_name}'"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
