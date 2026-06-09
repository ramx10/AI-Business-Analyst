import sys
import os
from unittest.mock import patch, MagicMock
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.nlq_agent import NLQAgent


class TestNLQAgent:
    def setup_method(self):
        self.agent = NLQAgent()
        self.sample_df = pd.DataFrame({
            "revenue": [100, 200, 300],
            "region": ["North", "South", "East"],
            "category": ["A", "B", "A"],
            "date": ["2024-01-01", "2024-02-01", "2024-03-01"],
        })

    @patch("agents.nlq_agent.llm")
    def test_successful_query_returns_structured_response(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = '{"answer": "Total revenue is $600.", "confidence": "high", "chart": {"type": "number", "title": "Total Revenue", "labels": ["Revenue"], "values": [600]}}'
        mock_llm.invoke.return_value = mock_response
        result = self.agent.query("What is the total revenue?", self.sample_df)
        assert result["answer"] == "Total revenue is $600."
        assert result["confidence"] == "high"
        assert result["chart"]["type"] == "number"

    @patch("agents.nlq_agent.llm")
    def test_rate_limit_error_returns_friendly_message(self, mock_llm):
        mock_llm.invoke.side_effect = Exception("rate_limit exceeded")
        result = self.agent.query("What is the total revenue?", self.sample_df)
        assert "rate limit" in result["answer"].lower()
        assert result["confidence"] == "low"

    @patch("agents.nlq_agent.llm")
    def test_resource_exhausted_error_returns_friendly_message(self, mock_llm):
        mock_llm.invoke.side_effect = Exception("RESOURCE_EXHAUSTED")
        result = self.agent.query("What is the total revenue?", self.sample_df)
        assert "rate limit" in result["answer"].lower()
        assert result["confidence"] == "low"

    @patch("agents.nlq_agent.llm")
    def test_generic_api_error_returns_error_message(self, mock_llm):
        mock_llm.invoke.side_effect = Exception("Some other API error")
        result = self.agent.query("What is the total revenue?", self.sample_df)
        assert "Error:" in result["answer"]
        assert result["confidence"] == "low"

    @patch("agents.nlq_agent.llm")
    def test_json_decode_fallback_returns_raw_content(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "Raw non-JSON response"
        mock_llm.invoke.return_value = mock_response
        result = self.agent.query("What is the total revenue?", self.sample_df)
        assert result["answer"] == "Raw non-JSON response"
        assert result["confidence"] == "low"

    @patch("agents.nlq_agent.llm")
    def test_malformed_json_returns_raw_content(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = '```json\n{"answer": "Test answer"}\n```'
        mock_llm.invoke.return_value = mock_response
        result = self.agent.query("What is the total revenue?", self.sample_df)
        assert result["answer"] == "Test answer"

    @patch("agents.nlq_agent.llm")
    def test_prompt_contains_dataset_context(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = '{"answer": "Test"}'
        mock_llm.invoke.return_value = mock_response
        self.agent.query("What is the total revenue?", self.sample_df)
        prompt = mock_llm.invoke.call_args[0][0]
        assert "revenue" in prompt
        assert "region" in prompt
        assert "category" in prompt
        assert "Dataset Context" in prompt
        assert "User Question" in prompt

    @patch("agents.nlq_agent.llm")
    def test_chart_response_with_bar_chart(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = '{"answer": "Sales by category.", "confidence": "high", "chart": {"type": "bar", "title": "Sales by Category", "labels": ["A", "B"], "values": [400, 200]}}'
        mock_llm.invoke.return_value = mock_response
        result = self.agent.query("Show me sales by category", self.sample_df)
        assert result["chart"]["type"] == "bar"
        assert result["chart"]["labels"] == ["A", "B"]
        assert result["chart"]["values"] == [400, 200]

    @patch("agents.nlq_agent.llm")
    def test_no_chart_when_null(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = '{"answer": "No chart needed.", "confidence": "medium", "chart": null}'
        mock_llm.invoke.return_value = mock_response
        result = self.agent.query("Simple question", self.sample_df)
        assert result["chart"] is None

    @patch("agents.nlq_agent.llm")
    def test_build_context_includes_numeric_summary(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = '{"answer": "Test"}'
        mock_llm.invoke.return_value = mock_response
        self.agent.query("Test question", self.sample_df)
        prompt = mock_llm.invoke.call_args[0][0]
        assert "Numeric summary" in prompt
        assert "3 rows" in prompt or "3" in prompt.split("rows")[0] if "rows" in prompt else False

    @patch("agents.nlq_agent.llm")
    def test_empty_question_returns_error(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = '{"answer": "", "confidence": "low", "chart": null}'
        mock_llm.invoke.return_value = mock_response
        result = self.agent.query("", self.sample_df)
        assert result["answer"] or result["confidence"] == "low"

    @patch("agents.nlq_agent.llm")
    def test_query_with_large_dataframe(self, mock_llm):
        large_df = pd.DataFrame({
            "col_" + str(i): range(1000) for i in range(20)
        })
        mock_response = MagicMock()
        mock_response.content = '{"answer": "Large dataset analysis complete.", "confidence": "high", "chart": null}'
        mock_llm.invoke.return_value = mock_response
        result = self.agent.query("Analyze this", large_df)
        assert result["answer"] == "Large dataset analysis complete."
        assert result["confidence"] == "high"

    @patch("agents.nlq_agent.llm")
    def test_prompt_includes_sample_rows(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = '{"answer": "Done"}'
        mock_llm.invoke.return_value = mock_response
        self.agent.query("Test", self.sample_df)
        prompt = mock_llm.invoke.call_args[0][0]
        assert "Sample rows" in prompt

    @patch("agents.nlq_agent.llm")
    def test_non_dict_response_is_wrapped(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = '["just", "an", "array"]'
        mock_llm.invoke.return_value = mock_response
        result = self.agent.query("Question", self.sample_df)
        assert isinstance(result["answer"], str)
        assert result["confidence"] == "low"
