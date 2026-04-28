from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from app.services.optimizer import run_optimization

router = APIRouter(prefix="/api/optimization", tags=["optimization"])


class OptimizeRequest(BaseModel):
    template: str = "sma"
    param_ranges: dict[str, dict]
    initial_capital: float = 10_000.0
    max_combinations: int = 100


@router.post("/run")
def optimize(req: OptimizeRequest):
    if req.max_combinations > 500:
        raise HTTPException(status_code=400, detail="max_combinations ne peut pas dépasser 500.")
    try:
        results = run_optimization(
            req.template,
            req.param_ranges,
            req.initial_capital,
            req.max_combinations,
        )
        return {"template": req.template, "results": results, "total_tested": req.max_combinations}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur optimisation : {exc}")
