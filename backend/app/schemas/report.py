from datetime import datetime
from pydantic import BaseModel


class GenerateReportRequest(BaseModel):
    strategy_id: int
    backtest_id: int | None = None


class ReportOut(BaseModel):
    id: int
    strategy_id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
