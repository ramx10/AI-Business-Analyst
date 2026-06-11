from agents.schema_agent import SchemaAgent
from agents.cleaning_agent import DataCleaningAgent
from agents.kpi_agent import KPIAgent
from agents.ai_insight_agent import AIInsightAgent
from agents.report_agent import ReportAgent


class SupervisorAgent:

    def __init__(self):

        self.schema_agent = SchemaAgent()

        self.cleaning_agent = DataCleaningAgent()

        self.kpi_agent = KPIAgent()

        self.ai_insight_agent = AIInsightAgent()

        self.report_agent = ReportAgent()

    def run(self, df, mode="detailed"):

        # Step 1: Schema Analysis
        schema_info = self.schema_agent.analyze_schema(df)

        # Step 2: Data Cleaning Analysis
        cleaning_info = self.cleaning_agent.analyze_data_quality(df)

        # Step 3: KPI Generation
        kpi_info = self.kpi_agent.generate_kpis(df)

        # Step 4: AI Insights (Groq Call #1)
        insights = self.ai_insight_agent.generate_insights(
            schema_info,
            cleaning_info,
            kpi_info,
            mode=mode
        )

        # Step 5: Final Report (Groq Call #2)
        report = self.report_agent.generate_report(
            schema_info,
            cleaning_info,
            kpi_info,
            insights,
            mode=mode
        )

        return {
            "schema_info": schema_info,
            "cleaning_info": cleaning_info,
            "kpi_info": kpi_info,
            "insights": insights,
            "report": report
        }