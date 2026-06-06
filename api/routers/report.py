import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from api.session_store import load_df, session_exists
from agents.supervisor_agent import SupervisorAgent
from reports.report_generator import save_report

router = APIRouter()


@router.get("/report")
async def get_report(session_id: str = Query(...)):
    """Run the full supervisor pipeline and return the executive report."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        result = SupervisorAgent().run(df)
        report_text = result["report"]

        if report_text.startswith("Error:") or "Limit Exceeded" in report_text:
            raise HTTPException(status_code=503, detail=report_text)

        saved_path = save_report(report_text)

        return JSONResponse({
            "report": report_text,
            "saved_path": saved_path,
            "kpis": result.get("kpi_info", {}),
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
