from dataclasses import dataclass, field
from typing import List, Dict, Any
import json
import os

LINEAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "lineage")
os.makedirs(LINEAGE_DIR, exist_ok=True)


@dataclass
class LineageStep:
    step_id: str
    step_name: str
    category: str
    description: str
    affected_columns: List[str] = field(default_factory=list)
    rows_before: int = 0
    rows_after: int = 0
    columns_before: int = 0
    columns_after: int = 0
    duration_ms: int = 0
    timestamp: str = ""


class LineageTracker:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.steps: List[LineageStep] = []
        self._load()

    def _get_path(self):
        return os.path.join(LINEAGE_DIR, f"{self.session_id}.json")

    def _load(self):
        path = self._get_path()
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                self.steps = [LineageStep(**s) for s in data]

    def _save(self):
        with open(self._get_path(), "w") as f:
            json.dump([s.__dict__ for s in self.steps], f, indent=2, default=str)

    def add_step(self, step: LineageStep):
        self.steps.append(step)
        self._save()

    def get_steps(self) -> List[LineageStep]:
        return list(self.steps)

    def clear(self):
        self.steps = []
        self._save()
