import pytest
from app.services.optimizer import run_optimization, _build_range


def test_build_range_int():
    r = _build_range({"min": 10, "max": 30, "step": 10})
    assert r == [10, 20, 30]


def test_build_range_float():
    r = _build_range({"min": 1.0, "max": 3.0, "step": 1.0})
    assert len(r) == 3


def test_optimization_returns_results():
    results = run_optimization(
        "sma",
        {
            "fast_length": {"min": 10, "max": 20, "step": 10},
            "slow_length": {"min": 40, "max": 50, "step": 10},
        },
        initial_capital=10_000,
        max_combinations=10,
    )
    assert isinstance(results, list)
    assert len(results) <= 10
    for r in results:
        assert "return_pct" in r
        assert "params" in r


def test_optimization_sorted_by_return():
    results = run_optimization(
        "rsi",
        {
            "rsi_length": {"min": 10, "max": 20, "step": 5},
        },
        max_combinations=20,
    )
    returns = [r["return_pct"] for r in results]
    assert returns == sorted(returns, reverse=True)
