from unittest.mock import patch, MagicMock
import pandas as pd

from agents.supervisor_agent import SupervisorAgent


class TestSupervisorAgent:
    def setup_method(self):
        self.agent = SupervisorAgent()

    @patch("agents.supervisor_agent.AIInsightAgent.generate_insights")
    @patch("agents.supervisor_agent.ReportAgent.generate_report")
    def test_run_returns_all_expected_keys(
        self, mock_generate_report, mock_generate_insights
    ):
        mock_generate_insights.return_value = "Sample insights"
        mock_generate_report.return_value = "Sample report"

        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [10.0, 20.0, 30.0],
        })

        result = self.agent.run(df)

        assert "schema_info" in result
        assert "cleaning_info" in result
        assert "kpi_info" in result
        assert "insights" in result
        assert "report" in result

    @patch("agents.supervisor_agent.AIInsightAgent.generate_insights")
    @patch("agents.supervisor_agent.ReportAgent.generate_report")
    def test_run_schema_info_is_dict(
        self, mock_generate_report, mock_generate_insights
    ):
        mock_generate_insights.return_value = "insights"
        mock_generate_report.return_value = "report"
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = self.agent.run(df)
        assert isinstance(result["schema_info"], dict)
        assert "a" in result["schema_info"]

    @patch("agents.supervisor_agent.AIInsightAgent.generate_insights")
    @patch("agents.supervisor_agent.ReportAgent.generate_report")
    def test_run_cleaning_info_has_expected_keys(
        self, mock_generate_report, mock_generate_insights
    ):
        mock_generate_insights.return_value = "insights"
        mock_generate_report.return_value = "report"
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = self.agent.run(df)
        assert "total_rows" in result["cleaning_info"]
        assert "missing_values" in result["cleaning_info"]
        assert "duplicate_rows" in result["cleaning_info"]

    @patch("agents.supervisor_agent.AIInsightAgent.generate_insights")
    @patch("agents.supervisor_agent.ReportAgent.generate_report")
    def test_run_kpi_info_has_expected_keys(
        self, mock_generate_report, mock_generate_insights
    ):
        mock_generate_insights.return_value = "insights"
        mock_generate_report.return_value = "report"
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = self.agent.run(df)
        assert "rows" in result["kpi_info"]
        assert "columns" in result["kpi_info"]

    @patch("agents.supervisor_agent.AIInsightAgent.generate_insights")
    @patch("agents.supervisor_agent.ReportAgent.generate_report")
    def test_run_insights_and_report_are_strings(
        self, mock_generate_report, mock_generate_insights
    ):
        mock_generate_insights.return_value = "Mocked insights text"
        mock_generate_report.return_value = "Mocked report text"
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = self.agent.run(df)
        assert isinstance(result["insights"], str)
        assert isinstance(result["report"], str)
        assert result["insights"] == "Mocked insights text"
        assert result["report"] == "Mocked report text"

    @patch("agents.supervisor_agent.AIInsightAgent.generate_insights")
    @patch("agents.supervisor_agent.ReportAgent.generate_report")
    def test_run_passes_schema_to_insight_agent(
        self, mock_generate_report, mock_generate_insights
    ):
        mock_generate_insights.return_value = "insights"
        mock_generate_report.return_value = "report"
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        self.agent.run(df)
        args, _ = mock_generate_insights.call_args
        schema_arg = args[0]
        assert "a" in schema_arg
        assert "b" in schema_arg
