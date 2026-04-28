import pytest
from app.services.backtester import run_backtest, _synthetic_btc_data


def test_synthetic_data_shape():
    df = _synthetic_btc_data(n=100)
    assert len(df) == 100
    assert "Close" in df.columns
    assert "Open" in df.columns


def test_backtest_sma_returns_metrics():
    metrics = run_backtest("sma", {"fast_length": 10, "slow_length": 30}, initial_capital=10_000)
    assert "return_pct" in metrics
    assert "win_rate" in metrics
    assert "max_drawdown" in metrics
    assert "num_trades" in metrics
    assert "profit_factor" in metrics
    assert "sharpe_ratio" in metrics
    assert "equity_curve" in metrics
    assert metrics["initial_capital"] == 10_000


def test_backtest_rsi_returns_metrics():
    metrics = run_backtest("rsi", {"rsi_length": 14, "oversold": 30, "overbought": 70})
    assert isinstance(metrics["return_pct"], float)
    assert metrics["num_trades"] >= 0


def test_backtest_adx_returns_metrics():
    metrics = run_backtest("adx", {"adx_length": 14, "adx_threshold": 25})
    assert isinstance(metrics["win_rate"], float)


def test_backtest_combined_returns_metrics():
    metrics = run_backtest("combined", {
        "sma_length": 50,
        "rsi_length": 14,
        "rsi_oversold": 40,
        "adx_threshold": 20,
    })
    assert metrics["final_capital"] > 0


def test_equity_curve_is_json():
    import json
    metrics = run_backtest("sma", {})
    curve = json.loads(metrics["equity_curve"])
    assert isinstance(curve, list)
    if curve:
        assert "date" in curve[0]
        assert "value" in curve[0]
