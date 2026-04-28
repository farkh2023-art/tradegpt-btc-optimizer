"""Backtester local simplifié — calcule les métriques à partir de données BTC réelles ou synthétiques."""
import json
import math
from typing import Any

import numpy as np
import pandas as pd

from app.core.logging import logger


# ---------------------------------------------------------------------------
# Données de prix
# ---------------------------------------------------------------------------

def _fetch_btc_data(period: str = "1y") -> pd.DataFrame:
    try:
        import yfinance as yf
        df = yf.download("BTC-USD", period=period, interval="1d", progress=False, auto_adjust=True)
        if df.empty:
            raise ValueError("Données vides")
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        logger.info("Données BTC chargées via yfinance (%d barres)", len(df))
        return df
    except Exception as exc:
        logger.warning("yfinance indisponible (%s) — données synthétiques utilisées", exc)
        return _synthetic_btc_data()


def _synthetic_btc_data(n: int = 365, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.now(), periods=n, freq="D")
    price = 45_000.0
    closes = [price]
    for _ in range(n - 1):
        price *= 1 + rng.normal(0.0003, 0.025)
        closes.append(max(price, 1.0))
    closes = np.array(closes)
    highs  = closes * (1 + np.abs(rng.normal(0, 0.008, n)))
    lows   = closes * (1 - np.abs(rng.normal(0, 0.008, n)))
    opens  = np.roll(closes, 1)
    opens[0] = closes[0]
    return pd.DataFrame({"Open": opens, "High": highs, "Low": lows, "Close": closes,
                         "Volume": rng.integers(5_000_000, 50_000_000, n)}, index=dates)


# ---------------------------------------------------------------------------
# Indicateurs
# ---------------------------------------------------------------------------

def _sma(series: pd.Series, n: int) -> pd.Series:
    return series.rolling(n).mean()


