"""
Session history tracker — keeps a local JSON index of the last N uploads
with parquet file backups so old data survives cleaning.
"""
import os
import json
import shutil
from datetime import datetime, timezone

import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HISTORY_DIR = os.path.join(BASE_DIR, "data", "history")
HISTORY_INDEX = os.path.join(HISTORY_DIR, "session_history.json")
MAX_HISTORY = 3

os.makedirs(HISTORY_DIR, exist_ok=True)

_SEQUENCE = 0  # monotonic counter for ordering when timestamps collide


def _load_index() -> list:
    if not os.path.exists(HISTORY_INDEX):
        return []
    try:
        with open(HISTORY_INDEX, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_index(entries: list):
    with open(HISTORY_INDEX, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def get_recent() -> list:
    """Return the list of historical upload entries, newest first."""
    entries = _load_index()
    entries.sort(key=lambda e: e.get("sort_key", 0), reverse=True)
    return entries


def record_upload(session_id: str, filename: str, rows: int, columns: int, source_parquet: str):
    """Record an upload in the history index and back up the parquet file.
    
    Keeps only the last MAX_HISTORY entries. Older entries' backup files
    are removed from disk.
    """
    global _SEQUENCE
    _SEQUENCE += 1
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dst = os.path.join(HISTORY_DIR, f"{session_id}.parquet")

    if os.path.exists(source_parquet):
        shutil.copy2(source_parquet, dst)

    entry = {
        "session_id": session_id,
        "filename": filename,
        "rows": rows,
        "columns": columns,
        "uploaded_at": timestamp,
        "sort_key": _SEQUENCE,
    }

    entries = _load_index()
    entries = [e for e in entries if e["session_id"] != session_id]
    entries.append(entry)
    entries.sort(key=lambda e: e.get("sort_key", 0), reverse=True)
    pruned = entries[:MAX_HISTORY]
    removed = entries[MAX_HISTORY:]

    for old in removed:
        old_path = os.path.join(HISTORY_DIR, f"{old['session_id']}.parquet")
        if os.path.exists(old_path):
            os.remove(old_path)

    _save_index(pruned)


def load_parquet(session_id: str) -> pd.DataFrame:
    """Load a historical parquet backup by session_id."""
    path = os.path.join(HISTORY_DIR, f"{session_id}.parquet")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No historical data found for session: {session_id}")
    return pd.read_parquet(path)


def parquet_exists(session_id: str) -> bool:
    return os.path.exists(os.path.join(HISTORY_DIR, f"{session_id}.parquet"))
