import secrets
import json
import os
from datetime import datetime, timedelta

SHARE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "shares")
os.makedirs(SHARE_DIR, exist_ok=True)

def create_share_link(session_id: str, expiry_hours: int = 24, password: str = None) -> dict:
    """Generate a shareable link token. Returns {token, expiry, url}."""
    token = secrets.token_urlsafe(16)
    expiry = (datetime.utcnow() + timedelta(hours=expiry_hours)).isoformat()
    data = {"token": token, "session_id": session_id, "expiry": expiry, "password": password, "created": datetime.utcnow().isoformat()}
    with open(os.path.join(SHARE_DIR, f"{token}.json"), "w") as f:
        json.dump(data, f)
    return {"token": token, "expiry": expiry, "url": f"/shared/{token}"}

def get_shared_session(token: str, password: str = None) -> str | None:
    """Validate a share token and return session_id, or None if invalid/expired."""
    path = os.path.join(SHARE_DIR, f"{token}.json")
    if not os.path.exists(path): return None
    with open(path) as f: data = json.load(f)
    if data.get("password") and data["password"] != password: return None
    expiry = datetime.fromisoformat(data["expiry"])
    if datetime.utcnow() > expiry: return None
    return data["session_id"]

def list_shares(session_id: str) -> list[dict]:
    """List all active share links for a session."""
    shares = []
    for fname in os.listdir(SHARE_DIR):
        if not fname.endswith(".json"): continue
        with open(os.path.join(SHARE_DIR, fname)) as f:
            data = json.load(f)
            if data["session_id"] == session_id:
                shares.append({"token": data["token"], "expiry": data["expiry"], "has_password": bool(data.get("password"))})
    return shares

def revoke_share(token: str):
    path = os.path.join(SHARE_DIR, f"{token}.json")
    if os.path.exists(path): os.remove(path)

def get_share_meta(token: str) -> dict | None:
    """Get share metadata without validating password/expiry (for checking if password is needed)."""
    path = os.path.join(SHARE_DIR, f"{token}.json")
    if not os.path.exists(path): return None
    with open(path) as f:
        return json.load(f)
