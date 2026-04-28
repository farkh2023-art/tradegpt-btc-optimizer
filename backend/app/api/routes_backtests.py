import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.backtest import Backtest
from app.schemas.backtest import RunBacktestRequest, ImportBacktestRequest, BacktestOut, CompareRequest
from app.services.backtester import run_backtest

router = APIRouter(prefix="/api/backtests", tags=["backtests"])


@router.post("/run", response_model=BacktestOut)
def run(req: RunBacktestRequest, db: Session = Depends(get_db)):
    try:
        metrics = run_backtest(req.template, req.params, req.initial_capital)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur backtest : {exc}")

    bt = Backtest(
        strategy_id=req.strategy_id,
        version_id=req.version_id,
        params=json.dumps(req.params),
        source="local",
        **{k: v for k, v in metrics.items() if k != "equity_curve"},
        equity_curve=metrics["equity_curve"],
    )
    db.add(bt)
    db.commit()
    db.refresh(bt)
    return BacktestOut.model_validate(bt)


@router.post("/import", response_model=BacktestOut)
def import_bt(req: ImportBacktestRequest, db: Session = Depends(get_db)):
    bt = Backtest(
        strategy_id=req.strategy_id,
        initial_capital=req.initial_capital,
        final_capital=req.final_capital,
        return_pct=req.return_pct,
        num_trades=req.num_trades,
        win_rate=req.win_rate,
        max_drawdown=req.max_drawdown,
        profit_factor=req.profit_factor,
        source="tradingview_import",
        equity_curve="[]",
    )
    db.add(bt)
    db.commit()
    db.refresh(bt)
    return BacktestOut.model_validate(bt)


@router.get("/strategy/{strategy_id}", response_model=list[BacktestOut])
def list_backtests(strategy_id: int, db: Session = Depends(get_db)):
    bts = db.query(Backtest).filter(
        Backtest.strategy_id == strategy_id
    ).order_by(Backtest.created_at.desc()).all()
    return [BacktestOut.model_validate(b) for b in bts]


@router.get("/{bt_id}", response_model=BacktestOut)
def get_backtest(bt_id: int, db: Session = Depends(get_db)):
    bt = db.query(Backtest).filter(Backtest.id == bt_id).first()
    if not bt:
        raise HTTPException(status_code=404, detail="Backtest introuvable")
    return BacktestOut.model_validate(bt)


@router.post("/compare")
def compare(req: CompareRequest, db: Session = Depends(get_db)):
    try:
        metrics_a = run_backtest(req.template, req.params_a, req.initial_capital)
        metrics_b = run_backtest(req.template, req.params_b, req.initial_capital)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur comparaison : {exc}")

    # Déterminer le gagnant
    score_a = (
        metrics_a["return_pct"] * 0.4
        + metrics_a["win_rate"]  * 0.3
        - metrics_a["max_drawdown"] * 0.3
    )
    score_b = (
        metrics_b["return_pct"] * 0.4
        + metrics_b["win_rate"]  * 0.3
        - metrics_b["max_drawdown"] * 0.3
    )

    winner = "A" if score_a >= score_b else "B"
    justification = (
        f"Variante {winner} recommandée : "
        f"rendement {metrics_a['return_pct']:+.1f} % vs {metrics_b['return_pct']:+.1f} %, "
        f"win rate {metrics_a['win_rate']:.1f} % vs {metrics_b['win_rate']:.1f} %, "
        f"drawdown {metrics_a['max_drawdown']:.1f} % vs {metrics_b['max_drawdown']:.1f} %."
    )

    return {
        "strategy_a": {"strategy_id": req.strategy_id_a, "params": req.params_a, "metrics": metrics_a},
        "strategy_b": {"strategy_id": req.strategy_id_b, "params": req.params_b, "metrics": metrics_b},
        "winner": winner,
        "justification": justification,
    }
