import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Optional

SCHEDULE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "schedules")
os.makedirs(SCHEDULE_DIR, exist_ok=True)


class ReportSchedule:
    def __init__(self, schedule_id: str, session_id: str, name: str, frequency: str,
                 email: str = None, format: str = "pdf", active: bool = True,
                 last_run: str = None, next_run: str = None):
        self.schedule_id = schedule_id
        self.session_id = session_id
        self.name = name
        self.frequency = frequency
        self.email = email
        self.format = format
        self.active = active
        self.last_run = last_run
        self.next_run = next_run


def save_schedule(schedule: ReportSchedule):
    path = os.path.join(SCHEDULE_DIR, f"{schedule.schedule_id}.json")
    with open(path, "w") as f:
        json.dump(schedule.__dict__, f, indent=2, default=str)


def load_schedule(schedule_id: str) -> Optional[ReportSchedule]:
    path = os.path.join(SCHEDULE_DIR, f"{schedule_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return ReportSchedule(**json.load(f))


def list_schedules(session_id: str = None) -> list[ReportSchedule]:
    schedules = []
    for fname in os.listdir(SCHEDULE_DIR):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(SCHEDULE_DIR, fname)) as f:
            s = ReportSchedule(**json.load(f))
            if not session_id or s.session_id == session_id:
                schedules.append(s)
    return schedules


def delete_schedule(schedule_id: str):
    path = os.path.join(SCHEDULE_DIR, f"{schedule_id}.json")
    if os.path.exists(path):
        os.remove(path)


def compute_next_run(frequency: str, from_dt: datetime = None) -> datetime:
    if from_dt is None:
        from_dt = datetime.utcnow()
    if frequency == "daily":
        return (from_dt + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    elif frequency == "weekly":
        return (from_dt + timedelta(weeks=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    elif frequency == "monthly":
        next_month = from_dt.replace(day=28) + timedelta(days=4)
        return next_month.replace(day=1, hour=8, minute=0, second=0, microsecond=0)
    return (from_dt + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)


def get_due_schedules() -> list[ReportSchedule]:
    now = datetime.utcnow()
    due = []
    for s in list_schedules():
        if not s.active or not s.next_run:
            continue
        try:
            next_dt = datetime.fromisoformat(s.next_run)
        except Exception:
            continue
        if now >= next_dt:
            due.append(s)
    return due