def _rsi(series: pd.Series, n: int = 14) -> pd.Series:
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(n).mean()
    loss  = (-delta.clip(upper=0)).rolling(n).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _adx(df: pd.DataFrame, n: int = 14) -> tuple[pd.Series, pd.Series, pd.Series]:
    high, low, close = df["High"], df["Low"], df["Close"]
    tr = pd.concat([high - low,
                    (high - close.shift()).abs(),
                    (low  - close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(n).mean()
    dm_plus  = (high - high.shift()).clip(lower=0)
    dm_minus = (low.shift() - low).clip(lower=0)
    dm_plus  = dm_plus.where(dm_plus > dm_minus, 0)
    dm_minus = dm_minus.where(dm_minus > dm_plus, 0)
    di_plus  = 100 * dm_plus.rolling(n).mean() / atr
    di_minus = 100 * dm_minus.rolling(n).mean() / atr
    dx       = (100 * (di_plus - di_minus).abs() / (di_plus + di_minus).replace(0, np.nan)).fillna(0)
    adx_val  = dx.rolling(n).mean()
    return di_plus, di_minus, adx_val


def _supertrend(df: pd.DataFrame, factor: float = 3.0, atr_period: int = 10) -> pd.Series:
    close = df["Close"]
    high  = df["High"]
    low   = df["Low"]
    tr    = pd.concat([high - low,
                       (high - close.shift()).abs(),
                       (low  - close.shift()).abs()], axis=1).max(axis=1)
    atr   = tr.rolling(atr_period).mean()
    hl2   = (high + low) / 2
    upper = hl2 + factor * atr
    lower = hl2 - factor * atr
    direction = pd.Series(1, index=df.index)
    for i in range(1, len(df)):
        if close.iloc[i] > upper.iloc[i - 1]:
            direction.iloc[i] = -1
        elif close.iloc[i] < lower.iloc[i - 1]:
            direction.iloc[i] = 1
        else:
            direction.iloc[i] = direction.iloc[i - 1]
    return direction


# ---------------------------------------------------------------------------
# Génération des signaux par template
# ---------------------------------------------------------------------------

def _signals_sma(df: pd.DataFrame, params: dict) -> pd.Series:
    fast = _sma(df["Close"], int(params.get("fast_length", 20)))
    slow = _sma(df["Close"], int(params.get("slow_length", 50)))
    return ((fast > slow) & (fast.shift() <= slow.shift())).astype(int)


def _signals_rsi(df: pd.DataFrame, params: dict) -> pd.Series:
    rsi = _rsi(df["Close"], int(params.get("rsi_length", 14)))
    oversold = float(params.get("oversold", 30))
    return ((rsi > oversold) & (rsi.shift() <= oversold)).astype(int)


def _signals_adx(df: pd.DataFrame, params: dict) -> pd.Series:
    di_plus, di_minus, adx = _adx(df, int(params.get("adx_length", 14)))
    threshold = float(params.get("adx_threshold", 25))
    cross = (di_plus > di_minus) & (di_plus.shift() <= di_minus.shift())
    return (cross & (adx > threshold)).astype(int)


def _signals_supertrend(df: pd.DataFrame, params: dict) -> pd.Series:
    direction = _supertrend(df, float(params.get("factor", 3.0)), int(params.get("atr_period", 10)))
    return ((direction == -1) & (direction.shift() == 1)).astype(int)


def _signals_combined(df: pd.DataFrame, params: dict) -> pd.Series:
    sma  = _sma(df["Close"], int(params.get("sma_length", 50)))
    rsi  = _rsi(df["Close"], int(params.get("rsi_length", 14)))
    _, _, adx_val = _adx(df, int(params.get("adx_length", 14)))
    oversold   = float(params.get("rsi_oversold", 40))
    adx_thresh = float(params.get("adx_threshold", 20))
    above_sma  = df["Close"] > sma
    rsi_cross  = (rsi > oversold) & (rsi.shift() <= oversold)
    adx_ok     = adx_val > adx_thresh
    return (above_sma & rsi_cross & adx_ok).astype(int)


_SIGNAL_FNS = {
    "sma": _signals_sma,
    "rsi": _signals_rsi,
    "adx": _signals_adx,
    "supertrend": _signals_supertrend,
    "combined": _signals_combined,
}


# ---------------------------------------------------------------------------
# Moteur de backtest
# ---------------------------------------------------------------------------

def run_backtest(template: str, params: dict[str, Any], initial_capital: float = 10_000.0) -> dict:
    df = _fetch_btc_data()
    signal_fn = _SIGNAL_FNS.get(template, _signals_sma)
    buy_signals = signal_fn(df, params)

    stop_loss_pct   = float(params.get("stop_loss_pct", 2.0))
    take_profit_pct = float(params.get("take_profit_pct", 4.0))

    capital     = initial_capital
    position    = 0.0
    entry_price = 0.0
    trades: list[dict] = []
    equity: list[float] = [capital]

    for i in range(1, len(df)):
        price = float(df["Close"].iloc[i])

        if position > 0:
            gain = (price - entry_price) / entry_price
            if gain <= -stop_loss_pct / 100 or gain >= take_profit_pct / 100:
                exit_value = position * price
                trades.append({
                    "entry": entry_price,
                    "exit": price,
                    "pnl": exit_value - position * entry_price,
                    "win": gain > 0,
                })
                capital  += exit_value
                position  = 0.0

        if position == 0 and buy_signals.iloc[i] == 1:
            qty = (capital * 0.99) / price  # 99 % du capital, simule frais
            position    = qty
            entry_price = price
            capital     = 0.0

        equity_val = capital + position * price
        equity.append(equity_val)

    # Fermer position ouverte en fin de période
    if position > 0:
        last_price = float(df["Close"].iloc[-1])
        capital += position * last_price
        position = 0.0

    equity[-1] = capital

    # Métriques
    num_trades  = len(trades)
    wins        = [t for t in trades if t["win"]]
    win_rate    = len(wins) / num_trades * 100 if num_trades else 0.0
    return_pct  = (capital - initial_capital) / initial_capital * 100

    gross_profit = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    gross_loss   = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else (1.0 if gross_profit == 0 else float("inf"))

    # Max drawdown
    eq_arr  = np.array(equity)
    peak    = np.maximum.accumulate(eq_arr)
    dd      = (peak - eq_arr) / peak
    max_dd  = float(dd.max()) * 100

    # Sharpe simplifié (daily returns)
    eq_series = pd.Series(equity)
    daily_ret = eq_series.pct_change().dropna()
    sharpe = float(daily_ret.mean() / daily_ret.std() * math.sqrt(252)) if daily_ret.std() > 0 else 0.0

    # Courbe d'équité (résumée à 100 points max pour l'API)
    step = max(1, len(equity) // 100)
    equity_curve = [
        {"date": str(df.index[min(i, len(df.index) - 1)].date()), "value": round(equity[i], 2)}
        for i in range(0, len(equity), step)
    ]

    return {
        "initial_capital": initial_capital,
        "final_capital":   round(capital, 2),
        "return_pct":      round(return_pct, 2),
        "num_trades":      num_trades,
        "win_rate":        round(win_rate, 2),
        "max_drawdown":    round(max_dd, 2),
        "profit_factor":   round(min(profit_factor, 99.0), 3),
        "sharpe_ratio":    round(sharpe, 3),
        "equity_curve":    json.dumps(equity_curve),
    }
