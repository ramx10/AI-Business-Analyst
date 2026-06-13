import os
import json
import time
import uuid

from utils.scheduler import (
    ReportSchedule, save_schedule, load_schedule,
    list_schedules, delete_schedule, SCHEDULE_DIR,
)
from utils.alerts import (
    AlertRule, save_alert, load_alert,
    list_alerts, delete_alert, ALERT_DIR,
)


class TestReportSchedule:
    def test_create_and_load(self):
        s = ReportSchedule(
            schedule_id="test-sched-1",
            session_id="session-1",
            name="Daily Report",
            frequency="daily",
            email="test@example.com",
            format="pdf",
            active=True,
            last_run=None,
            next_run="2026-06-10T08:00:00",
        )
        save_schedule(s)
        loaded = load_schedule("test-sched-1")
        assert loaded is not None
        assert loaded.name == "Daily Report"
        assert loaded.frequency == "daily"
        assert loaded.email == "test@example.com"
        assert loaded.format == "pdf"
        assert loaded.active is True
        assert loaded.next_run == "2026-06-10T08:00:00"
        delete_schedule("test-sched-1")

    def test_load_nonexistent(self):
        assert load_schedule("nonexistent-id") is None

    def test_list_by_session(self):
        save_schedule(ReportSchedule(schedule_id="ls-1", session_id="sess-a", name="A", frequency="daily"))
        save_schedule(ReportSchedule(schedule_id="ls-2", session_id="sess-a", name="B", frequency="weekly"))
        save_schedule(ReportSchedule(schedule_id="ls-3", session_id="sess-b", name="C", frequency="monthly"))

        sess_a = list_schedules("sess-a")
        assert len(sess_a) == 2
        assert all(s.session_id == "sess-a" for s in sess_a)

        all_s = list_schedules()
        assert len(all_s) >= 3

        for sid in ["ls-1", "ls-2", "ls-3"]:
            delete_schedule(sid)

    def test_delete(self):
        save_schedule(ReportSchedule(schedule_id="del-sched", session_id="sess-x", name="X", frequency="daily"))
        path = os.path.join(SCHEDULE_DIR, "del-sched.json")
        assert os.path.exists(path)
        delete_schedule("del-sched")
        assert not os.path.exists(path)

    def test_default_values(self):
        s = ReportSchedule(schedule_id="defaults-test", session_id="sess-d", name="Default", frequency="weekly")
        assert s.active is True
        assert s.last_run is None
        assert s.next_run is None
        assert s.email is None
        assert s.format == "pdf"
        delete_schedule("defaults-test")


class TestAlertRule:
    def test_create_and_load(self):
        r = AlertRule(
            rule_id="alert-1",
            session_id="session-1",
            name="Revenue Drop Alert",
            metric="revenue_drop",
            condition="below",
            threshold=15.0,
            email="alert@example.com",
            active=True,
        )
        save_alert(r)
        loaded = load_alert("alert-1")
        assert loaded is not None
        assert loaded.name == "Revenue Drop Alert"
        assert loaded.metric == "revenue_drop"
        assert loaded.condition == "below"
        assert loaded.threshold == 15.0
        assert loaded.email == "alert@example.com"
        assert loaded.active is True
        delete_alert("alert-1")

    def test_load_nonexistent(self):
        assert load_alert("nonexistent-alert") is None

    def test_list_by_session(self):
        save_alert(AlertRule(rule_id="al-1", session_id="sess-a", name="A", metric="revenue_drop", condition="above", threshold=5))
        save_alert(AlertRule(rule_id="al-2", session_id="sess-a", name="B", metric="profit_drop", condition="below", threshold=10))
        save_alert(AlertRule(rule_id="al-3", session_id="sess-b", name="C", metric="missing_data", condition="above", threshold=20))

        sess_a = list_alerts("sess-a")
        assert len(sess_a) == 2
        assert all(r.session_id == "sess-a" for r in sess_a)

        for rid in ["al-1", "al-2", "al-3"]:
            delete_alert(rid)

    def test_delete(self):
        save_alert(AlertRule(rule_id="del-alert", session_id="sess-y", name="Y", metric="duplicate_spike", condition="above", threshold=5))
        path = os.path.join(ALERT_DIR, "del-alert.json")
        assert os.path.exists(path)
        delete_alert("del-alert")
        assert not os.path.exists(path)


class TestScheduleCheck:
    def test_compute_next_run(self):
        from utils.scheduler import compute_next_run
        from datetime import datetime

        base = datetime(2026, 6, 9, 12, 0, 0)
        daily = compute_next_run("daily", base)
        assert daily > base
        assert daily.hour == 8
        assert daily.minute == 0

        weekly = compute_next_run("weekly", base)
        assert weekly > base
        assert weekly.hour == 8

        monthly = compute_next_run("monthly", base)
        assert monthly > base
        assert monthly.hour == 8

    def test_check_returns_due_schedules(self):
        save_schedule(ReportSchedule(
            schedule_id="due-test",
            session_id="sess-due",
            name="Due Now",
            frequency="daily",
            active=True,
            next_run="2020-01-01T00:00:00",
        ))
        save_schedule(ReportSchedule(
            schedule_id="not-due-test",
            session_id="sess-due",
            name="Not Due",
            frequency="daily",
            active=True,
            next_run="2099-01-01T00:00:00",
        ))
        save_schedule(ReportSchedule(
            schedule_id="inactive-test",
            session_id="sess-due",
            name="Inactive",
            frequency="daily",
            active=False,
            next_run="2020-01-01T00:00:00",
        ))

        from utils.scheduler import get_due_schedules
        due = get_due_schedules()
        ids = [s.schedule_id for s in due]
        assert "due-test" in ids
        assert "not-due-test" not in ids
        assert "inactive-test" not in ids

        for sid in ["due-test", "not-due-test", "inactive-test"]:
            delete_schedule(sid)
