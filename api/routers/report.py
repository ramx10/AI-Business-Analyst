import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, Response

from api.session_store import load_df, session_exists
from agents.supervisor_agent import SupervisorAgent
from reports.report_generator import save_report, generate_pdf

router = APIRouter()


@router.get("/report")
async def get_report(
    session_id: str = Query(...),
    mode: str = Query("detailed", pattern="^(summary|detailed)$")
):
    """Run the full supervisor pipeline and return the executive report.
    
    - mode=summary : concise bullet-point executive summary
    - mode=detailed: comprehensive bullet-point analysis report
    """
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)
        result = SupervisorAgent().run(df, mode=mode)
        report_text = result["report"]

        if report_text.startswith("Error:") or "Limit Exceeded" in report_text:
            raise HTTPException(status_code=503, detail=report_text)

        saved_path = save_report(report_text, mode=mode)

        return JSONResponse({
            "report": report_text,
            "saved_path": saved_path,
            "kpis": result.get("kpi_info", {}),
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report/export/pdf")
async def export_report_pdf(data: dict):
    """Convert report markdown text to PDF and return the file."""
    report_text = data.get("report_text", "")
    mode = data.get("mode", "detailed")
    if not report_text.strip():
        raise HTTPException(status_code=400, detail="report_text is required.")
    try:
        pdf_bytes = generate_pdf(report_text, mode=mode)
        filename = f"{mode}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
