from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_provider import get_ai_provider
from app.services.pine_debugger import debug_script

router = APIRouter(prefix="/api/pine", tags=["ai"])


class DebugRequest(BaseModel):
    script: str


class RecommendRequest(BaseModel):
    metrics: dict
    params: dict
    template: str = "sma"


@router.post("/debug")
async def debug(req: DebugRequest):
    return await debug_script(req.script)


@router.post("/recommend")
async def recommend(req: RecommendRequest):
    provider = get_ai_provider()
    return await provider.get_recommendations(req.metrics, req.params, req.template)


@router.get("/status")
def ai_status():
    provider = get_ai_provider()
    return {
        "provider": provider.provider_name,
        "available": provider.is_available,
        "mode": "live" if provider.provider_name != "mock" else "mock",
    }
