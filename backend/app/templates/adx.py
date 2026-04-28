def generate(
    adx_length: int = 14,
    adx_threshold: int = 25,
    di_length: int = 14,
    stop_loss_pct: float = 2.5,
    take_profit_pct: float = 5.0,
    qty_pct: float = 10.0,
) -> str:
    return f"""//@version=5
// ============================================================
// ADX Trend Filter Strategy — TradeGPT BTC Optimizer
// SIMULATION UNIQUEMENT — Pas un conseil financier
// ============================================================
strategy("ADX Trend Filter Strategy", overlay=true,
         default_qty_type=strategy.percent_of_equity,
         default_qty_value={qty_pct},
         initial_capital=10000,
         commission_type=strategy.commission.percent,
         commission_value=0.1)

// ---- Paramètres ----
adx_length    = input.int({adx_length},    "Période ADX",       minval=1, maxval=50,  group="ADX")
di_length     = input.int({di_length},     "Période DI",        minval=1, maxval=50,  group="ADX")
adx_threshold = input.int({adx_threshold}, "Seuil ADX (force)", minval=10, maxval=60, group="ADX")
stop_loss     = input.float({stop_loss_pct},   "Stop Loss %",   minval=0.1, maxval=20.0, step=0.1, group="Gestion du risque")
take_profit   = input.float({take_profit_pct}, "Take Profit %", minval=0.1, maxval=50.0, step=0.1, group="Gestion du risque")

// ---- ADX + DI ----
[diplus, diminus, adx] = ta.dmi(di_length, adx_length)

// ---- Signaux ----
trend_strong = adx > adx_threshold
long_signal  = trend_strong and ta.crossover(diplus, diminus)
close_signal = ta.crossunder(diplus, diminus)

// ---- Entrées / Sorties ----
if long_signal
    strategy.entry("Long", strategy.long, comment="ADX ↑")
    strategy.exit("Exit Long", "Long",
                  stop  = strategy.position_avg_price * (1 - stop_loss / 100),
                  limit = strategy.position_avg_price * (1 + take_profit / 100))

if close_signal
    strategy.close("Long", comment="DI- > DI+")

// ---- Affichage ----
plot(diplus,  "+DI", color=color.green, linewidth=1)
plot(diminus, "-DI", color=color.red,   linewidth=1)
hline(adx_threshold, "Seuil ADX", color=color.gray, linestyle=hline.style_dashed)

// ---- Alertes ----
alertcondition(long_signal,  "ADX — Achat", "ADX: Tendance forte + DI+ > DI-")
alertcondition(close_signal, "ADX — Vente", "ADX: DI- repasse au-dessus de DI+")
"""


PARAMS_SCHEMA = {
    "adx_length":    {"type": "int", "default": 14, "min": 1,  "max": 50,  "label": "Période ADX"},
    "di_length":     {"type": "int", "default": 14, "min": 1,  "max": 50,  "label": "Période DI"},
    "adx_threshold": {"type": "int", "default": 25, "min": 10, "max": 60,  "label": "Seuil ADX (force de tendance)"},
    "stop_loss_pct":    {"type": "float", "default": 2.5, "min": 0.1, "max": 20.0, "label": "Stop Loss %"},
    "take_profit_pct":  {"type": "float", "default": 5.0, "min": 0.1, "max": 50.0, "label": "Take Profit %"},
}

INDICATORS = ["ADX", "DI+", "DI-"]
DESCRIPTION = "Stratégie utilisant l'ADX comme filtre de tendance. Les trades ne sont pris qu'en tendance forte (ADX > seuil), avec croisement DI+ / DI- pour le timing."
