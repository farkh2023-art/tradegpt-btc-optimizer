"""Optimisation par grille — grid search sur les paramètres d'une stratégie."""
import itertools
from typing import Any

from app.core.logging import logger
from app.services.backtester import run_backtest


def _build_range(spec: dict) -> list:
    """Convertit une spec {min, max, step} en liste de valeurs."""
    start = spec["min"]
    stop  = spec["max"]
    step  = spec.get("step", 1)
    result = []
    v = start
    while v <= stop:
        result.append(round(v, 6))
        v += step
    return result or [start]


def run_optimization(
    template: str,
    param_ranges: dict[str, dict],
    initial_capital: float = 10_000.0,
    max_combinations: int = 200,
) -> list[dict[str, Any]]:
    """
    Exécute un grid search sur les plages de paramètres.

    param_ranges exemple:
        {
            "fast_length": {"min": 10, "max": 30, "step": 5},
            "slow_length": {"min": 40, "max": 80, "step": 10},
        }

    Retourne les 10 meilleures combinaisons triées par rendement décroissant.
    """
    param_names  = list(param_ranges.keys())
    param_values = [_build_range(param_ranges[n]) for n in param_names]

    all_combos = list(itertools.product(*param_values))

    # Limiter le nombre de combinaisons pour le MVP
    if len(all_combos) > max_combinations:
        import random
        random.seed(42)
        all_combos = random.sample(all_combos, max_combinations)

    logger.info("Optimisation %s : %d combinaisons à tester", template, len(all_combos))

    results = []
    for combo in all_combos:
        params = dict(zip(param_names, combo))
        try:
            metrics = run_backtest(template, params, initial_capital)
            results.append({"params": params, **metrics})
        except Exception as exc:
            logger.debug("Combinaison ignorée %s : %s", params, exc)

    results.sort(key=lambda r: r.get("return_pct", -9999), reverse=True)
    return results[:10]
