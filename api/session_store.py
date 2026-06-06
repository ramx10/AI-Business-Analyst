"""
Session store: saves each uploaded DataFrame as a parquet file keyed by a UUID session_id.
This replaces Streamlit's st.session_state for the new FastAPI architecture.
"""
import os
import uuid
import pandas as pd

SESSION_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)


def new_session_id() -> str:
    return str(uuid.uuid4())


def save_df(session_id: str, df: pd.DataFrame):
    path = os.path.join(SESSION_DIR, f"{session_id}.parquet")
    df.to_parquet(path, index=False)


def load_df(session_id: str) -> pd.DataFrame:
    path = os.path.join(SESSION_DIR, f"{session_id}.parquet")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No session found for id: {session_id}")
    return pd.read_parquet(path)


def session_exists(session_id: str) -> bool:
    path = os.path.join(SESSION_DIR, f"{session_id}.parquet")
    return os.path.exists(path)
