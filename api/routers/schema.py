from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from api.session_store import load_df, session_exists
from agents.schema_agent import SchemaAgent

router = APIRouter()
agent = SchemaAgent()


@router.get("/schema")
async def get_schema(session_id: str = Query(...)):
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found. Please upload a dataset first.")
    try:
        df = load_df(session_id)
        schema_info = agent.analyze_schema(df)

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

        numeric_stats = df[numeric_cols].describe().round(2).fillna(0).to_dict() if numeric_cols else {}
        cat_stats = df[categorical_cols].describe(include="object").fillna("").to_dict() if categorical_cols else {}

        return JSONResponse({
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "schema": schema_info,
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "numeric_stats": numeric_stats,
            "categorical_stats": cat_stats,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
