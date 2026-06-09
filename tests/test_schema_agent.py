import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.schema_agent import SchemaAgent


class TestSchemaAgent:
    def setup_method(self):
        self.agent = SchemaAgent()

    def test_returns_correct_datatype_and_unique_counts(self):
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Alice"],
            "value": [10.5, 20.3, 30.1],
        })
        result = self.agent.analyze_schema(df)
        assert "int" in result["id"]["datatype"]
        assert result["id"]["unique_values"] == 3
        assert "str" in result["name"]["datatype"] or result["name"]["datatype"] == "object"
        assert result["name"]["unique_values"] == 2
        assert "float" in result["value"]["datatype"]
        assert result["value"]["unique_values"] == 3

    def test_with_numeric_columns(self):
        df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": [4.0, 5.0, 6.0],
        })
        result = self.agent.analyze_schema(df)
        assert result["a"]["datatype"] == "int64"
        assert result["b"]["datatype"] == "float64"

    def test_with_string_columns(self):
        df = pd.DataFrame({
            "city": ["London", "Paris", "Tokyo"],
            "country": ["UK", "France", "Japan"],
        })
        result = self.agent.analyze_schema(df)
        assert "str" in result["city"]["datatype"] or result["city"]["datatype"] == "object"
        assert "str" in result["country"]["datatype"] or result["country"]["datatype"] == "object"

    def test_with_datetime_column(self):
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
            "value": [100, 200, 300],
        })
        result = self.agent.analyze_schema(df)
        assert "datetime" in result["date"]["datatype"]
        assert result["date"]["unique_values"] == 3

    def test_with_mixed_column_types(self):
        df = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["x", "y", "z"],
            "bool_col": [True, False, True],
        })
        result = self.agent.analyze_schema(df)
        assert "int" in result["int_col"]["datatype"]
        assert "float" in result["float_col"]["datatype"]
        assert "str" in result["str_col"]["datatype"] or result["str_col"]["datatype"] == "object"
        assert "bool" in result["bool_col"]["datatype"]

    def test_with_empty_dataframe(self):
        df = pd.DataFrame()
        result = self.agent.analyze_schema(df)
        assert result == {}

    def test_schema_keys_per_column(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        result = self.agent.analyze_schema(df)
        assert "datatype" in result["x"]
        assert "unique_values" in result["x"]

    def test_all_nan_column_unique_count(self):
        df = pd.DataFrame({"a": [np.nan, np.nan, np.nan]})
        result = self.agent.analyze_schema(df)
        assert result["a"]["unique_values"] == 0
