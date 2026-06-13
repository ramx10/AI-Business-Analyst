from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from utils.lineage import LineageTracker

router = APIRouter()


@router.get("/lineage")
async def get_lineage(session_id: str = Query(...)):
    try:
        tracker = LineageTracker(session_id)
        steps = tracker.get_steps()
        return JSONResponse({
            "session_id": session_id,
            "steps": [
                {
                    "step_id": s.step_id,
                    "step_name": s.step_name,
                    "category": s.category,
                    "description": s.description,
                    "affected_columns": s.affected_columns,
                    "rows_before": s.rows_before,
                    "rows_after": s.rows_after,
                    "columns_before": s.columns_before,
                    "columns_after": s.columns_after,
                    "duration_ms": s.duration_ms,
                    "timestamp": s.timestamp,
                }
                for s in steps
            ],
            "total_steps": len(steps),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/lineage")
async def clear_lineage(session_id: str = Query(...)):
    try:
        tracker = LineageTracker(session_id)
        tracker.clear()
        return JSONResponse({"success": True, "session_id": session_id, "message": "Lineage cleared"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
