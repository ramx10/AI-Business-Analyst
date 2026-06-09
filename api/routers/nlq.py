import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.session_store import load_df, session_exists
from agents.nlq_agent import NLQAgent

router = APIRouter()
nlq_agent = NLQAgent()


class QueryRequest(BaseModel):
    session_id: str
    question: str


@router.post("/query")
async def ask_question(req: QueryRequest):
    """Answer a natural language question about the dataset."""
    if not session_exists(req.session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        df = load_df(req.session_id)
        result = nlq_agent.query(req.question.strip(), df)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
