import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.pii_agent import PIIAgent


class TestPIIAgent:
    def setup_method(self):
        self.agent = PIIAgent()

    # ── detect_pii ──────────────────────────────────────────────

    def test_detect_pii_finds_emails(self):
        df = pd.DataFrame({
            "email": ["user@example.com", "test@domain.org", "nobody@nowhere.net"],
            "other": ["a", "b", "c"],
        })
        findings = self.agent.detect_pii(df)
        email_findings = [f for f in findings if f["type"] == "email"]
        assert len(email_findings) >= 1
        assert email_findings[0]["column"] == "email"

    def test_detect_pii_finds_phones(self):
        df = pd.DataFrame({
            "phone": ["+1-555-123-4567", "555-987-6543", "(555) 123-4567"],
        })
        findings = self.agent.detect_pii(df)
        phone_findings = [f for f in findings if f["type"] == "phone"]
        assert len(phone_findings) >= 1

    def test_detect_pii_finds_ssns(self):
        df = pd.DataFrame({
            "ssn": ["123-45-6789", "987-65-4321"],
        })
        findings = self.agent.detect_pii(df)
        ssn_findings = [f for f in findings if f["type"] == "ssn"]
        assert len(ssn_findings) >= 1

    def test_detect_pii_finds_credit_cards(self):
        df = pd.DataFrame({
            "card": ["4111-1111-1111-1111", "5500 0000 0000 0004"],
        })
        findings = self.agent.detect_pii(df)
        cc_findings = [f for f in findings if f["type"] == "credit_card"]
        assert len(cc_findings) >= 1

    def test_detect_pii_finds_ip_addresses(self):
        df = pd.DataFrame({
            "ip": ["192.168.1.1", "10.0.0.1", "8.8.8.8"],
        })
        findings = self.agent.detect_pii(df)
        ip_findings = [f for f in findings if f["type"] == "ip_address"]
        assert len(ip_findings) >= 1

    def test_detect_pii_returns_empty_for_clean_data(self):
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "value": [10.5, 20.3, 30.1],
            "label": ["foo", "bar", "baz"],
        })
        findings = self.agent.detect_pii(df)
        assert findings == []

    def test_detect_pii_detects_by_column_name(self):
        df = pd.DataFrame({
            "email_address": ["a@b.com", "c@d.org"],
            "customer_phone": ["555-1234", "555-5678"],
        })
        findings = self.agent.detect_pii(df)
        types = {f["column"]: f["type"] for f in findings}
        assert types.get("email_address") == "email"
        assert types.get("customer_phone") == "phone"

    # ── mask_pii ────────────────────────────────────────────────

    def test_mask_pii_masks_email_correctly(self):
        df = pd.DataFrame({"email": ["user@example.com", "test@domain.org"]})
        masked, log = self.agent.mask_pii(df)
        val = masked["email"].iloc[0]
        assert val.endswith("@example.com")
        assert val != "user@example.com"
        assert "***" in val

    def test_mask_pii_masks_phone_correctly(self):
        df = pd.DataFrame({"phone": ["+1-555-123-4567"]})
        masked, log = self.agent.mask_pii(df)
        val = masked["phone"].iloc[0]
        assert val.endswith("-4567")

    def test_mask_pii_masks_ssn_correctly(self):
        df = pd.DataFrame({"ssn": ["123-45-6789"]})
        masked, log = self.agent.mask_pii(df)
        val = masked["ssn"].iloc[0]
        assert val.endswith("-6789")
        assert val.startswith("***")

    def test_mask_pii_masks_credit_card_correctly(self):
        df = pd.DataFrame({"card": ["4111-1111-1111-1111"]})
        masked, log = self.agent.mask_pii(df)
        val = masked["card"].iloc[0]
        assert val.endswith("-1111")
        assert val.startswith("****")

    def test_mask_pii_with_specific_columns(self):
        df = pd.DataFrame({
            "email": ["a@b.com"],
            "phone": ["555-1234"],
        })
        masked, log = self.agent.mask_pii(df, columns_to_mask=["email"])
        assert "***" in masked["email"].iloc[0]
        assert masked["phone"].iloc[0] == "555-1234"

    def test_mask_pii_does_not_mutate_input(self):
        df = pd.DataFrame({"email": ["user@example.com"]})
        original = df.copy()
        self.agent.mask_pii(df)
        pd.testing.assert_frame_equal(df, original)

    # ── Risk Levels ─────────────────────────────────────────────

    def test_risk_levels(self):
        df = pd.DataFrame({
            "email": ["a@b.com"],
            "phone": ["555-1234"],
            "ssn": ["123-45-6789"],
            "cc": ["4111-1111-1111-1111"],
            "ip": ["192.168.1.1"],
        })
        findings = self.agent.detect_pii(df)
        risk_map = {f["column"]: f["risk"] for f in findings}
        assert risk_map.get("email") == "high"
        assert risk_map.get("phone") == "high"
        assert risk_map.get("ssn") == "critical"
        assert risk_map.get("cc") == "critical"
        assert risk_map.get("ip") == "medium"
