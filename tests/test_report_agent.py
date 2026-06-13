from unittest.mock import patch, MagicMock
import pandas as pd

from agents.report_agent import ReportAgent


class TestReportAgent:
    def setup_method(self):
        self.agent = ReportAgent()

    def make_sample_inputs(self):
        schema_info = {"col1": {"datatype": "int64", "unique_values": 5}}
        cleaning_info = {"missing_values": 0, "duplicate_rows": 0}
        kpi_info = {"rows": 100, "columns": 5}
        insights = "Sample insights text"
        return schema_info, cleaning_info, kpi_info, insights

    @patch("agents.report_agent.llm")
    def test_rate_limit_error_returns_friendly_message(self, mock_llm):
        mock_llm.invoke.side_effect = Exception("rate_limit exceeded")
        schema_info, cleaning_info, kpi_info, insights = self.make_sample_inputs()
        result = self.agent.generate_report(schema_info, cleaning_info, kpi_info, insights)
        assert "Rate Limit" in result

    @patch("agents.report_agent.llm")
    def test_resource_exhausted_error_returns_friendly_message(self, mock_llm):
        mock_llm.invoke.side_effect = Exception("RESOURCE_EXHAUSTED")
        schema_info, cleaning_info, kpi_info, insights = self.make_sample_inputs()
        result = self.agent.generate_report(schema_info, cleaning_info, kpi_info, insights)
        assert "Rate Limit" in result

    @patch("agents.report_agent.llm")
    def test_generic_api_error_returns_error_message(self, mock_llm):
        mock_llm.invoke.side_effect = Exception("Some other API error")
        schema_info, cleaning_info, kpi_info, insights = self.make_sample_inputs()
        result = self.agent.generate_report(schema_info, cleaning_info, kpi_info, insights)
        assert "Error:" in result

    @patch("agents.report_agent.llm")
    def test_successful_response_returns_content(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "Generated report content"
        mock_llm.invoke.return_value = mock_response
        schema_info, cleaning_info, kpi_info, insights = self.make_sample_inputs()
        result = self.agent.generate_report(schema_info, cleaning_info, kpi_info, insights)
        assert result == "Generated report content"

    @patch("agents.report_agent.llm")
    def test_prompt_contains_insights_section(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "report"
        mock_llm.invoke.return_value = mock_response
        schema_info, cleaning_info, kpi_info, insights = self.make_sample_inputs()
        self.agent.generate_report(schema_info, cleaning_info, kpi_info, insights)
        prompt = mock_llm.invoke.call_args[0][0]
        assert "Insights:" in prompt

    @patch("agents.report_agent.llm")
    def test_prompt_contains_summary_sections(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "report"
        mock_llm.invoke.return_value = mock_response
        schema_info, cleaning_info, kpi_info, insights = self.make_sample_inputs()
        self.agent.generate_report(schema_info, cleaning_info, kpi_info, insights, mode="summary")
        prompt = mock_llm.invoke.call_args[0][0]
        for section in ["EXECUTIVE SUMMARY", "KEY METRICS", "TOP FINDINGS", "RECOMMENDATIONS"]:
            assert section in prompt

    @patch("agents.report_agent.llm")
    def test_prompt_contains_detailed_sections(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "report"
        mock_llm.invoke.return_value = mock_response
        schema_info, cleaning_info, kpi_info, insights = self.make_sample_inputs()
        self.agent.generate_report(schema_info, cleaning_info, kpi_info, insights, mode="detailed")
        prompt = mock_llm.invoke.call_args[0][0]
        for section in ["EXECUTIVE SUMMARY", "DATASET OVERVIEW", "KEY FINDINGS", "RISKS & CHALLENGES", "STRATEGIC RECOMMENDATIONS", "CONCLUSION"]:
            assert section in prompt

    @patch("agents.report_agent.llm")
    def test_insights_text_included_in_prompt(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "report"
        mock_llm.invoke.return_value = mock_response
        schema_info, cleaning_info, kpi_info, _ = self.make_sample_inputs()
        self.agent.generate_report(schema_info, cleaning_info, kpi_info, "Custom insight text here")
        prompt = mock_llm.invoke.call_args[0][0]
        assert "Custom insight text here" in prompt
