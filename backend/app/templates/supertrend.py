def generate(
    atr_period: int = 10,
    factor: float = 3.0,
    stop_loss_pct: float = 2.0,
    take_profit_pct: float = 6.0,
    qty_pct: float = 10.0,
) -> str:
    return f"""//@version=5
// ============================================================
// Supertrend Strategy — TradeGPT BTC Optimizer
// SIMULATION UNIQUEMENT — Pas un conseil financier
// ============================================================
strategy("Supertrend Strategy", overlay=true,
         default_qty_type=strategy.percent_of_equity,
         default_qty_value={qty_pct},
         initial_capital=10000,
         commission_type=strategy.commission.percent,
         commission_value=0.1)

// ---- Paramètres ----
atr_period  = input.int({atr_period}, "Période ATR",    minval=1, maxval=50,   group="Supertrend")
factor      = input.float({factor},   "Facteur",        minval=0.5, maxval=10.0, step=0.1, group="Supertrend")
stop_loss   = input.float({stop_loss_pct},  "Stop Loss %",  minval=0.1, maxval=20.0, step=0.1, group="Gestion du risque")
take_profit = input.float({take_profit_pct}, "Take Profit %", minval=0.1, maxval=50.0, step=0.1, group="Gestion du risque")

// ---- Supertrend ----
[supertrend, direction] = ta.supertrend(factor, atr_period)

// ---- Signaux ----
long_signal  = direction < 0 and direction[1] >= 0
close_signal = direction > 0 and direction[1] <= 0

// ---- Entrées / Sorties ----
if long_signal
    strategy.entry("Long", strategy.long, comment="ST ↑")
    strategy.exit("Exit Long", "Long",
                  stop  = strategy.position_avg_price * (1 - stop_loss / 100),
                  limit = strategy.position_avg_price * (1 + take_profit / 100))

if close_signal
    strategy.close("Long", comment="ST ↓")

// ---- Affichage ----
st_color = direction < 0 ? color.new(color.green, 0) : color.new(color.red, 0)
plot(supertrend, "Supertrend", color=st_color, linewidth=2)

bgcolor(long_signal  ? color.new(color.green, 90) : na)
bgcolor(close_signal ? color.new(color.red,   90) : na)

// ---- Alertes ----
alertcondition(long_signal,  "ST — Achat", "Supertrend: Signal d'achat")
alertcondition(close_signal, "ST — Vente", "Supertrend: Signal de vente")
"""


PARAMS_SCHEMA = {
    "atr_period":    {"type": "int",   "default": 10,  "min": 1,   "max": 50,   "label": "Période ATR"},
    "factor":        {"type": "float", "default": 3.0, "min": 0.5, "max": 10.0, "label": "Facteur multiplicateur"},
    "stop_loss_pct":    {"type": "float", "default": 2.0, "min": 0.1, "max": 20.0, "label": "Stop Loss %"},
    "take_profit_pct":  {"type": "float", "default": 6.0, "min": 0.1, "max": 50.0, "label": "Take Profit %"},
}

INDICATORS = ["ATR", "Supertrend"]
DESCRIPTION = "Stratégie basée sur l'indicateur Supertrend. Suit la tendance et génère des signaux d'achat lorsque le prix passe au-dessus de la ligne Supertrend."
