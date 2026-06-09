import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helper import truncate_dataframe
from utils.metrics import basic_stats, missing_value_summary


class TestTruncateDataFrame:
    def test_truncates_when_over_limit(self):
        df = pd.DataFrame({"a": range(100)})
        result = truncate_dataframe(df, max_rows=10)
        assert len(result) == 10

    def test_does_not_truncate_when_under_limit(self):
        df = pd.DataFrame({"a": range(5)})
        result = truncate_dataframe(df, max_rows=10)
        assert len(result) == 5

    def test_does_not_truncate_when_equal_to_limit(self):
        df = pd.DataFrame({"a": range(10)})
        result = truncate_dataframe(df, max_rows=10)
        assert len(result) == 10

    def test_returns_first_n_rows(self):
        df = pd.DataFrame({"a": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]})
        result = truncate_dataframe(df, max_rows=3)
        assert list(result["a"]) == [0, 1, 2]

    def test_default_max_rows_is_10000(self):
        df = pd.DataFrame({"a": range(5000)})
        result = truncate_dataframe(df)
        assert len(result) == 5000

    def test_does_not_mutate_input(self):
        df = pd.DataFrame({"a": range(20)})
        original_len = len(df)
        truncate_dataframe(df, max_rows=5)
        assert len(df) == original_len


class TestBasicStats:
    def test_returns_correct_keys(self):
        df = pd.DataFrame({
            "num": [1, 2, 3],
            "cat": ["a", "b", "c"],
        })
        stats = basic_stats(df)
        expected_keys = {
            "rows", "columns", "numeric_columns",
            "categorical_columns", "missing_values",
            "duplicate_rows", "memory_mb",
        }
        assert set(stats.keys()) == expected_keys

    def test_row_count(self):
        df = pd.DataFrame({"a": [1, 2, 3, 4, 5]})
        stats = basic_stats(df)
        assert stats["rows"] == 5

    def test_column_count(self):
        df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
        stats = basic_stats(df)
        assert stats["columns"] == 3

    def test_numeric_columns_list(self):
        df = pd.DataFrame({
            "x": [1, 2, 3],
            "y": [1.5, 2.5, 3.5],
            "z": ["a", "b", "c"],
        })
        stats = basic_stats(df)
        assert stats["numeric_columns"] == ["x", "y"]

    def test_categorical_columns_list(self):
        df = pd.DataFrame({
            "a": ["x", "y", "z"],
            "b": [1, 2, 3],
        })
        stats = basic_stats(df)
        assert stats["categorical_columns"] == ["a"]

    def test_missing_values_count(self):
        df = pd.DataFrame({"a": [1, np.nan, 3], "b": [np.nan, 2, 3]})
        stats = basic_stats(df)
        assert stats["missing_values"] == 2

    def test_duplicate_rows_count(self):
        df = pd.DataFrame({"a": [1, 1, 2, 2, 3]})
        stats = basic_stats(df)
        assert stats["duplicate_rows"] == 2

    def test_memory_mb_is_float(self):
        df = pd.DataFrame({"a": range(1000)})
        stats = basic_stats(df)
        assert isinstance(stats["memory_mb"], float)

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        stats = basic_stats(df)
        assert stats["rows"] == 0
        assert stats["columns"] == 0


class TestMissingValueSummary:
    def test_returns_dataframe(self):
        df = pd.DataFrame({"a": [1, np.nan, 3]})
        result = missing_value_summary(df)
        assert isinstance(result, pd.DataFrame)

    def test_returns_only_columns_with_missing(self):
        df = pd.DataFrame({
            "a": [1, np.nan, 3],
            "b": [1, 2, 3],
            "c": [np.nan, np.nan, 3],
        })
        result = missing_value_summary(df)
        assert "a" in result.index
        assert "c" in result.index
        assert "b" not in result.index

    def test_returns_correct_columns(self):
        df = pd.DataFrame({"a": [1, np.nan, 3]})
        result = missing_value_summary(df)
        assert "missing_count" in result.columns
        assert "missing_pct" in result.columns

    def test_missing_count_correct(self):
        df = pd.DataFrame({"a": [1, np.nan, np.nan, 4]})
        result = missing_value_summary(df)
        assert result.loc["a", "missing_count"] == 2

    def test_missing_pct_correct(self):
        df = pd.DataFrame({"a": [1, np.nan, np.nan, 4]})
        result = missing_value_summary(df)
        assert result.loc["a", "missing_pct"] == 50.0

    def test_returns_sorted_by_missing_count_descending(self):
        df = pd.DataFrame({
            "x": [1, np.nan, np.nan, np.nan],
            "y": [1, np.nan, 3, 4],
        })
        result = missing_value_summary(df)
        assert result.index[0] == "x"

    def test_empty_dataframe_returns_empty(self):
        df = pd.DataFrame()
        result = missing_value_summary(df)
        assert len(result) == 0

    def test_no_missing_returns_empty(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        result = missing_value_summary(df)
        assert len(result) == 0
