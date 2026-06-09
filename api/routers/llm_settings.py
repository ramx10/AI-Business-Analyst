import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from config.llm_manager import get_config, update_config, get_available_models, test_connection

router = APIRouter()


class LLMConfigRequest(BaseModel):
    provider: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None


@router.get("/llm/config")
async def get_llm_config():
    return get_config()


@router.post("/llm/config")
async def save_llm_config(req: LLMConfigRequest):
    try:
        update_config(provider=req.provider, api_key=req.api_key, model=req.model)
        return {"status": "saved", "config": get_config()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/llm/models")
async def llm_models(provider: str = Query(...)):
    models = get_available_models(provider)
    return {"provider": provider, "models": models}


@router.post("/llm/test")
async def test_llm(req: LLMConfigRequest):
    result = test_connection(provider=req.provider, api_key=req.api_key, model=req.model)
    return result
