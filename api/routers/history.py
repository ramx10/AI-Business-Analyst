from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from api.java_client import get_history, record_history

router = APIRouter()


@router.get("/history")
async def list_history(
    user_email: str = Query(..., description="Email of the user"),
):
    """Return dashboard history entries by proxying to the Java backend."""
    entries = await get_history(user_email)
    return JSONResponse({"history": entries})


@router.post("/history")
async def create_history(
    user_email: str = Query(..., description="Email of the user"),
    dataset_name: str = Query(..., description="Name of the dataset"),
    row_count: int = Query(..., description="Row count after cleaning"),
    cleaning_summary: str = Query("", description="Summary of cleaning actions"),
    session_id: str = Query("", description="Optional session identifier"),
):
    """Record a new dashboard history entry by proxying to the Java backend."""
    ok = await record_history(
        user_email=user_email,
        dataset_name=dataset_name,
        row_count=row_count,
        cleaning_summary=cleaning_summary,
        session_id=session_id,
    )
    if ok:
        return JSONResponse({"success": True, "message": "History recorded."})
    raise HTTPException(
        status_code=502, detail="Failed to record history (Java unavailable)."
    )
