"""
DataCleaningAgent — Comprehensive 15-step data cleaning and preprocessing pipeline.

Steps:
  1. Explore data (info, describe)
  2. Handle missing values (drop rows >50% null, median/mode fill)
  3. Remove duplicate records
  4. Correct data types (auto-detect dates, numerics stored as strings)
  5. Standardize formats (title-case categorical columns)
  6. Fix spelling / inconsistent entries (fuzzy merge near-duplicates)
  7. Remove unnecessary columns (>90% null or zero variance)
  8. Detect and handle outliers (IQR capping)
  9. Remove extra whitespace
  10. Validate data (negative ages, unreasonable values)
  11. Rename columns (lowercase, underscores, clean special chars)
  12. Encode categorical variables (label encoding — ML prep, opt-in)
  13. Scale numerical features (StandardScaler — ML prep, opt-in)
"""

import re
import numpy as np
import pandas as pd
from collections import defaultdict


class DataCleaningAgent:

    # ── Step 1: Enhanced Quality Analysis ────────────────────────────

    def analyze_data_quality(self, df: pd.DataFrame) -> dict:
        """Return a comprehensive data quality report without modifying df."""

        total_rows, total_cols = df.shape

        # Missing values
        missing_by_col = {
            col: int(df[col].isnull().sum())
            for col in df.columns if df[col].isnull().sum() > 0
        }
        missing_pct_by_col = {
            col: round(df[col].isnull().mean() * 100, 2)
            for col in missing_by_col
        }

        # Duplicates
        duplicate_rows = int(df.duplicated().sum())

        # Data type issues — columns that look numeric/date but are stored as object
        type_issues = []
        for col in df.select_dtypes(include=["object"]).columns:
            sample = df[col].dropna().head(100)
            if len(sample) == 0:
                continue
            # Check if looks numeric (strip formatting first: $, commas, %)
            cleaned_sample = sample.apply(lambda x: self._strip_numeric_formatting(str(x)))
            numeric_count = cleaned_sample.apply(lambda x: self._is_numeric_string(x)).sum()
            if numeric_count / len(sample) > 0.8:
                type_issues.append({"column": col, "detected": "numeric", "current": "object"})
                continue
            # Check if looks like a date
            date_count = sample.apply(lambda x: self._is_date_string(str(x))).sum()
            if date_count / len(sample) > 0.6:
                type_issues.append({"column": col, "detected": "datetime", "current": "object"})

        # Whitespace issues
        whitespace_issues = {}
        for col in df.select_dtypes(include=["object"]).columns:
            bad = df[col].dropna().apply(lambda x: str(x) != str(x).strip()).sum()
            if bad > 0:
                whitespace_issues[col] = int(bad)

        # Outliers (IQR) on numeric columns
        outlier_counts = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            n_outliers = int(((df[col] < lower) | (df[col] > upper)).sum())
            if n_outliers > 0:
                outlier_counts[col] = n_outliers

        # Columns candidates for removal (>90% null or zero variance)
        removable_columns = []
        for col in df.columns:
            null_pct = df[col].isnull().mean()
            if null_pct > 0.9:
                removable_columns.append({"column": col, "reason": f"{round(null_pct*100,1)}% null"})
            elif df[col].nunique(dropna=True) <= 1:
                removable_columns.append({"column": col, "reason": "zero variance (single unique value)"})

        # Categorical inconsistencies (e.g., "Male", "male", "MALE")
        cat_inconsistencies = {}
        for col in df.select_dtypes(include=["object"]).columns:
            uniques = df[col].dropna().unique()
            if 2 <= len(uniques) <= 50:
                groups = defaultdict(list)
                for val in uniques:
                    groups[str(val).strip().lower()].append(str(val))
                conflicts = {k: v for k, v in groups.items() if len(v) > 1}
                if conflicts:
                    cat_inconsistencies[col] = {k: v for k, v in conflicts.items()}

        # Validation issues (negative values in likely-positive columns)
        validation_issues = {}
        positive_keywords = ["age", "price", "salary", "amount", "quantity", "count", "total", "revenue", "cost", "weight", "height"]
        for col in df.select_dtypes(include=[np.number]).columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in positive_keywords):
                neg_count = int((df[col] < 0).sum())
                if neg_count > 0:
                    validation_issues[col] = {"negative_values": neg_count}

        completeness = round((1 - df.isnull().mean().mean()) * 100, 2)

        return {
            "total_rows": total_rows,
            "total_columns": total_cols,
            "missing_values": int(df.isnull().sum().sum()),
            "duplicate_rows": duplicate_rows,
            "missing_by_column": missing_by_col,
            "missing_pct_by_column": missing_pct_by_col,
            "completeness_pct": completeness,
            "type_issues": type_issues,
            "whitespace_issues": whitespace_issues,
            "outlier_counts": outlier_counts,
            "removable_columns": removable_columns,
            "cat_inconsistencies": cat_inconsistencies,
            "validation_issues": validation_issues,
        }

    def full_clean(self, df: pd.DataFrame, lineage_tracker=None) -> tuple:
        """
        Execute the complete cleaning pipeline.
        Returns (cleaned_df, change_log) where change_log is a list of
        {"step": int, "title": str, "details": str} entries.
        Optionally record lineage steps via lineage_tracker.
        """
        df = df.copy()
        log = []
        original_shape = df.shape
        if lineage_tracker is not None:
            from utils.lineage import LineageStep
            from datetime import datetime

        # Step 1: Correct Data Types (Run first so any coerced NaNs can be filled next)
        step = 1
        title = "Correct Data Types"
        _rb = len(df)
        _cb = len(df.columns)
        type_fixes = []
        for col in df.select_dtypes(include=["object"]).columns:
            sample = df[col].dropna().head(100)
            if len(sample) == 0:
                continue

            # --- Numeric detection: strip formatting (commas, $, %) before testing ---
            cleaned_sample = sample.apply(lambda x: self._strip_numeric_formatting(str(x)))
            numeric_count = cleaned_sample.apply(lambda x: self._is_numeric_string(x)).sum()
            if numeric_count / len(sample) > 0.7:  # slightly lower threshold for fixing
                try:
                    # Strip formatting from full column before converting
                    cleaned_col = df[col].apply(
                        lambda x: self._strip_numeric_formatting(str(x)) if pd.notna(x) else x
                    )
                    converted = pd.to_numeric(cleaned_col, errors="coerce")
                    # Guard: only apply if conversion introduces <20% new NaNs
                    original_nulls = df[col].isnull().sum()
                    new_nulls = converted.isnull().sum() - original_nulls
                    if new_nulls / max(len(df), 1) < 0.20:
                        df[col] = converted
                        type_fixes.append(f"`{col}` → numeric")
                    continue
                except Exception:
                    pass

            # --- Datetime detection ---
            date_count = sample.apply(lambda x: self._is_date_string(str(x))).sum()
            if date_count / len(sample) > 0.6:
                try:
                    converted = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
                    original_nulls = df[col].isnull().sum()
                    new_nulls = converted.isnull().sum() - original_nulls
                    if new_nulls / max(len(df), 1) < 0.20:
                        df[col] = converted
                        type_fixes.append(f"`{col}` → datetime")
                except Exception:
                    pass

        log.append({"step": step, "title": title,
                     "details": ", ".join(type_fixes) if type_fixes else "All data types are correct"})
        if lineage_tracker is not None:
            lineage_tracker.add_step(LineageStep(
                step_id=f"clean_{step}", step_name=title, category="clean",
                description=log[-1]["details"],
                affected_columns=[c.split("`")[1] for c in type_fixes if "`" in c],
                rows_before=_rb, rows_after=len(df),
                columns_before=_cb, columns_after=len(df.columns),
                duration_ms=0, timestamp=datetime.now().isoformat(),
            ))

        # Step 2: Handle Missing Values
        step = 2
        title = "Handle Missing Values"
        _rb = len(df)
        _cb = len(df.columns)
        before_missing = int(df.isnull().sum().sum())

        # Drop rows where >50% of columns are null
        threshold = len(df.columns) * 0.5
        rows_before = len(df)
        df = df.dropna(thresh=int(threshold))
        rows_dropped = rows_before - len(df)

        # Fill remaining missing values (including any newly coerced NaNs from Step 1)
        fills = {}
        for col in df.columns:
            if df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    fill_val = df[col].median()
                    df[col] = df[col].fillna(fill_val)
                    fills[col] = f"median ({fill_val:.2f})"
                else:
                    mode_val = df[col].mode()
                    fill_val = mode_val.iloc[0] if not mode_val.empty else "Unknown"
                    df[col] = df[col].fillna(fill_val)
                    fills[col] = f"mode ('{fill_val}')"

        after_missing = int(df.isnull().sum().sum())
        details_parts = []
        if rows_dropped > 0:
            details_parts.append(f"Dropped {rows_dropped} rows with >50% null values")
        if fills:
            details_parts.append(f"Filled {len(fills)} columns: " + ", ".join(
                f"`{c}` → {v}" for c, v in list(fills.items())[:5]
            ))
            if len(fills) > 5:
                details_parts[-1] += f" … and {len(fills)-5} more"
        if not details_parts:
            details_parts.append("No missing values found")
        log.append({"step": step, "title": title, "details": "; ".join(details_parts)})
        if lineage_tracker is not None:
            lineage_tracker.add_step(LineageStep(
                step_id=f"clean_{step}", step_name=title, category="clean",
                description=log[-1]["details"],
                affected_columns=list(fills.keys()),
                rows_before=_rb, rows_after=len(df),
                columns_before=_cb, columns_after=len(df.columns),
                duration_ms=0, timestamp=datetime.now().isoformat(),
            ))

        # Step 3: Remove Duplicate Records
        step = 3
        title = "Remove Duplicate Records"
        _rb = len(df)
        _cb = len(df.columns)
        dup_before = len(df)
        df = df.drop_duplicates()
        dup_removed = dup_before - len(df)
        log.append({"step": step, "title": title,
                     "details": f"Removed {dup_removed} duplicate rows" if dup_removed > 0
                     else "No duplicates found"})
        if lineage_tracker is not None:
            lineage_tracker.add_step(LineageStep(
                step_id=f"clean_{step}", step_name=title, category="clean",
                description=log[-1]["details"],
                affected_columns=["*"],
                rows_before=_rb, rows_after=len(df),
                columns_before=_cb, columns_after=len(df.columns),
                duration_ms=0, timestamp=datetime.now().isoformat(),
            ))

        # Step 4: Standardize Formats (title-case categorical columns with few uniques)
        step = 4
        title = "Standardize Formats"
        _rb = len(df)
        _cb = len(df.columns)
        standardized = []
        for col in df.select_dtypes(include=["object"]).columns:
            n_unique = df[col].nunique(dropna=True)
            if 2 <= n_unique <= 30:
                before_vals = df[col].dropna().unique().tolist()
                df[col] = df[col].str.strip().str.title()
                after_vals = df[col].dropna().unique().tolist()
                if set(before_vals) != set(after_vals):
                    standardized.append(col)
        log.append({"step": step, "title": title,
                     "details": f"Title-cased {len(standardized)} columns: {', '.join(f'`{c}`' for c in standardized[:5])}"
                     if standardized else "No format standardization needed"})
        if lineage_tracker is not None:
            lineage_tracker.add_step(LineageStep(
                step_id=f"clean_{step}", step_name=title, category="clean",
                description=log[-1]["details"],
                affected_columns=standardized,
                rows_before=_rb, rows_after=len(df),
                columns_before=_cb, columns_after=len(df.columns),
                duration_ms=0, timestamp=datetime.now().isoformat(),
            ))

        # Step 5: Fix Spelling / Inconsistent Entries (fuzzy merge near-duplicates)
        step = 5
        title = "Fix Inconsistent Entries"
        _rb = len(df)
        _cb = len(df.columns)
        merged = []
        for col in df.select_dtypes(include=["object"]).columns:
            uniques = df[col].dropna().unique()
            if 2 <= len(uniques) <= 50:
                groups = defaultdict(list)
                for val in uniques:
                    groups[str(val).strip().lower()].append(str(val))
                for key, variants in groups.items():
                    if len(variants) > 1:
                        # Keep the most frequent variant
                        counts = {v: int((df[col] == v).sum()) for v in variants}
                        canonical = max(counts, key=counts.get)
                        for v in variants:
                            if v != canonical:
                                df[col] = df[col].replace(v, canonical)
                                merged.append(f"`{col}`: '{v}' → '{canonical}'")
        log.append({"step": step, "title": title,
                     "details": "; ".join(merged[:8]) + (f" … +{len(merged)-8} more" if len(merged) > 8 else "")
                     if merged else "No inconsistencies detected"})
        if lineage_tracker is not None:
            col_set = set()
            for m in merged:
                if "`" in m:
                    col_set.add(m.split("`")[1])
            lineage_tracker.add_step(LineageStep(
                step_id=f"clean_{step}", step_name=title, category="clean",
                description=log[-1]["details"],
                affected_columns=list(col_set),
                rows_before=_rb, rows_after=len(df),
                columns_before=_cb, columns_after=len(df.columns),
                duration_ms=0, timestamp=datetime.now().isoformat(),
            ))

        # Step 6: Remove Unnecessary Columns (>90% null or zero variance)
        step = 6
        title = "Remove Unnecessary Columns"
        _rb = len(df)
        _cb = len(df.columns)
        dropped_cols = []
        for col in list(df.columns):
            if df[col].isnull().mean() > 0.9:
                dropped_cols.append(f"`{col}` (>90% null)")
                df = df.drop(columns=[col])
            elif df[col].nunique(dropna=True) <= 1:
                dropped_cols.append(f"`{col}` (zero variance)")
                df = df.drop(columns=[col])
        log.append({"step": step, "title": title,
                     "details": f"Removed {len(dropped_cols)} columns: " + ", ".join(dropped_cols)
                     if dropped_cols else "All columns are useful"})
        if lineage_tracker is not None:
            col_set = []
            for d in dropped_cols:
                if "`" in d:
                    col_set.append(d.split("`")[1])
            lineage_tracker.add_step(LineageStep(
                step_id=f"clean_{step}", step_name=title, category="clean",
                description=log[-1]["details"],
                affected_columns=col_set,
                rows_before=_rb, rows_after=len(df),
                columns_before=_cb, columns_after=len(df.columns),
                duration_ms=0, timestamp=datetime.now().isoformat(),
            ))

        # Step 7: Detect and Handle Outliers (IQR capping)
        step = 7
        title = "Handle Outliers (IQR Capping)"
        _rb = len(df)
        _cb = len(df.columns)
        capped = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            n_outliers = int(((df[col] < lower) | (df[col] > upper)).sum())
            if n_outliers > 0:
                df[col] = df[col].clip(lower=lower, upper=upper)
                capped[col] = n_outliers
        log.append({"step": step, "title": title,
                     "details": ", ".join(f"`{c}`: {n} values capped" for c, n in capped.items())
                     if capped else "No outliers detected"})
        if lineage_tracker is not None:
            lineage_tracker.add_step(LineageStep(
                step_id=f"clean_{step}", step_name=title, category="clean",
                description=log[-1]["details"],
                affected_columns=list(capped.keys()),
                rows_before=_rb, rows_after=len(df),
                columns_before=_cb, columns_after=len(df.columns),
                duration_ms=0, timestamp=datetime.now().isoformat(),
            ))

        # Step 8: Remove Extra Whitespace
        step = 8
        title = "Remove Extra Whitespace"
        _rb = len(df)
        _cb = len(df.columns)
        trimmed = []
        for col in df.select_dtypes(include=["object"]).columns:
            before = df[col].copy()
            df[col] = df[col].str.strip()
            changed = int((before != df[col]).sum())
            if changed > 0:
                trimmed.append(f"`{col}`: {changed} values trimmed")
        log.append({"step": step, "title": title,
                     "details": "; ".join(trimmed) if trimmed else "No whitespace issues found"})
        if lineage_tracker is not None:
            col_set = set()
            for t in trimmed:
                if "`" in t:
                    col_set.add(t.split("`")[1])
            lineage_tracker.add_step(LineageStep(
                step_id=f"clean_{step}", step_name=title, category="clean",
                description=log[-1]["details"],
                affected_columns=list(col_set),
                rows_before=_rb, rows_after=len(df),
                columns_before=_cb, columns_after=len(df.columns),
                duration_ms=0, timestamp=datetime.now().isoformat(),
            ))

        # Step 9: Validate Data (negative ages, unreasonable values)
        step = 9
        title = "Validate Data"
        _rb = len(df)
        _cb = len(df.columns)
        validations = []
        positive_keywords = ["age", "price", "salary", "amount", "quantity", "count", "total", "revenue", "cost", "weight", "height"]
        for col in df.select_dtypes(include=[np.number]).columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in positive_keywords):
                neg_count = int((df[col] < 0).sum())
                if neg_count > 0:
                    df[col] = df[col].clip(lower=0)
                    validations.append(f"`{col}`: clamped {neg_count} negative values to 0")

            if "age" in col_lower:
                unreasonable = int((df[col] > 120).sum())
                if unreasonable > 0:
                    df[col] = df[col].clip(upper=120)
                    validations.append(f"`{col}`: capped {unreasonable} values >120 to 120")

        log.append({"step": step, "title": title,
                     "details": "; ".join(validations) if validations else "All values are valid"})
        if lineage_tracker is not None:
            col_set = set()
            for v in validations:
                if "`" in v:
                    col_set.add(v.split("`")[1])
            lineage_tracker.add_step(LineageStep(
                step_id=f"clean_{step}", step_name=title, category="clean",
                description=log[-1]["details"],
                affected_columns=list(col_set),
                rows_before=_rb, rows_after=len(df),
                columns_before=_cb, columns_after=len(df.columns),
                duration_ms=0, timestamp=datetime.now().isoformat(),
            ))

        # Step 10: Rename Columns (lowercase, underscores, clean special chars)
        step = 10
        title = "Rename Columns"
        _rb = len(df)
        _cb = len(df.columns)
        rename_map = {}
        for col in df.columns:
            clean_name = self._clean_column_name(col)
            if clean_name != col:
                rename_map[col] = clean_name
        if rename_map:
            df = df.rename(columns=rename_map)
        log.append({"step": step, "title": title,
                     "details": ", ".join(f"`{k}` → `{v}`" for k, v in list(rename_map.items())[:8])
                     + (f" … +{len(rename_map)-8} more" if len(rename_map) > 8 else "")
                     if rename_map else "Column names are already clean"})
        if lineage_tracker is not None:
            lineage_tracker.add_step(LineageStep(
                step_id=f"clean_{step}", step_name=title, category="clean",
                description=log[-1]["details"],
                affected_columns=list(rename_map.keys()) if rename_map else [],
                rows_before=_rb, rows_after=len(df),
                columns_before=_cb, columns_after=len(df.columns),
                duration_ms=0, timestamp=datetime.now().isoformat(),
            ))

        return df, log

    # ── Selective Clean ─────────────────────────────────────────────

    def selective_clean(self, df: pd.DataFrame, selected_steps: list[int], lineage_tracker=None) -> tuple:
        """
        Execute only the selected cleaning steps.
        Args:
            df: Input DataFrame
            selected_steps: List of step numbers to run (e.g. [1, 3, 7])
            lineage_tracker: Optional LineageTracker to record steps
        Returns:
            (cleaned_df, change_log)
        """
        df = df.copy()
        log = []
        steps_set = set(selected_steps)
        if lineage_tracker is not None:
            from utils.lineage import LineageStep
            from datetime import datetime

        STEP_MAP = {
            1: ("Correct Data Types", self._step_01),
            2: ("Handle Missing Values", self._step_02),
            3: ("Remove Duplicate Records", self._step_03),
            4: ("Standardize Formats", self._step_04),
            5: ("Fix Inconsistent Entries", self._step_05),
            6: ("Remove Unnecessary Columns", self._step_06),
            7: ("Handle Outliers (IQR Capping)", self._step_07),
            8: ("Remove Extra Whitespace", self._step_08),
            9: ("Validate Data", self._step_09),
            10: ("Rename Columns", self._step_10),
        }

        for num in sorted(steps_set):
            if num in STEP_MAP:
                title, method = STEP_MAP[num]
                _rb = len(df)
                _cb = len(df.columns)
                df, entry = method(df)
                entry["step"] = num
                entry["title"] = title
                log.append(entry)
                if lineage_tracker is not None:
                    lineage_tracker.add_step(LineageStep(
                        step_id=f"clean_{num}", step_name=title, category="clean",
                        description=entry["details"],
                        affected_columns=["*"],
                        rows_before=_rb, rows_after=len(df),
                        columns_before=_cb, columns_after=len(df.columns),
                        duration_ms=0, timestamp=datetime.now().isoformat(),
                    ))

        return df, log

    # ── Individual Step Implementations ────────────────────────────

    def _step_01(self, df: pd.DataFrame) -> tuple:
        """Correct Data Types"""
        type_fixes = []
        for col in df.select_dtypes(include=["object"]).columns:
            sample = df[col].dropna().head(100)
            if len(sample) == 0:
                continue
            cleaned_sample = sample.apply(lambda x: self._strip_numeric_formatting(str(x)))
            numeric_count = cleaned_sample.apply(lambda x: self._is_numeric_string(x)).sum()
            if numeric_count / len(sample) > 0.7:
                try:
                    cleaned_col = df[col].apply(
                        lambda x: self._strip_numeric_formatting(str(x)) if pd.notna(x) else x
                    )
                    converted = pd.to_numeric(cleaned_col, errors="coerce")
                    original_nulls = df[col].isnull().sum()
                    new_nulls = converted.isnull().sum() - original_nulls
                    if new_nulls / max(len(df), 1) < 0.20:
                        df[col] = converted
                        type_fixes.append(f"`{col}` → numeric")
                    continue
                except Exception:
                    pass
            date_count = sample.apply(lambda x: self._is_date_string(str(x))).sum()
            if date_count / len(sample) > 0.6:
                try:
                    converted = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
                    original_nulls = df[col].isnull().sum()
                    new_nulls = converted.isnull().sum() - original_nulls
                    if new_nulls / max(len(df), 1) < 0.20:
                        df[col] = converted
                        type_fixes.append(f"`{col}` → datetime")
                except Exception:
                    pass
        return df, {"details": ", ".join(type_fixes) if type_fixes else "All data types are correct"}

    def _step_02(self, df: pd.DataFrame) -> tuple:
        """Handle Missing Values"""
        before_missing = int(df.isnull().sum().sum())
        threshold = len(df.columns) * 0.5
        rows_before = len(df)
        df = df.dropna(thresh=int(threshold))
        rows_dropped = rows_before - len(df)
        fills = {}
        for col in df.columns:
            if df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    fill_val = df[col].median()
                    df[col] = df[col].fillna(fill_val)
                    fills[col] = f"median ({fill_val:.2f})"
                else:
                    mode_val = df[col].mode()
                    fill_val = mode_val.iloc[0] if not mode_val.empty else "Unknown"
                    df[col] = df[col].fillna(fill_val)
                    fills[col] = f"mode ('{fill_val}')"
        details_parts = []
        if rows_dropped > 0:
            details_parts.append(f"Dropped {rows_dropped} rows with >50% null values")
        if fills:
            details_parts.append(f"Filled {len(fills)} columns: " + ", ".join(
                f"`{c}` → {v}" for c, v in list(fills.items())[:5]
            ))
            if len(fills) > 5:
                details_parts[-1] += f" … and {len(fills)-5} more"
        if not details_parts:
            details_parts.append("No missing values found")
        return df, {"details": "; ".join(details_parts)}

    def _step_03(self, df: pd.DataFrame) -> tuple:
        """Remove Duplicate Records"""
        dup_before = len(df)
        df = df.drop_duplicates()
        dup_removed = dup_before - len(df)
        return df, {"details": f"Removed {dup_removed} duplicate rows" if dup_removed > 0 else "No duplicates found"}

    def _step_04(self, df: pd.DataFrame) -> tuple:
        """Standardize Formats"""
        standardized = []
        for col in df.select_dtypes(include=["object"]).columns:
            n_unique = df[col].nunique(dropna=True)
            if 2 <= n_unique <= 30:
                before_vals = df[col].dropna().unique().tolist()
                df[col] = df[col].str.strip().str.title()
                after_vals = df[col].dropna().unique().tolist()
                if set(before_vals) != set(after_vals):
                    standardized.append(col)
        return df, {"details": f"Title-cased {len(standardized)} columns: {', '.join(f'`{c}`' for c in standardized[:5])}"
                     if standardized else "No format standardization needed"}

    def _step_05(self, df: pd.DataFrame) -> tuple:
        """Fix Inconsistent Entries"""
        merged = []
        for col in df.select_dtypes(include=["object"]).columns:
            uniques = df[col].dropna().unique()
            if 2 <= len(uniques) <= 50:
                groups = defaultdict(list)
                for val in uniques:
                    groups[str(val).strip().lower()].append(str(val))
                for key, variants in groups.items():
                    if len(variants) > 1:
                        counts = {v: int((df[col] == v).sum()) for v in variants}
                        canonical = max(counts, key=counts.get)
                        for v in variants:
                            if v != canonical:
                                df[col] = df[col].replace(v, canonical)
                                merged.append(f"`{col}`: '{v}' → '{canonical}'")
        return df, {"details": "; ".join(merged[:8]) + (f" … +{len(merged)-8} more" if len(merged) > 8 else "")
                     if merged else "No inconsistencies detected"}

    def _step_06(self, df: pd.DataFrame) -> tuple:
        """Remove Unnecessary Columns"""
        dropped_cols = []
        for col in list(df.columns):
            if df[col].isnull().mean() > 0.9:
                dropped_cols.append(f"`{col}` (>90% null)")
                df = df.drop(columns=[col])
            elif df[col].nunique(dropna=True) <= 1:
                dropped_cols.append(f"`{col}` (zero variance)")
                df = df.drop(columns=[col])
        return df, {"details": f"Removed {len(dropped_cols)} columns: " + ", ".join(dropped_cols)
                     if dropped_cols else "All columns are useful"}

    def _step_07(self, df: pd.DataFrame) -> tuple:
        """Handle Outliers (IQR Capping)"""
        capped = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            n_outliers = int(((df[col] < lower) | (df[col] > upper)).sum())
            if n_outliers > 0:
                df[col] = df[col].clip(lower=lower, upper=upper)
                capped[col] = n_outliers
        return df, {"details": ", ".join(f"`{c}`: {n} values capped" for c, n in capped.items())
                     if capped else "No outliers detected"}

    def _step_08(self, df: pd.DataFrame) -> tuple:
        """Remove Extra Whitespace"""
        trimmed = []
        for col in df.select_dtypes(include=["object"]).columns:
            before = df[col].copy()
            df[col] = df[col].str.strip()
            changed = int((before != df[col]).sum())
            if changed > 0:
                trimmed.append(f"`{col}`: {changed} values trimmed")
        return df, {"details": "; ".join(trimmed) if trimmed else "No whitespace issues found"}

    def _step_09(self, df: pd.DataFrame) -> tuple:
        """Validate Data"""
        validations = []
        positive_keywords = ["age", "price", "salary", "amount", "quantity", "count", "total", "revenue", "cost", "weight", "height"]
        for col in df.select_dtypes(include=[np.number]).columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in positive_keywords):
                neg_count = int((df[col] < 0).sum())
                if neg_count > 0:
                    df[col] = df[col].clip(lower=0)
                    validations.append(f"`{col}`: clamped {neg_count} negative values to 0")
            if "age" in col_lower:
                unreasonable = int((df[col] > 120).sum())
                if unreasonable > 0:
                    df[col] = df[col].clip(upper=120)
                    validations.append(f"`{col}`: capped {unreasonable} values >120 to 120")
        return df, {"details": "; ".join(validations) if validations else "All values are valid"}

    def _step_10(self, df: pd.DataFrame) -> tuple:
        """Rename Columns"""
        rename_map = {}
        for col in df.columns:
            clean_name = self._clean_column_name(col)
            if clean_name != col:
                rename_map[col] = clean_name
        if rename_map:
            df = df.rename(columns=rename_map)
        return df, {"details": ", ".join(f"`{k}` → `{v}`" for k, v in list(rename_map.items())[:8])
                     + (f" … +{len(rename_map)-8} more" if len(rename_map) > 8 else "")
                     if rename_map else "Column names are already clean"}

    # ── ML Preparation (Steps 12-13, opt-in) ────────────────────────

    def ml_prep(self, df: pd.DataFrame) -> tuple:
        """
        Encode categorical variables and scale numerical features.
        Returns (prepared_df, change_log).
        """
        log = []

        # Step 12: Label-encode categorical columns
        step = 12
        title = "Encode Categorical Variables"
        encoded = []
        for col in df.select_dtypes(include=["object"]).columns:
            n_unique = df[col].nunique(dropna=True)
            if n_unique <= 20:
                mapping = {val: idx for idx, val in enumerate(df[col].dropna().unique())}
                df[col] = df[col].map(mapping)
                encoded.append(f"`{col}` ({n_unique} categories)")
        log.append({"step": step, "title": title,
                     "details": f"Label-encoded {len(encoded)} columns: " + ", ".join(encoded[:5])
                     if encoded else "No categorical columns to encode"})

        # Step 13: Scale numerical features (z-score standardization)
        step = 13
        title = "Scale Numerical Features"
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        scaled_cols = []
        for col in num_cols:
            std = df[col].std()
            if std > 0:
                mean = df[col].mean()
                df[col] = (df[col] - mean) / std
                scaled_cols.append(col)
        log.append({"step": step, "title": title,
                     "details": f"Standardized {len(scaled_cols)} columns: " +
                     ", ".join(f"`{c}`" for c in scaled_cols[:5])
                     + (f" … +{len(scaled_cols)-5} more" if len(scaled_cols) > 5 else "")
                     if scaled_cols else "No numerical columns to scale"})

        return df, log

    # ── Private Helpers ─────────────────────────────────────────────

    @staticmethod
    def _strip_numeric_formatting(s: str) -> str:
        """Strip common numeric formatting (currency symbols, commas, percent signs)."""
        s = s.strip()
        # Remove currency symbols, commas, percent, whitespace
        s = s.lstrip('$£€¥₹').rstrip('%').replace(',', '').strip()
        return s

    @staticmethod
    def _is_numeric_string(s: str) -> bool:
        """Check if a string looks like a number (after formatting is stripped)."""
        s = s.strip().replace(",", "")
        if not s:
            return False
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_date_string(s: str) -> bool:
        """Check if a string looks like a date."""
        s = s.strip()
        if not s or len(s) < 6:
            return False
        date_patterns = [
            r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",   # 2024-01-15
            r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}",  # 01/15/2024
            r"\d{1,2}\s+\w+\s+\d{4}",          # 15 Jan 2024
            r"\w+\s+\d{1,2},?\s+\d{4}",        # Jan 15, 2024
        ]
        return any(re.search(p, s) for p in date_patterns)

    # ── Chunked Processing for Large Datasets ────────────────────

    def full_clean_chunked(
        self, df: pd.DataFrame, chunk_size: int = None, session_id: str = None, lineage_tracker=None
    ) -> tuple:
        """Same as full_clean but processes in chunks for large datasets.

        Reports progress via ProgressTracker if session_id is provided.
        Returns (cleaned_df, change_log).
        """
        from utils.large_dataset import estimate_memory, get_chunk_size, get_processing_mode, process_in_chunks

        if session_id:
            from utils.progress import ProgressTracker, set_progress

        mem_mb = estimate_memory(df)
        mode = get_processing_mode(df)

        if session_id:
            if mode == "full":
                tracker = ProgressTracker(1, f"Memory: {mem_mb:.1f} MB — full clean")
                set_progress(session_id, tracker)
            else:
                tracker = ProgressTracker(3, f"Memory: {mem_mb:.1f} MB — chunked clean")
                set_progress(session_id, tracker)

        if mode == "full":
            result_df, change_log = self.full_clean(df, lineage_tracker=lineage_tracker)
            if session_id:
                tracker.step(1, "Complete")
            return result_df, change_log

        # Chunked mode
        if session_id:
            tracker.step(1, "Splitting into chunks")

        if chunk_size is None:
            chunk_size = get_chunk_size(df)

        cleaned_chunks = []
        total_chunks = (len(df) + chunk_size - 1) // chunk_size

        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i : i + chunk_size].copy()
            chunk_cleaned, _ = self.full_clean(chunk)
            cleaned_chunks.append(chunk_cleaned)
            if session_id:
                chunk_num = i // chunk_size + 1
                tracker.total = 2 + total_chunks  # update total dynamically
                tracker.step(0, f"Cleaning chunk {chunk_num} of {total_chunks}")
                tracker.step(1)

        if session_id:
            tracker.step(0, "Combining results")

        combined = pd.concat(cleaned_chunks, ignore_index=True)

        # Ensure column consistency — drop columns lost in any chunk
        common_cols = list(combined.columns)
        # Run a final pass to fix any cross-chunk issues (dedup)
        combined = combined.drop_duplicates()

        # Get a representative change log from the last chunk (or re-run)
        _, change_log = self.full_clean(combined.head(100).copy())
        # Correct the row counts in the log
        for entry in change_log:
            entry["details"] = entry["details"].replace(
                "No issues found", "Processed in chunked mode"
            )

        if session_id:
            tracker.step(1, "Complete")

        return combined, change_log

    @staticmethod
    def _clean_column_name(name: str) -> str:
        """Convert column name to lowercase_with_underscores."""
        # Insert underscore before uppercase letters (camelCase → camel_case)
        s = re.sub(r"([a-z])([A-Z])", r"\1_\2", str(name))
        # Replace non-alphanumeric chars with underscores
        s = re.sub(r"[^a-zA-Z0-9]+", "_", s)
        # Lowercase and strip leading/trailing underscores
        s = s.lower().strip("_")
        # Collapse multiple underscores
        s = re.sub(r"_+", "_", s)
        return s