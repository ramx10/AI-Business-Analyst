import os
import threading
import time
from datetime import datetime

from utils.scheduler import list_schedules, save_schedule, ReportSchedule
from api.session_store import load_df, session_exists
from agents.supervisor_agent import SupervisorAgent
from reports.report_generator import save_report


def _compute_next_run(frequency: str, from_dt: datetime = None) -> str:
    from datetime import timedelta
    if from_dt is None:
        from_dt = datetime.utcnow()
    if frequency == "daily":
        next_dt = (from_dt + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    elif frequency == "weekly":
        next_dt = (from_dt + timedelta(weeks=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    elif frequency == "monthly":
        next_month = from_dt.replace(day=28) + timedelta(days=4)
        next_dt = next_month.replace(day=1, hour=8, minute=0, second=0, microsecond=0)
    else:
        next_dt = (from_dt + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    return next_dt.isoformat()


def _send_email(schedule: ReportSchedule, report_path: str):
    """Send email notification (SMTP) or log if not configured."""
    import smtplib
    from email.message import EmailMessage

    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")

    if not schedule.email or not smtp_host:
        print(f"[scheduler] No SMTP configured or no recipient. Report saved at: {report_path}")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = f"Scheduled Report: {schedule.name}"
        msg["From"] = smtp_user or "noreply@aianalyst.local"
        msg["To"] = schedule.email
        msg.set_content(f"Your scheduled report '{schedule.name}' is ready.\n\nDownload: {report_path}")

        with open(report_path, "rb") as f:
            report_data = f.read()
            ext = os.path.splitext(report_path)[1] or ".md"
            msg.add_attachment(report_data, maintype="application", subtype="octet-stream",
                               filename=f"report_{schedule.frequency}_{schedule.schedule_id[:8]}{ext}")

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"[scheduler] Email sent to {schedule.email} for schedule '{schedule.name}'")
    except Exception as e:
        print(f"[scheduler] Failed to send email: {e}")


def start_scheduler(app):
    """Start background scheduler thread."""
    def _run():
        while True:
            time.sleep(60)
            now = datetime.utcnow()
            for s in list_schedules():
                if not s.active or not s.next_run:
                    continue
                try:
                    next_dt = datetime.fromisoformat(s.next_run)
                except Exception:
                    continue
                if now < next_dt:
                    continue
                print(f"[scheduler] Running schedule '{s.name}' (id={s.schedule_id})")
                try:
                    if not session_exists(s.session_id):
                        print(f"[scheduler] Session {s.session_id} gone, skipping.")
                        s.active = False
                        save_schedule(s)
                        continue

                    df = load_df(s.session_id)
                    result = SupervisorAgent().run(df)
                    report_text = result.get("report", "")
                    saved_path = save_report(report_text)

                    _send_email(s, saved_path)

                    s.last_run = now.isoformat()
                    s.next_run = _compute_next_run(s.frequency, datetime.utcnow())
                    save_schedule(s)
                except Exception as e:
                    print(f"[scheduler] Error running schedule '{s.name}': {e}")

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    print("[scheduler] Background scheduler daemon started.")
