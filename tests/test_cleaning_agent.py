import pandas as pd
import numpy as np

from agents.cleaning_agent import DataCleaningAgent


class TestDataCleaningAgent:
    def setup_method(self):
        self.agent = DataCleaningAgent()

    # ── analyze_data_quality ──────────────────────────────────────

    def test_analyze_returns_correct_keys(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = self.agent.analyze_data_quality(df)
        expected_keys = {
            "total_rows", "total_columns", "missing_values",
            "duplicate_rows", "missing_by_column", "missing_pct_by_column",
            "completeness_pct", "type_issues", "whitespace_issues",
            "outlier_counts", "removable_columns", "cat_inconsistencies",
            "validation_issues",
        }
        assert set(result.keys()) == expected_keys

    def test_analyze_value_types(self):
        df = pd.DataFrame({"a": [1, np.nan, 3], "b": ["x", "y", "x"]})
        result = self.agent.analyze_data_quality(df)
        assert isinstance(result["total_rows"], int)
        assert isinstance(result["total_columns"], int)
        assert isinstance(result["missing_values"], int)
        assert isinstance(result["duplicate_rows"], int)
        assert isinstance(result["missing_by_column"], dict)
        assert isinstance(result["missing_pct_by_column"], dict)
        assert isinstance(result["completeness_pct"], float)
        assert isinstance(result["type_issues"], list)
        assert isinstance(result["whitespace_issues"], dict)
        assert isinstance(result["outlier_counts"], dict)
        assert isinstance(result["removable_columns"], list)
        assert isinstance(result["cat_inconsistencies"], dict)
        assert isinstance(result["validation_issues"], dict)

    def test_missing_values_detection(self):
        df = pd.DataFrame({
            "a": [1, np.nan, np.nan, 4],
            "b": [np.nan, 2, 3, 4],
        })
        result = self.agent.analyze_data_quality(df)
        assert result["missing_values"] == 3
        assert result["missing_by_column"]["a"] == 2
        assert result["missing_by_column"]["b"] == 1
        assert result["missing_pct_by_column"]["a"] == 50.0
        assert result["missing_pct_by_column"]["b"] == 25.0

    def test_no_missing_values(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        result = self.agent.analyze_data_quality(df)
        assert result["missing_values"] == 0
        assert result["missing_by_column"] == {}
        assert result["missing_pct_by_column"] == {}

    def test_duplicate_detection(self):
        df = pd.DataFrame({
            "a": [1, 1, 2, 2, 3],
            "b": [10, 10, 20, 20, 30],
        })
        result = self.agent.analyze_data_quality(df)
        assert result["duplicate_rows"] == 2

    def test_no_duplicates(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        result = self.agent.analyze_data_quality(df)
        assert result["duplicate_rows"] == 0

    def test_type_issues_numeric_as_string(self):
        df = pd.DataFrame({"price": ["$1,200", "$3,400", "$5,600", "7,800", "9,000"]})
        result = self.agent.analyze_data_quality(df)
        assert len(result["type_issues"]) == 1
        assert result["type_issues"][0]["column"] == "price"
        assert result["type_issues"][0]["detected"] == "numeric"
        assert result["type_issues"][0]["current"] == "object"

    def test_type_issues_mixed_non_numeric(self):
        df = pd.DataFrame({"code": ["abc", "def", "ghi", "jkl", "mno"]})
        result = self.agent.analyze_data_quality(df)
        assert result["type_issues"] == []

    def test_outlier_detection(self):
        np.random.seed(42)
        df = pd.DataFrame({"value": [10, 12, 11, 13, 12, 1000, 11, 12, 10, 13]})
        result = self.agent.analyze_data_quality(df)
        assert "value" in result["outlier_counts"]
        assert result["outlier_counts"]["value"] > 0

    def test_no_outliers(self):
        df = pd.DataFrame({"value": [10, 11, 12, 13, 10, 11, 12, 13]})
        result = self.agent.analyze_data_quality(df)
        assert result["outlier_counts"] == {}

    def test_whitespace_issues(self):
        df = pd.DataFrame({"name": [" Alice ", "Bob", " Charlie"]})
        result = self.agent.analyze_data_quality(df)
        assert "name" in result["whitespace_issues"]
        assert result["whitespace_issues"]["name"] == 2

    # ── full_clean ────────────────────────────────────────────────

    def test_full_clean_handles_missing_values(self):
        df = pd.DataFrame({
            "value": [1, np.nan, 3, np.nan, 5],
            "category": ["a", "b", None, "a", "b"],
        })
        cleaned, log = self.agent.full_clean(df)
        assert cleaned.isnull().sum().sum() == 0

    def test_full_clean_removes_duplicates(self):
        df = pd.DataFrame({
            "a": [1, 1, 2, 2, 3],
            "b": [10, 10, 20, 20, 30],
        })
        cleaned, log = self.agent.full_clean(df)
        assert len(cleaned) < len(df)

    def test_full_clean_strips_whitespace(self):
        df = pd.DataFrame({"name": [" Alice ", "Bob ", " Charlie"]})
        cleaned, log = self.agent.full_clean(df)
        for val in cleaned["name"]:
            assert val == str(val).strip()

    def test_full_clean_does_not_mutate_input(self):
        original = pd.DataFrame({
            "value": [1, np.nan, 3],
            "cat": ["a", None, "b"],
        })
        original_copy = original.copy()
        self.agent.full_clean(original)
        pd.testing.assert_frame_equal(original, original_copy)

    def test_full_clean_change_log_has_ten_steps(self):
        df = pd.DataFrame({
            "value": [1, 2, 3, 4, 5],
            "cat": ["a", "b", "c", "d", "e"],
        })
        _, log = self.agent.full_clean(df)
        assert len(log) == 10
        for entry in log:
            assert "step" in entry
            assert "title" in entry
            assert "details" in entry

    def test_full_clean_change_log_steps_ordered(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        _, log = self.agent.full_clean(df)
        steps = [entry["step"] for entry in log]
        assert steps == list(range(1, 11))

    def test_full_clean_change_log_titles(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        _, log = self.agent.full_clean(df)
        expected_titles = [
            "Correct Data Types",
            "Handle Missing Values",
            "Remove Duplicate Records",
            "Standardize Formats",
            "Fix Inconsistent Entries",
            "Remove Unnecessary Columns",
            "Handle Outliers (IQR Capping)",
            "Remove Extra Whitespace",
            "Validate Data",
            "Rename Columns",
        ]
        titles = [entry["title"] for entry in log]
        assert titles == expected_titles

    def test_full_clean_corrects_numeric_types(self):
        df = pd.DataFrame({"price": ["$1,200", "$3,400", "$5,600"]})
        cleaned, log = self.agent.full_clean(df)
        assert pd.api.types.is_numeric_dtype(cleaned["price"])

    def test_full_clean_removes_high_nullity_columns(self):
        df = pd.DataFrame({
            "good": [1, 2, 3],
            "bad": [np.nan, np.nan, np.nan],
        })
        cleaned, log = self.agent.full_clean(df)
        assert "bad" not in cleaned.columns

    def test_full_clean_clips_outliers(self):
        df = pd.DataFrame({"value": [10, 12, 11, 1000, 13, 12]})
        cleaned, log = self.agent.full_clean(df)
        assert cleaned["value"].max() < 1000

    def test_full_clean_rename_columns_cleans_names(self):
        df = pd.DataFrame({"My Column": [1, 2], "anotherCol": [3, 4]})
        cleaned, log = self.agent.full_clean(df)
        for col in cleaned.columns:
            assert "_" not in col or col == col.lower()
        assert "my_column" in cleaned.columns or "my column" not in cleaned.columns

    # ── ml_prep ───────────────────────────────────────────────────

    def test_ml_prep_label_encoding(self):
        df = pd.DataFrame({
            "cat": ["a", "b", "c", "a", "b"],
            "val": [1, 2, 3, 4, 5],
        })
        prepared, log = self.agent.ml_prep(df)
        assert pd.api.types.is_numeric_dtype(prepared["cat"])
        assert prepared["cat"].dtype != object
        assert str(prepared["cat"].dtype) != "str"

    def test_ml_prep_scaling(self):
        df = pd.DataFrame({
            "value": [10, 20, 30, 40, 50],
            "label": ["a", "b", "c", "d", "e"],
        })
        prepared, log = self.agent.ml_prep(df)
        assert abs(prepared["value"].mean()) < 1e-10
        assert abs(prepared["value"].std() - 1.0) < 1e-10

    def test_ml_prep_returns_log_with_two_steps(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
        _, log = self.agent.ml_prep(df)
        assert len(log) == 2
        assert log[0]["title"] == "Encode Categorical Variables"
        assert log[1]["title"] == "Scale Numerical Features"

    def test_ml_prep_ignores_high_cardinality_categories(self):
        df = pd.DataFrame({
            "id": [f"id_{i}" for i in range(50)],
            "val": range(50),
        })
        prepared, log = self.agent.ml_prep(df)
        assert not pd.api.types.is_numeric_dtype(prepared["id"])

    # ── outlier detection ─────────────────────────────────────────

    def test_iqr_outlier_detection(self):
        df = pd.DataFrame({"val": [1, 2, 1, 2, 1, 2, 100, 1, 2, 1]})
        qc = self.agent.analyze_data_quality(df)
        assert "val" in qc["outlier_counts"]
        assert qc["outlier_counts"]["val"] >= 1

    def test_no_false_outliers_on_uniform_data(self):
        df = pd.DataFrame({"val": [5, 5, 5, 5, 5]})
        qc = self.agent.analyze_data_quality(df)
        assert qc["outlier_counts"] == {}
