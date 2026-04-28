def generate(
    rsi_length: int = 14,
    oversold: int = 30,
    overbought: int = 70,
    stop_loss_pct: float = 3.0,
    take_profit_pct: float = 5.0,
    qty_pct: float = 10.0,
) -> str:
    return f"""//@version=5
// ============================================================
// RSI Reversal Strategy — TradeGPT BTC Optimizer
// SIMULATION UNIQUEMENT — Pas un conseil financier
// ============================================================
strategy("RSI Reversal Strategy", overlay=false,
         default_qty_type=strategy.percent_of_equity,
         default_qty_value={qty_pct},
         initial_capital=10000,
         commission_type=strategy.commission.percent,
         commission_value=0.1)

// ---- Paramètres ----
rsi_length  = input.int({rsi_length},  "Période RSI",       minval=1, maxval=100, group="RSI")
oversold    = input.int({oversold},    "Niveau survente",   minval=1, maxval=50,  group="RSI")
overbought  = input.int({overbought},  "Niveau surachat",   minval=50, maxval=99, group="RSI")
stop_loss   = input.float({stop_loss_pct},   "Stop Loss %",   minval=0.1, maxval=20.0, step=0.1, group="Gestion du risque")
take_profit = input.float({take_profit_pct}, "Take Profit %", minval=0.1, maxval=50.0, step=0.1, group="Gestion du risque")

// ---- RSI ----
rsi = ta.rsi(close, rsi_length)

// ---- Signaux ----
long_signal  = ta.crossover(rsi, oversold)
close_signal = ta.crossunder(rsi, overbought)

// ---- Entrées / Sorties ----
if long_signal
    strategy.entry("Long", strategy.long, comment="RSI survente ↑")
    strategy.exit("Exit Long", "Long",
                  stop  = strategy.position_avg_price * (1 - stop_loss / 100),
                  limit = strategy.position_avg_price * (1 + take_profit / 100))

if close_signal
    strategy.close("Long", comment="RSI surachat ↓")

// ---- Affichage ----
hline(oversold,    "Survente",  color=color.green, linestyle=hline.style_dashed)
hline(overbought,  "Surachat",  color=color.red,   linestyle=hline.style_dashed)
hline(50,          "Neutre",    color=color.gray,  linestyle=hline.style_dotted)

rsi_color = rsi < oversold ? color.green : rsi > overbought ? color.red : color.purple
plot(rsi, "RSI", color=rsi_color, linewidth=2)

// ---- Alertes ----
alertcondition(long_signal,  "RSI — Achat", "RSI: Sortie de zone survente — Signal d'achat")
alertcondition(close_signal, "RSI — Vente", "RSI: Entrée en zone surachat — Signal de vente")
"""


PARAMS_SCHEMA = {
    "rsi_length":    {"type": "int",   "default": 14, "min": 1,  "max": 100, "label": "Période RSI"},
    "oversold":      {"type": "int",   "default": 30, "min": 10, "max": 50,  "label": "Niveau survente"},
    "overbought":    {"type": "int",   "default": 70, "min": 50, "max": 90,  "label": "Niveau surachat"},
    "stop_loss_pct":    {"type": "float", "default": 3.0, "min": 0.1, "max": 20.0, "label": "Stop Loss %"},
    "take_profit_pct":  {"type": "float", "default": 5.0, "min": 0.1, "max": 50.0, "label": "Take Profit %"},
}

INDICATORS = ["RSI"]
DESCRIPTION = "Stratégie de retournement RSI. Achat quand le RSI sort de la zone de survente, fermeture en zone de surachat."
