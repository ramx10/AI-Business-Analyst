"""
utils/progress.py — Progress tracking utility for long-running operations.
Provides a ProgressTracker class and a module-level store keyed by session_id.
"""

from typing import Dict, Optional


class ProgressTracker:
    """Tracks progress of a multi-step operation."""

    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total = total_steps
        self.current = 0
        self.description = description
        self.result: Optional[dict] = None
        self.error: Optional[str] = None

    def step(self, n: int = 1, detail: str = ""):
        self.current += n
        if detail:
            self.description = detail

    def get_status(self) -> dict:
        return {
            "current": self.current,
            "total": self.total,
            "percent": round(self.current / self.total * 100, 1) if self.total else 0,
            "description": self.description,
            "result": self.result,
            "error": self.error,
        }


_progress_store: Dict[str, ProgressTracker] = {}


def get_progress(session_id: str) -> Optional[ProgressTracker]:
    return _progress_store.get(session_id)


def set_progress(session_id: str, tracker: Optional[ProgressTracker]):
    _progress_store[session_id] = tracker


def clear_progress(session_id: str):
    _progress_store.pop(session_id, None)
