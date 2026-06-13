from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from utils.sharing import create_share_link, get_shared_session, list_shares, revoke_share, get_share_meta
from api.session_store import session_exists
from api.routers.dashboard import get_dashboard_data

router = APIRouter()


@router.post("/share/create")
async def api_create_share(data: dict):
    session_id = data.get("session_id")
    if not session_id or not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    expiry_hours = data.get("expiry_hours", 24)
    password = data.get("password") or None
    result = create_share_link(session_id, expiry_hours=expiry_hours, password=password)
    return JSONResponse(result)


@router.get("/share/{token}")
async def api_get_shared(token: str):
    meta = get_share_meta(token)
    if not meta:
        raise HTTPException(status_code=404, detail="Share link not found.")
    expiry = meta["expiry"]
    from datetime import datetime
    if datetime.utcnow() > datetime.fromisoformat(expiry):
        raise HTTPException(status_code=410, detail="Share link has expired.")
    if meta.get("password"):
        return JSONResponse({"requires_password": True, "token": token})
    session_id = get_shared_session(token)
    if not session_id:
        raise HTTPException(status_code=410, detail="Share link is invalid or expired.")
    dash_data = await get_dashboard_data(session_id)
    return JSONResponse({"session_id": session_id, "dashboard": dash_data})


@router.post("/share/verify/{token}")
async def api_verify_shared(token: str, data: dict):
    password = data.get("password", "")
    session_id = get_shared_session(token, password=password)
    if not session_id:
        raise HTTPException(status_code=403, detail="Invalid password or expired share link.")
    dash_data = await get_dashboard_data(session_id)
    return JSONResponse({"session_id": session_id, "dashboard": dash_data})


@router.get("/share/list")
async def api_list_shares(session_id: str = Query(...)):
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    shares = list_shares(session_id)
    return JSONResponse({"shares": shares})


@router.delete("/share/{token}")
async def api_revoke_share(token: str):
    revoke_share(token)
    return JSONResponse({"success": True})
