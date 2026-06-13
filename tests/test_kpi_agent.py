import pandas as pd
import numpy as np

from agents.kpi_agent import KPIAgent


class TestKPIAgent:
    def setup_method(self):
        self.agent = KPIAgent()

    def test_returns_correct_row_count(self):
        df = pd.DataFrame({"a": [1, 2, 3, 4, 5]})
        result = self.agent.generate_kpis(df)
        assert result["rows"] == 5

    def test_returns_correct_column_count(self):
        df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
        result = self.agent.generate_kpis(df)
        assert result["columns"] == 3

    def test_missing_values_count(self):
        df = pd.DataFrame({"a": [1, np.nan, 3], "b": [np.nan, 2, 3]})
        result = self.agent.generate_kpis(df)
        assert result["missing_values"] == 2

    def test_duplicate_rows_count(self):
        df = pd.DataFrame({"a": [1, 1, 2, 2, 3]})
        result = self.agent.generate_kpis(df)
        assert result["duplicate_rows"] == 2

    def test_statistics_for_numeric_columns(self):
        df = pd.DataFrame({"value": [10, 20, 30, 40, 50]})
        result = self.agent.generate_kpis(df)
        assert "statistics" in result
        stats = result["statistics"]
        assert "value" in stats
        val_stats = stats["value"]
        assert val_stats["mean"] == 30.0
        assert val_stats["min"] == 10.0
        assert val_stats["max"] == 50.0
        assert val_stats["count"] == 5.0

    def test_statistics_has_standard_keys(self):
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0]})
        result = self.agent.generate_kpis(df)
        stats = result["statistics"]["a"]
        expected_keys = {"count", "mean", "std", "min", "25%", "50%", "75%", "max"}
        assert expected_keys.issubset(stats.keys())

    def test_empty_statistics_when_no_numeric_columns(self):
        df = pd.DataFrame({"name": ["Alice", "Bob"], "city": ["London", "Paris"]})
        result = self.agent.generate_kpis(df)
        assert result["statistics"] == {}

    def test_kpis_contains_all_expected_keys(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = self.agent.generate_kpis(df)
        assert set(result.keys()) == {"rows", "columns", "missing_values", "duplicate_rows", "statistics"}

    def test_with_empty_dataframe(self):
        df = pd.DataFrame()
        result = self.agent.generate_kpis(df)
        assert result["rows"] == 0
        assert result["columns"] == 0

    def test_statistics_with_multiple_numeric_columns(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        result = self.agent.generate_kpis(df)
        assert "x" in result["statistics"]
        assert "y" in result["statistics"]
