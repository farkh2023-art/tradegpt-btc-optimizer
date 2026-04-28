def generate(
    sma_length: int = 50,
    rsi_length: int = 14,
    rsi_oversold: int = 40,
    rsi_overbought: int = 60,
    adx_length: int = 14,
    adx_threshold: int = 20,
    stop_loss_pct: float = 2.0,
    take_profit_pct: float = 5.0,
    qty_pct: float = 10.0,
) -> str:
    return f"""//@version=5
// ============================================================
// SMA + RSI + ADX Combined Strategy — TradeGPT BTC Optimizer
// SIMULATION UNIQUEMENT — Pas un conseil financier
// ============================================================
strategy("SMA + RSI + ADX Combined", overlay=true,
         default_qty_type=strategy.percent_of_equity,
         default_qty_value={qty_pct},
         initial_capital=10000,
         commission_type=strategy.commission.percent,
         commission_value=0.1)

// ---- Paramètres SMA ----
sma_length      = input.int({sma_length},      "Période SMA",       minval=1,  maxval=500, group="SMA")

// ---- Paramètres RSI ----
rsi_length      = input.int({rsi_length},      "Période RSI",       minval=1,  maxval=100, group="RSI")
rsi_oversold    = input.int({rsi_oversold},    "RSI — Survente",    minval=10, maxval=50,  group="RSI")
rsi_overbought  = input.int({rsi_overbought},  "RSI — Surachat",    minval=50, maxval=90,  group="RSI")

// ---- Paramètres ADX ----
adx_length      = input.int({adx_length},      "Période ADX",       minval=1,  maxval=50,  group="ADX")
adx_threshold   = input.int({adx_threshold},   "Seuil ADX",         minval=10, maxval=60,  group="ADX")

// ---- Gestion du risque ----
stop_loss       = input.float({stop_loss_pct},   "Stop Loss %",    minval=0.1, maxval=20.0, step=0.1, group="Risque")
take_profit     = input.float({take_profit_pct}, "Take Profit %",  minval=0.1, maxval=50.0, step=0.1, group="Risque")

// ---- Calcul des indicateurs ----
sma             = ta.sma(close, sma_length)
rsi             = ta.rsi(close, rsi_length)
[diplus, diminus, adx] = ta.dmi(adx_length, adx_length)

// ---- Filtres et conditions ----
// Prix au-dessus de la SMA (tendance haussière)
above_sma       = close > sma
// RSI pas en surachat
rsi_ok          = rsi < rsi_overbought
// RSI en zone neutre-survente (opportunité achat)
rsi_buy_zone    = rsi < rsi_overbought and rsi > rsi_oversold - 5
// Tendance forte confirmée par ADX
trend_strong    = adx > adx_threshold and diplus > diminus

// ---- Signaux ----
// Achat : prix > SMA + RSI sort de survente + tendance ADX confirmée
long_signal     = above_sma and ta.crossover(rsi, rsi_oversold) and trend_strong

// Vente : RSI en surachat OU prix < SMA
close_signal    = ta.crossunder(rsi, rsi_overbought) or (not above_sma and strategy.position_size > 0)

// ---- Entrées / Sorties ----
if long_signal
    strategy.entry("Long", strategy.long, comment="SMA+RSI+ADX ↑")
    strategy.exit("Exit Long", "Long",
                  stop  = strategy.position_avg_price * (1 - stop_loss / 100),
                  limit = strategy.position_avg_price * (1 + take_profit / 100))

if close_signal
    strategy.close("Long", comment="Signal de vente combiné")

// ---- Affichage ----
plot(sma, "SMA " + str.tostring(sma_length), color=color.new(color.orange, 0), linewidth=2)

// Couleur RSI dans un panneau séparé (overlay=false serait mieux mais on garde overlay=true ici)
// Indicateur visuel de tendance
bgcolor(trend_strong ? color.new(color.blue, 92) : na, title="Tendance forte")
bgcolor(long_signal  ? color.new(color.green, 80) : na, title="Signal achat")
bgcolor(close_signal ? color.new(color.red,   80) : na, title="Signal vente")

// ---- Alertes ----
alertcondition(long_signal,  "Combiné — Achat", "SMA+RSI+ADX: Signal d'achat multi-indicateurs")
alertcondition(close_signal, "Combiné — Vente", "SMA+RSI+ADX: Signal de vente multi-indicateurs")
"""


PARAMS_SCHEMA = {
    "sma_length":     {"type": "int",   "default": 50, "min": 5,  "max": 500, "label": "Période SMA"},
    "rsi_length":     {"type": "int",   "default": 14, "min": 1,  "max": 100, "label": "Période RSI"},
    "rsi_oversold":   {"type": "int",   "default": 40, "min": 10, "max": 50,  "label": "RSI Survente"},
    "rsi_overbought": {"type": "int",   "default": 60, "min": 50, "max": 90,  "label": "RSI Surachat"},
    "adx_length":     {"type": "int",   "default": 14, "min": 1,  "max": 50,  "label": "Période ADX"},
    "adx_threshold":  {"type": "int",   "default": 20, "min": 10, "max": 60,  "label": "Seuil ADX"},
    "stop_loss_pct":  {"type": "float", "default": 2.0, "min": 0.1, "max": 20.0, "label": "Stop Loss %"},
    "take_profit_pct":{"type": "float", "default": 5.0, "min": 0.1, "max": 50.0, "label": "Take Profit %"},
}

INDICATORS = ["SMA", "RSI", "ADX"]
DESCRIPTION = "Stratégie combinée multi-indicateurs. Utilise SMA comme filtre de tendance, RSI pour le timing d'entrée et ADX pour confirmer la force de la tendance avant de prendre position."
