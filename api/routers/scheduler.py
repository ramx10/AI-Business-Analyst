import uuid
from datetime import datetime

import pandas as pd

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from utils.scheduler import (
    ReportSchedule, save_schedule, load_schedule,
    list_schedules, delete_schedule, compute_next_run,
    get_due_schedules,
)
from utils.alerts import (
    AlertRule, save_alert, load_alert,
    list_alerts, delete_alert,
)
from api.session_store import load_df, session_exists

router = APIRouter()


@router.post("/schedule/create")
async def api_create_schedule(data: dict):
    session_id = data.get("session_id")
    if not session_id or not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    schedule_id = str(uuid.uuid4())
    name = data.get("name", "Untitled Schedule")
    frequency = data.get("frequency", "daily")
    email = data.get("email") or None
    fmt = data.get("format", "pdf")

    now = datetime.utcnow()
    next_run = compute_next_run(frequency, now).isoformat()

    schedule = ReportSchedule(
        schedule_id=schedule_id,
        session_id=session_id,
        name=name,
        frequency=frequency,
        email=email,
        format=fmt,
        active=True,
        last_run=None,
        next_run=next_run,
    )
    save_schedule(schedule)
    return JSONResponse(schedule.__dict__)


@router.get("/schedule/list")
async def api_list_schedules(session_id: str = Query(None)):
    schedules = list_schedules(session_id)
    return JSONResponse({"schedules": [s.__dict__ for s in schedules]})


@router.delete("/schedule/{schedule_id}")
async def api_delete_schedule(schedule_id: str):
    s = load_schedule(schedule_id)
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found.")
    delete_schedule(schedule_id)
    return JSONResponse({"success": True})


@router.post("/schedule/{schedule_id}/toggle")
async def api_toggle_schedule(schedule_id: str):
    s = load_schedule(schedule_id)
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found.")
    s.active = not s.active
    if s.active:
        now = datetime.utcnow()
        s.next_run = compute_next_run(s.frequency, now).isoformat()
    else:
        s.next_run = None
    save_schedule(s)
    return JSONResponse(s.__dict__)


@router.get("/schedule/check")
async def api_check_schedules():
    due = get_due_schedules()
    return JSONResponse({"due_schedules": [s.__dict__ for s in due]})


@router.post("/alerts/create")
async def api_create_alert(data: dict):
    session_id = data.get("session_id")
    if not session_id or not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    rule_id = str(uuid.uuid4())
    name = data.get("name", "Untitled Alert")
    metric = data.get("metric", "revenue_drop")
    condition = data.get("condition", "below")
    threshold = float(data.get("threshold", 0))
    email = data.get("email") or None

    rule = AlertRule(
        rule_id=rule_id,
        session_id=session_id,
        name=name,
        metric=metric,
        condition=condition,
        threshold=threshold,
        email=email,
        active=True,
    )
    save_alert(rule)
    return JSONResponse(rule.__dict__)


@router.get("/alerts/list")
async def api_list_alerts(session_id: str = Query(None)):
    rules = list_alerts(session_id)
    return JSONResponse({"alerts": [r.__dict__ for r in rules]})


@router.delete("/alerts/{rule_id}")
async def api_delete_alert(rule_id: str):
    r = load_alert(rule_id)
    if not r:
        raise HTTPException(status_code=404, detail="Alert rule not found.")
    delete_alert(rule_id)
    return JSONResponse({"success": True})


@router.get("/alerts/check")
async def api_check_alerts(session_id: str = Query(...)):
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    df = load_df(session_id)
    rules = list_alerts(session_id)
    triggered = []
    for rule in rules:
        if not rule.active:
            continue
        if _evaluate_rule(rule, df):
            triggered.append(rule.__dict__)
    return JSONResponse({"triggered": triggered})


def _evaluate_rule(rule: AlertRule, df) -> bool:
    try:
        total_revenue = 0
        total_profit = 0
        rev_col = _find_col(df, ["revenue", "sales", "amount", "price"])
        prof_col = _find_col(df, ["profit", "margin", "gain"])

        if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
            total_revenue = float(df[rev_col].sum())
        if prof_col and pd.api.types.is_numeric_dtype(df[prof_col]):
            total_profit = float(df[prof_col].sum())

        missing_pct = float(df.isnull().sum().sum() / max(len(df), 1) * 100)
        duplicate_pct = float(df.duplicated().sum() / max(len(df), 1) * 100)

        if rule.metric == "revenue_drop":
            val = total_revenue
            threshold_val = total_revenue * (1 - rule.threshold / 100) if rule.condition == "below" else total_revenue * (1 + rule.threshold / 100)
            return rule.condition == "below" and total_revenue < threshold_val
        elif rule.metric == "profit_drop":
            return rule.condition == "below" and total_profit < rule.threshold
        elif rule.metric == "missing_data":
            if rule.condition == "above":
                return missing_pct > rule.threshold
            return missing_pct < rule.threshold
        elif rule.metric == "duplicate_spike":
            if rule.condition == "above":
                return duplicate_pct > rule.threshold
            return duplicate_pct < rule.threshold
    except Exception:
        pass
    return False


def _find_col(df, keywords):
    for k in keywords:
        for col in df.columns:
            if k in col.lower():
                return col
    return None
