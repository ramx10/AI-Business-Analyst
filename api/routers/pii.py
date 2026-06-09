import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.session_store import load_df, save_df, session_exists
from agents.pii_agent import PIIAgent
from utils.lineage import LineageTracker


class MaskRequest(BaseModel):
    columns: Optional[list[str]] = None

router = APIRouter()
agent = PIIAgent()


@router.post("/pii/detect")
async def pii_detect(session_id: str = Query(...)):
    """Scan the dataset for PII and return findings."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        findings = agent.detect_pii(df)
        return JSONResponse({"findings": findings, "total_findings": len(findings)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pii/mask")
async def pii_mask(
    session_id: str = Query(...),
    body: MaskRequest = None,
):
    """Mask PII columns and save the masked dataset."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        columns_to_mask = body.columns if body and body.columns else None
        lineage_tracker = LineageTracker(session_id)
        masked_df, change_log = agent.mask_pii(df, columns_to_mask, lineage_tracker=lineage_tracker)
        save_df(session_id, masked_df)

        preview = masked_df.head(10).fillna("").astype(str).to_dict(orient="records")

        return JSONResponse({
            "success": True,
            "columns_masked": len(change_log),
            "change_log": change_log,
            "preview": preview,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
