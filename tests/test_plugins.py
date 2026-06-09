import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pandas as pd
from utils.plugin_base import BasePlugin
from utils.plugin_manager import PluginManager, get_plugin_manager, PLUGIN_DIR


class TestPluginManager:
    def test_loads_plugins_from_directory(self):
        pm = PluginManager()
        plugins = pm.get_plugins()
        names = [p["name"] for p in plugins]
        assert "Sentiment Analyzer" in names

    def test_get_plugins_returns_metadata(self):
        pm = PluginManager()
        plugins = pm.get_plugins()
        assert len(plugins) > 0
        for p in plugins:
            assert "name" in p
            assert "version" in p
            assert "description" in p
            assert "category" in p

    def test_sentiment_plugin_metadata(self):
        pm = PluginManager()
        plugins = pm.get_plugins()
        sent = next(p for p in plugins if p["name"] == "Sentiment Analyzer")
        assert sent["version"] == "1.0.0"
        assert sent["category"] == "analysis"
        assert "sentiment" in sent["description"].lower()

    def test_run_plugin_with_valid_name_succeeds(self):
        pm = PluginManager()
        df = pd.DataFrame({"text": ["I love this product", "This is terrible"]})
        result = pm.run_plugin("Sentiment Analyzer", df)
        assert result["success"] is True
        assert "sentiment_score" in result["result"].columns
        assert result["summary"] != ""

    def test_run_plugin_with_invalid_name_returns_error(self):
        pm = PluginManager()
        df = pd.DataFrame({"a": [1]})
        result = pm.run_plugin("NonExistent", df)
        assert result["success"] is False
        assert "error" in result

    def test_run_plugin_returns_expected_keys(self):
        pm = PluginManager()
        df = pd.DataFrame({"text": ["good", "bad"]})
        result = pm.run_plugin("Sentiment Analyzer", df)
        assert "success" in result
        assert "result" in result
        assert "summary" in result

    def test_sentiment_plugin_analyzes_text(self):
        pm = PluginManager()
        df = pd.DataFrame({"review": ["good", "bad", "terrible", "amazing"]})
        result = pm.run_plugin("Sentiment Analyzer", df, column="review")
        assert result["success"] is True
        scores = result["result"]["sentiment_score"].tolist()
        assert scores == [1, -1, -1, 1]

    def test_sentiment_plugin_auto_detects_text_column(self):
        pm = PluginManager()
        df = pd.DataFrame({"num": [1, 2], "comment": ["great", "awful"]})
        result = pm.run_plugin("Sentiment Analyzer", df)
        assert result["success"] is True
        assert "sentiment_score" in result["result"].columns

    def test_sentiment_plugin_no_text_column_returns_error(self):
        pm = PluginManager()
        df = pd.DataFrame({"a": [1, 2], "b": [3.0, 4.0]})
        result = pm.run_plugin("Sentiment Analyzer", df)
        assert result["success"] is False
        assert "No text column found" in result["error"]

    def test_plugin_manager_singleton(self):
        pm1 = get_plugin_manager()
        pm2 = get_plugin_manager()
        assert pm1 is pm2

    def test_base_plugin_is_abstract(self):
        with pytest.raises(TypeError):
            BasePlugin()

    def test_reload_plugins(self):
        pm = PluginManager()
        before = len(pm.get_plugins())
        pm.reload()
        after = len(pm.get_plugins())
        assert before == after
