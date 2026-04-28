from pydantic import BaseModel
from typing import Optional


class EtoroStatus(BaseModel):
    enabled: bool
    mode: str
    connected: bool
    allow_real_orders: bool
    mock: bool


class EtoroPosition(BaseModel):
    symbol: str
    name: str
    weight_pct: float
    performance_pct: float
    invested: float
    current_value: float
    buy_price: Optional[float] = None
    sell_price: Optional[float] = None
    is_crypto: bool = False


class EtoroPortfolio(BaseModel):
    total_value: float
    cash: float
    invested: float
    performance_pct: float
    btc_exposure_pct: float
    concentration_score: float
    currency: str = "USD"
    positions: list[EtoroPosition]


class EtoroAnalyzeRequest(BaseModel):
    focus: str = "btc"


class EtoroAnalysis(BaseModel):
    btc_exposure_pct: float
    concentration_score: float
    recommendations: list[str]
    risk_level: str
    summary: str
    disclaimer: str
