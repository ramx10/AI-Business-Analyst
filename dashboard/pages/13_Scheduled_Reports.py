import sys
import os
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from dashboard.styles import apply_page_styling
from utils.scheduler import ReportSchedule, save_schedule, list_schedules, delete_schedule, load_schedule
from utils.alerts import AlertRule, save_alert, list_alerts, delete_alert

apply_page_styling()

st.title("◉ Scheduled Reports & Alerts")

st.markdown("""
<div style="font-size: 16px; color: #94a3b8; margin-bottom: 25px;">
Automate executive report generation and configure business alert rules.
</div>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.warning("No active session. Please upload a dataset first.")
    st.stop()

session_id = st.session_state["session_id"]

tab1, tab2 = st.tabs(["◈ Scheduled Reports", "◉ Alert Rules"])

# ─── Tab 1: Scheduled Reports ──────────────────────────────────

with tab1:
    st.markdown("### Create Schedule")
    with st.form("schedule-form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            sched_name = st.text_input("Name", value="Weekly Executive Report")
        with col2:
            sched_freq = st.selectbox("Frequency", ["daily", "weekly", "monthly"], index=1)
        with col3:
            sched_email = st.text_input("Email (optional)")
        with col4:
            sched_format = st.selectbox("Format", ["pdf", "html", "md"], index=0)
        submitted = st.form_submit_button("Create Schedule", use_container_width=True, type="primary")
        if submitted:
            schedule_id = str(uuid.uuid4())
            now = datetime.utcnow()
            if sched_freq == "daily":
                next_run = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
            elif sched_freq == "weekly":
                next_run = (now + timedelta(weeks=1)).replace(hour=8, minute=0, second=0, microsecond=0)
            else:
                next_month = now.replace(day=28) + timedelta(days=4)
                next_run = next_month.replace(day=1, hour=8, minute=0, second=0, microsecond=0)
            s = ReportSchedule(
                schedule_id=schedule_id,
                session_id=session_id,
                name=sched_name,
                frequency=sched_freq,
                email=sched_email or None,
                format=sched_format,
                active=True,
                last_run=None,
                next_run=next_run.isoformat(),
            )
            save_schedule(s)
            st.success(f"Schedule '{sched_name}' created!")

    st.markdown("### Schedules")
    schedules = list_schedules(session_id)
    if schedules:
        for s in schedules:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                status = "◉ Active" if s.active else "◉ Disabled"
                next_str = datetime.fromisoformat(s.next_run).strftime("%Y-%m-%d %H:%M") if s.next_run else "—"
                last_str = datetime.fromisoformat(s.last_run).strftime("%Y-%m-%d %H:%M") if s.last_run else "Never"
                st.markdown(f"**{s.name}** — {s.frequency} / {s.format}")
                st.caption(f"{status} | Next: {next_str} | Last: {last_str}" + (f" | ✦ {s.email}" if s.email else ""))
            with col2:
                if st.button("Toggle", key=f"st_{s.schedule_id}"):
                    s.active = not s.active
                    if s.active:
                        now = datetime.utcnow()
                        if s.frequency == "daily":
                            s.next_run = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0).isoformat()
                        elif s.frequency == "weekly":
                            s.next_run = (now + timedelta(weeks=1)).replace(hour=8, minute=0, second=0, microsecond=0).isoformat()
                        else:
                            next_month = now.replace(day=28) + timedelta(days=4)
                            s.next_run = next_month.replace(day=1, hour=8, minute=0, second=0, microsecond=0).isoformat()
                    else:
                        s.next_run = None
                    save_schedule(s)
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"sd_{s.schedule_id}"):
                    delete_schedule(s.schedule_id)
                    st.rerun()
    else:
        st.info("No schedules yet.")

# ─── Tab 2: Alert Rules ────────────────────────────────────────

with tab2:
    st.markdown("### Create Alert Rule")
    with st.form("alert-form", clear_on_submit=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            alert_name = st.text_input("Name", value="Revenue Drop Alert")
        with col2:
            alert_metric = st.selectbox("Metric", ["revenue_drop", "profit_drop", "missing_data", "duplicate_spike"], index=0)
        with col3:
            alert_condition = st.selectbox("Condition", ["above", "below"], index=1)
        with col4:
            alert_threshold = st.number_input("Threshold (%)", value=10.0, step=0.5)
        with col5:
            alert_email = st.text_input("Email (optional)")
        alert_submitted = st.form_submit_button("Create Alert Rule", use_container_width=True, type="primary")
        if alert_submitted:
            rule = AlertRule(
                rule_id=str(uuid.uuid4()),
                session_id=session_id,
                name=alert_name,
                metric=alert_metric,
                condition=alert_condition,
                threshold=alert_threshold,
                email=alert_email or None,
                active=True,
            )
            save_alert(rule)
            st.success(f"Alert rule '{alert_name}' created!")

    st.markdown("### Alert Rules")
    rules = list_alerts(session_id)
    if rules:
        for r in rules:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                icons = {"revenue_drop": "✦", "profit_drop": "↓", "missing_data": "◉", "duplicate_spike": "↻"}
                icon = icons.get(r.metric, "◉")
                status = "◉ On" if r.active else "◉ Off"
                st.markdown(f"{icon} **{r.name}**")
                st.caption(f"{status} | {r.metric} {r.condition} {r.threshold}%" + (f" | ✦ {r.email}" if r.email else ""))
            with col2:
                if st.button("Toggle", key=f"at_{r.rule_id}"):
                    r.active = not r.active
                    save_alert(r)
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"ad_{r.rule_id}"):
                    delete_alert(r.rule_id)
                    st.rerun()
    else:
        st.info("No alert rules yet.")
