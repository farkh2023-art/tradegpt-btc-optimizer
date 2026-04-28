from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class RunBacktestRequest(BaseModel):
    strategy_id: int
    version_id: Optional[int] = None
    template: str = "sma"
    params: dict[str, Any] = {}
    initial_capital: float = 10000.0


class ImportBacktestRequest(BaseModel):
    strategy_id: int
    initial_capital: float
    final_capital: float
    return_pct: float
    num_trades: int
    win_rate: float
    max_drawdown: float
    profit_factor: float = 1.0


class BacktestOut(BaseModel):
    id: int
    strategy_id: int
    version_id: Optional[int]
    params: str
    initial_capital: float
    final_capital: float
    return_pct: float
    num_trades: int
    win_rate: float
    max_drawdown: float
    profit_factor: float
    sharpe_ratio: float
    source: str
    equity_curve: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CompareRequest(BaseModel):
    strategy_id_a: int
    version_id_a: Optional[int] = None
    strategy_id_b: int
    version_id_b: Optional[int] = None
    template: str = "sma"
    params_a: dict[str, Any] = {}
    params_b: dict[str, Any] = {}
    initial_capital: float = 10000.0
