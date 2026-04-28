from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class GenerateStrategyRequest(BaseModel):
    prompt: str
    template: Optional[str] = None
    risk_profile: str = "balanced"


class GenerateStrategyResponse(BaseModel):
    strategy_id: int
    name: str
    description: str
    pine_script: str
    parameters: dict
    explanation: str
    indicators: list[str]
    warning: str = "⚠️ Simulation uniquement — pas un conseil financier."


class StrategyOut(BaseModel):
    id: int
    name: str
    description: str
    template: Optional[str]
    risk_profile: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StrategyList(BaseModel):
    items: list[StrategyOut]
    total: int
