"""Génération de Pine Script via le fournisseur IA ou les templates locaux."""
from typing import Optional, Any

from app.services.ai_provider import get_ai_provider
import app.templates.sma as sma_tpl
import app.templates.rsi as rsi_tpl
import app.templates.adx as adx_tpl
import app.templates.supertrend as st_tpl
import app.templates.combined as combo_tpl

TEMPLATE_MAP = {
    "sma": sma_tpl,
    "supertrend": st_tpl,
    "rsi": rsi_tpl,
    "adx": adx_tpl,
    "combined": combo_tpl,
}

ALL_TEMPLATES = [
    {"key": "sma",        "name": "SMA Cross Strategy",          "indicators": sma_tpl.INDICATORS,   "description": sma_tpl.DESCRIPTION},
    {"key": "supertrend", "name": "Supertrend Strategy",         "indicators": st_tpl.INDICATORS,    "description": st_tpl.DESCRIPTION},
    {"key": "rsi",        "name": "RSI Reversal Strategy",       "indicators": rsi_tpl.INDICATORS,   "description": rsi_tpl.DESCRIPTION},
    {"key": "adx",        "name": "ADX Trend Filter Strategy",   "indicators": adx_tpl.INDICATORS,   "description": adx_tpl.DESCRIPTION},
    {"key": "combined",   "name": "SMA + RSI + ADX Combined",    "indicators": combo_tpl.INDICATORS, "description": combo_tpl.DESCRIPTION},
]


async def generate_strategy(prompt: str, template: Optional[str], risk_profile: str) -> dict:
    provider = get_ai_provider()
    return await provider.generate_strategy(prompt, template, risk_profile)


def get_template_pine_script(template_key: str, params: dict[str, Any]) -> str:
    tpl = TEMPLATE_MAP.get(template_key)
    if tpl is None:
        raise ValueError(f"Template inconnu : {template_key}")
    # Filtrer uniquement les paramètres attendus par le template
    import inspect
    sig = inspect.signature(tpl.generate)
    valid_keys = set(sig.parameters.keys())
    filtered = {k: v for k, v in params.items() if k in valid_keys}
    return tpl.generate(**filtered)


def get_template_schema(template_key: str) -> dict:
    tpl = TEMPLATE_MAP.get(template_key)
    if tpl is None:
        raise ValueError(f"Template inconnu : {template_key}")
    return {
        "key": template_key,
        "params_schema": tpl.PARAMS_SCHEMA,
        "indicators": tpl.INDICATORS,
        "description": tpl.DESCRIPTION,
    }
