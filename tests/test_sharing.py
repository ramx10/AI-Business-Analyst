import os
import json
import time

from utils.sharing import create_share_link, get_shared_session, list_shares, revoke_share, SHARE_DIR


class TestCreateShareLink:
    def test_returns_valid_token_and_url(self):
        result = create_share_link("test-session-1", expiry_hours=24)
        assert "token" in result
        assert "expiry" in result
        assert "url" in result
        assert result["url"].startswith("/shared/")
        assert len(result["token"]) > 0

    def test_stores_data_on_disk(self):
        token = create_share_link("test-session-2")["token"]
        path = os.path.join(SHARE_DIR, f"{token}.json")
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert data["session_id"] == "test-session-2"
        os.remove(path)

    def test_token_uniqueness(self):
        t1 = create_share_link("test-session-3")["token"]
        t2 = create_share_link("test-session-3")["token"]
        assert t1 != t2
        os.remove(os.path.join(SHARE_DIR, f"{t1}.json"))
        os.remove(os.path.join(SHARE_DIR, f"{t2}.json"))


class TestGetSharedSession:
    def test_returns_session_id_for_valid_token(self):
        result = create_share_link("test-session-4", expiry_hours=24)
        sid = get_shared_session(result["token"])
        assert sid == "test-session-4"
        revoke_share(result["token"])

    def test_returns_none_for_invalid_token(self):
        sid = get_shared_session("nonexistent-token")
        assert sid is None

    def test_returns_none_for_expired_token(self):
        result = create_share_link("test-session-5", expiry_hours=-1)
        sid = get_shared_session(result["token"])
        assert sid is None
        revoke_share(result["token"])

    def test_checks_password_correctly(self):
        result = create_share_link("test-session-6", password="secret123")
        sid = get_shared_session(result["token"], password="wrong")
        assert sid is None
        sid = get_shared_session(result["token"], password="secret123")
        assert sid == "test-session-6"
        revoke_share(result["token"])


class TestRevokeShare:
    def test_removes_share_file(self):
        result = create_share_link("test-session-7")
        path = os.path.join(SHARE_DIR, f"{result['token']}.json")
        assert os.path.exists(path)
        revoke_share(result["token"])
        assert not os.path.exists(path)

    def test_returns_none_after_revoke(self):
        result = create_share_link("test-session-8")
        revoke_share(result["token"])
        sid = get_shared_session(result["token"])
        assert sid is None


class TestListShares:
    def test_returns_correct_shares(self):
        s1 = create_share_link("test-list-1")["token"]
        s2 = create_share_link("test-list-1")["token"]
        s3 = create_share_link("test-list-2")["token"]

        shares = list_shares("test-list-1")
        tokens = [s["token"] for s in shares]
        assert s1 in tokens
        assert s2 in tokens
        assert s3 not in tokens

        revoke_share(s1)
        revoke_share(s2)
        revoke_share(s3)

    def test_returns_password_status(self):
        result = create_share_link("test-list-3", password="abc")
        shares = list_shares("test-list-3")
        assert shares[0]["has_password"] is True
        revoke_share(result["token"])

    def test_empty_for_unknown_session(self):
        shares = list_shares("nonexistent-session")
        assert shares == []
