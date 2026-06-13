from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from api.session_store import load_df, session_exists
from agents.schema_agent import SchemaAgent
from agents.cleaning_agent import DataCleaningAgent
from agents.kpi_agent import KPIAgent
from agents.ai_insight_agent import AIInsightAgent

router = APIRouter()


@router.get("/insights")
async def get_insights(session_id: str = Query(...)):
    """Run the AI insight pipeline and return markdown text."""
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        df = load_df(session_id)

        schema_info = SchemaAgent().analyze_schema(df)
        cleaning_info = DataCleaningAgent().analyze_data_quality(df)
        kpi_info = KPIAgent().generate_kpis(df)

        insights = AIInsightAgent().generate_insights(schema_info, cleaning_info, kpi_info)

        if insights.startswith("Error:") or "Limit Exceeded" in insights:
            raise HTTPException(status_code=503, detail=insights)

        return JSONResponse({"insights": insights})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
