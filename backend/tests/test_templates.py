import pytest
import app.templates.sma as sma
import app.templates.rsi as rsi
import app.templates.adx as adx
import app.templates.supertrend as st
import app.templates.combined as combo


def _has_pine_header(script: str) -> bool:
    return "//@version=5" in script


def _has_strategy_call(script: str) -> bool:
    return "strategy(" in script


def test_sma_generates_valid_pine():
    script = sma.generate()
    assert _has_pine_header(script)
    assert _has_strategy_call(script)
    assert "ta.sma" in script
    assert "strategy.entry" in script
    assert "alertcondition" in script


def test_sma_params_reflected():
    script = sma.generate(fast_length=10, slow_length=30)
    assert "10" in script
    assert "30" in script


def test_rsi_generates_valid_pine():
    script = rsi.generate()
    assert _has_pine_header(script)
    assert _has_strategy_call(script)
    assert "ta.rsi" in script
    assert "hline" in script


def test_rsi_params_schema():
    assert "rsi_length" in rsi.PARAMS_SCHEMA
    assert "oversold" in rsi.PARAMS_SCHEMA
    assert "overbought" in rsi.PARAMS_SCHEMA


def test_adx_generates_valid_pine():
    script = adx.generate()
    assert _has_pine_header(script)
    assert "ta.dmi" in script


def test_supertrend_generates_valid_pine():
    script = st.generate()
    assert _has_pine_header(script)
    assert "ta.supertrend" in script


def test_combined_generates_valid_pine():
    script = combo.generate()
    assert _has_pine_header(script)
    assert "ta.sma" in script
    assert "ta.rsi" in script
    assert "ta.dmi" in script


def test_all_templates_have_metadata():
    for tpl in [sma, rsi, adx, st, combo]:
        assert hasattr(tpl, "PARAMS_SCHEMA")
        assert hasattr(tpl, "INDICATORS")
        assert hasattr(tpl, "DESCRIPTION")
        assert len(tpl.INDICATORS) > 0
        assert len(tpl.DESCRIPTION) > 10
