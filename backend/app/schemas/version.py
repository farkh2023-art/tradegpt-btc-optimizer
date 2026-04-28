from datetime import datetime
from typing import Any
from pydantic import BaseModel


class CreateVersionRequest(BaseModel):
    pine_script: str
    parameters: dict[str, Any] = {}
    explanation: str = ""


class VersionOut(BaseModel):
    id: int
    strategy_id: int
    version_number: int
    pine_script: str
    parameters: str
    explanation: str
    is_current: bool
    created_at: datetime

    model_config = {"from_attributes": True}
