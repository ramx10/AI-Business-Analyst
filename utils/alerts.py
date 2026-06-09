import json
import os
from typing import Optional

ALERT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "alerts")
os.makedirs(ALERT_DIR, exist_ok=True)


class AlertRule:
    def __init__(self, rule_id: str, session_id: str, name: str,
                 metric: str, condition: str, threshold: float,
                 email: str = None, active: bool = True):
        self.rule_id = rule_id
        self.session_id = session_id
        self.name = name
        self.metric = metric
        self.condition = condition
        self.threshold = threshold
        self.email = email
        self.active = active


def save_alert(rule: AlertRule):
    path = os.path.join(ALERT_DIR, f"{rule.rule_id}.json")
    with open(path, "w") as f:
        json.dump(rule.__dict__, f, indent=2, default=str)


def load_alert(rule_id: str) -> Optional[AlertRule]:
    path = os.path.join(ALERT_DIR, f"{rule_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return AlertRule(**json.load(f))


def list_alerts(session_id: str = None) -> list[AlertRule]:
    rules = []
    for fname in os.listdir(ALERT_DIR):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(ALERT_DIR, fname)) as f:
            r = AlertRule(**json.load(f))
            if not session_id or r.session_id == session_id:
                rules.append(r)
    return rules


def delete_alert(rule_id: str):
    path = os.path.join(ALERT_DIR, f"{rule_id}.json")
    if os.path.exists(path):
        os.remove(path)
