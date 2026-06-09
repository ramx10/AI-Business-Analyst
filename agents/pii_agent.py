"""
PIIAgent — PII (Personally Identifiable Information) Detection & Masking Agent.
"""

import re
import hashlib
import pandas as pd
from typing import Optional


class PIIAgent:

    # Order matters: check credit_card before phone to avoid false matches
    PATTERNS = {
        "credit_card": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
        "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
        "phone": re.compile(
            r"(?:(?:\+?\d{1,3}[-.\s]?)?"
            r"(?:\(?\d{2,4}\)?[-.\s]?)?"
            r"\d{3,4}[-.\s]?\d{3,4}"
            r"(?:[-.\s]?\d{2,4})?)"
        ),
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    }

    COLUMN_KEYWORDS = {
        "email": ["email", "e-mail", "mail"],
        "phone": ["phone", "telephone", "mobile", "cell", "contact", "fax"],
        "ssn": ["ssn", "social_security", "socialsecurity", "social security"],
        "credit_card": ["credit_card", "creditcard", "cc_number", "ccnum", "card_number", "card"],
        "ip_address": ["ip_address", "ipaddress", "ip"],
        "name": ["name", "full_name", "fullname", "customer_name", "user_name", "username"],
    }

    RISK_MAP = {
        "email": "high",
        "phone": "high",
        "ssn": "critical",
        "credit_card": "critical",
        "ip_address": "medium",
        "name": "medium",
    }

    def detect_pii(self, df: pd.DataFrame) -> list:
        findings = {}

        # 1. Detect by column name keywords
        for pii_type, keywords in self.COLUMN_KEYWORDS.items():
            for col in df.columns:
                normalized = col.lower().replace(" ", "_").replace("-", "_")
                match = any(kw in normalized for kw in keywords)
                if match:
                    sample_values = df[col].dropna().astype(str).unique().tolist()[:5]
                    findings[col] = {
                        "column": col,
                        "type": pii_type,
                        "sample_values": sample_values,
                        "count": int(df[col].notna().sum()),
                        "risk": self.RISK_MAP[pii_type],
                    }
                    break

        # 2. Detect by regex content scan (only for columns not already identified)
        for col in df.columns:
            if col in findings:
                continue
            sample = df[col].dropna().astype(str)
            if len(sample) == 0:
                continue
            for pii_type, pattern in self.PATTERNS.items():
                matches = sample.apply(lambda x: bool(pattern.search(x)))
                match_count = int(matches.sum())
                if match_count > 0 and match_count / max(len(sample), 1) >= 0.1:
                    matched_values = sample[matches].unique().tolist()[:5]
                    findings[col] = {
                        "column": col,
                        "type": pii_type,
                        "sample_values": matched_values,
                        "count": match_count,
                        "risk": self.RISK_MAP[pii_type],
                    }
                    break

        return list(findings.values())

    def mask_pii(self, df: pd.DataFrame, columns_to_mask: Optional[list] = None, lineage_tracker=None) -> tuple:
        masked_df = df.copy()
        change_log = []

        if columns_to_mask is None:
            detected = self.detect_pii(df)
            columns_to_mask = [d["column"] for d in detected]

        type_map = {d["column"]: d["type"] for d in self.detect_pii(df)}

        for col in columns_to_mask:
            if col not in masked_df.columns:
                continue
            pii_type = type_map.get(col)
            original_series = masked_df[col].astype(str)
            masked_series = original_series.apply(
                lambda v: self._mask_value(v, pii_type) if pd.notna(v) else v
            )
            changes = int((original_series != masked_series).sum())
            if changes > 0:
                masked_df[col] = masked_series
                change_log.append({
                    "column": col,
                    "type": pii_type or "unknown",
                    "values_masked": changes,
                })

        if lineage_tracker is not None and change_log:
            from utils.lineage import LineageStep
            from datetime import datetime
            lineage_tracker.add_step(LineageStep(
                step_id="pii_mask",
                step_name="PII Masking",
                category="pii",
                description=f"Masked {sum(c['values_masked'] for c in change_log)} values across {len(change_log)} columns",
                affected_columns=[c["column"] for c in change_log],
                rows_before=len(df), rows_after=len(masked_df),
                columns_before=len(df.columns), columns_after=len(masked_df.columns),
                duration_ms=0,
                timestamp=datetime.now().isoformat(),
            ))

        return masked_df, change_log

    @staticmethod
    def _mask_value(value: str, pii_type: Optional[str]) -> str:
        if not value or value == "nan":
            return value

        if pii_type == "email":
            match = re.match(r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", value)
            if match:
                local, domain = match.group(1), match.group(2)
                masked_local = local[0] + "***" if len(local) > 1 else local + "***"
                return f"{masked_local}@{domain}"
            return value

        if pii_type == "phone":
            digits = re.sub(r"\D", "", value)
            if len(digits) >= 4:
                return "***-***-" + digits[-4:]
            return value

        if pii_type == "ssn":
            match = re.match(r"\d{3}-\d{2}-(\d{4})", value)
            if match:
                return "***-**-" + match.group(1)
            return value

        if pii_type == "credit_card":
            digits = re.sub(r"\D", "", value)
            if len(digits) >= 4:
                return "****-****-****-" + digits[-4:]
            return value

        if pii_type == "ip_address":
            parts = value.split(".")
            if len(parts) == 4 and all(p.isdigit() for p in parts):
                return parts[0] + "." + parts[1] + ".*.*"
            return value

        if pii_type == "name":
            return hashlib.sha256(value.encode()).hexdigest()[:16]

        return value
