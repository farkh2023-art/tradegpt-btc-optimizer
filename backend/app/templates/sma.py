def generate(
    fast_length: int = 20,
    slow_length: int = 50,
    stop_loss_pct: float = 2.0,
    take_profit_pct: float = 4.0,
    qty_pct: float = 10.0,
) -> str:
    return f"""//@version=5
// ============================================================
// SMA Cross Strategy — TradeGPT BTC Optimizer
// SIMULATION UNIQUEMENT — Pas un conseil financier
// ============================================================
strategy("SMA Cross Strategy", overlay=true,
         default_qty_type=strategy.percent_of_equity,
         default_qty_value={qty_pct},
         initial_capital=10000,
         commission_type=strategy.commission.percent,
         commission_value=0.1)

// ---- Paramètres ----
fast_length = input.int({fast_length}, "Période SMA rapide", minval=1, maxval=200, group="Indicateurs")
slow_length = input.int({slow_length}, "Période SMA lente",  minval=1, maxval=500, group="Indicateurs")
stop_loss   = input.float({stop_loss_pct}, "Stop Loss %",    minval=0.1, maxval=20.0, step=0.1, group="Gestion du risque")
take_profit = input.float({take_profit_pct}, "Take Profit %", minval=0.1, maxval=50.0, step=0.1, group="Gestion du risque")

// ---- Indicateurs ----
fast_sma = ta.sma(close, fast_length)
slow_sma = ta.sma(close, slow_length)

// ---- Signaux ----
long_signal  = ta.crossover(fast_sma, slow_sma)
close_signal = ta.crossunder(fast_sma, slow_sma)

// ---- Entrées / Sorties ----
if long_signal
    strategy.entry("Long", strategy.long, comment="SMA Cross ↑")
    strategy.exit("Exit Long", "Long",
                  stop  = strategy.position_avg_price * (1 - stop_loss / 100),
                  limit = strategy.position_avg_price * (1 + take_profit / 100))

if close_signal
    strategy.close("Long", comment="SMA Cross ↓")

// ---- Affichage ----
plot(fast_sma, "SMA Rapide", color=color.new(color.blue,   0), linewidth=2)
plot(slow_sma, "SMA Lente",  color=color.new(color.orange, 0), linewidth=2)

bgcolor(long_signal  ? color.new(color.green, 90) : na, title="Signal achat")
bgcolor(close_signal ? color.new(color.red,   90) : na, title="Signal vente")

// ---- Alertes ----
alertcondition(long_signal,  "SMA — Achat",  "SMA Cross: Signal d'achat détecté")
alertcondition(close_signal, "SMA — Vente",  "SMA Cross: Signal de vente détecté")
"""


PARAMS_SCHEMA = {
    "fast_length": {"type": "int",   "default": 20,  "min": 1,   "max": 200,  "label": "Période SMA rapide"},
    "slow_length": {"type": "int",   "default": 50,  "min": 1,   "max": 500,  "label": "Période SMA lente"},
    "stop_loss_pct":    {"type": "float", "default": 2.0, "min": 0.1, "max": 20.0, "label": "Stop Loss %"},
    "take_profit_pct":  {"type": "float", "default": 4.0, "min": 0.1, "max": 50.0, "label": "Take Profit %"},
}

INDICATORS = ["SMA"]
DESCRIPTION = "Stratégie de croisement de moyennes mobiles simples. Achat quand la SMA rapide croise au-dessus de la SMA lente, vente en cas de croisement inverse."
