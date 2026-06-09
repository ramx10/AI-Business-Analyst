import sys
import os
from unittest.mock import patch, MagicMock
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.ai_insight_agent import AIInsightAgent


class TestAIInsightAgent:
    def setup_method(self):
        self.agent = AIInsightAgent()

    def make_sample_inputs(self):
        schema_info = {"col1": {"datatype": "int64", "unique_values": 5}}
        cleaning_info = {"missing_values": 0, "duplicate_rows": 0}
        kpi_info = {"rows": 100, "columns": 1}
        return schema_info, cleaning_info, kpi_info

    @patch("agents.ai_insight_agent.llm")
    def test_rate_limit_error_returns_friendly_message(self, mock_llm):
        mock_llm.invoke.side_effect = Exception("rate_limit exceeded")
        schema_info, cleaning_info, kpi_info = self.make_sample_inputs()
        result = self.agent.generate_insights(schema_info, cleaning_info, kpi_info)
        assert "Rate Limit" in result

    @patch("agents.ai_insight_agent.llm")
    def test_resource_exhausted_error_returns_friendly_message(self, mock_llm):
        mock_llm.invoke.side_effect = Exception("RESOURCE_EXHAUSTED")
        schema_info, cleaning_info, kpi_info = self.make_sample_inputs()
        result = self.agent.generate_insights(schema_info, cleaning_info, kpi_info)
        assert "Rate Limit" in result

    @patch("agents.ai_insight_agent.llm")
    def test_generic_api_error_returns_error_message(self, mock_llm):
        mock_llm.invoke.side_effect = Exception("Some other API error")
        schema_info, cleaning_info, kpi_info = self.make_sample_inputs()
        result = self.agent.generate_insights(schema_info, cleaning_info, kpi_info)
        assert "Error:" in result

    @patch("agents.ai_insight_agent.llm")
    def test_successful_response_returns_content(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "Generated insights"
        mock_llm.invoke.return_value = mock_response
        schema_info, cleaning_info, kpi_info = self.make_sample_inputs()
        result = self.agent.generate_insights(schema_info, cleaning_info, kpi_info)
        assert result == "Generated insights"

    @patch("agents.ai_insight_agent.llm")
    def test_prompt_contains_dataset_summary(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "insights"
        mock_llm.invoke.return_value = mock_response
        schema_info, cleaning_info, kpi_info = self.make_sample_inputs()
        self.agent.generate_insights(schema_info, cleaning_info, kpi_info)
        prompt = mock_llm.invoke.call_args[0][0]
        assert "Dataset Summary" in prompt

    @patch("agents.ai_insight_agent.llm")
    def test_prompt_contains_all_sections(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "insights"
        mock_llm.invoke.return_value = mock_response
        schema_info, cleaning_info, kpi_info = self.make_sample_inputs()
        self.agent.generate_insights(schema_info, cleaning_info, kpi_info)
        prompt = mock_llm.invoke.call_args[0][0]
        for section in ["Key Business Insights", "Trends", "Risks", "Opportunities", "Recommendations"]:
            assert section in prompt

    @patch("agents.ai_insight_agent.llm")
    def test_prompt_includes_summary_numbers(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "insights"
        mock_llm.invoke.return_value = mock_response
        schema_info = {"a": {"datatype": "int64", "unique_values": 3}, "b": {"datatype": "object", "unique_values": 5}}
        cleaning_info = {"missing_values": 10, "duplicate_rows": 2}
        kpi_info = {"rows": 200, "columns": 2}
        self.agent.generate_insights(schema_info, cleaning_info, kpi_info)
        prompt = mock_llm.invoke.call_args[0][0]
        assert "'columns': 2" in prompt or "200" in prompt
