import pytest
from app.integrations.etoro_client import MockEtoroClient, get_etoro_client, _btc_exposure, _concentration_score


# ---------------------------------------------------------------------------
# MockEtoroClient
# ---------------------------------------------------------------------------

def test_mock_status_read_only():
    status = MockEtoroClient().get_status()
    assert status.mock is True
    assert status.allow_real_orders is False
    assert status.mode == "read_only"
    assert status.connected is False


def test_mock_portfolio_structure():
    p = MockEtoroClient().get_portfolio()
    assert p.total_value > 0
    assert p.cash >= 0
    assert p.invested > 0
    assert 0.0 <= p.btc_exposure_pct <= 100.0
    assert 0.0 <= p.concentration_score <= 100.0
    assert len(p.positions) > 0


def test_mock_positions_have_required_fields():
    for pos in MockEtoroClient().get_positions():
        assert pos.symbol
        assert pos.name
        assert 0.0 <= pos.weight_pct <= 100.0
        assert pos.current_value > 0


def test_mock_btc_position_is_crypto():
    positions = MockEtoroClient().get_positions()
    btc = next((p for p in positions if p.symbol == "BTC"), None)
    assert btc is not None
    assert btc.is_crypto is True


def test_mock_btc_exposure_matches_position_weight():
    client = MockEtoroClient()
    portfolio = client.get_portfolio()
    positions = client.get_positions()
    btc_weight = sum(p.weight_pct for p in positions if p.symbol == "BTC")
    assert portfolio.btc_exposure_pct == btc_weight


def test_mock_portfolio_capital_consistency():
    p = MockEtoroClient().get_portfolio()
    # cash + invested ≈ total (floating point tolerance)
    assert abs((p.cash + sum(pos.current_value for pos in p.positions)) - p.total_value) < 1.0


# ---------------------------------------------------------------------------
# Analyse
# ---------------------------------------------------------------------------

def test_mock_analyze_fields():
    analysis = MockEtoroClient().analyze()
    assert analysis.btc_exposure_pct >= 0
    assert analysis.concentration_score >= 0
    assert len(analysis.recommendations) > 0
    assert analysis.risk_level in ("faible", "modéré", "élevé")
    assert analysis.summary
    assert analysis.disclaimer


def test_analyze_btc_exposure_high_triggers_warning():
    from app.schemas.etoro import EtoroPortfolio, EtoroPosition
    from app.integrations.etoro_client import _build_analysis

    btc_pos = EtoroPosition(
        symbol="BTC", name="Bitcoin", weight_pct=65.0, performance_pct=10.0,
        invested=6500.0, current_value=6500.0, is_crypto=True,
    )
    portfolio = EtoroPortfolio(
        total_value=10000.0, cash=1000.0, invested=9000.0, performance_pct=0.0,
        btc_exposure_pct=65.0, concentration_score=80.0, positions=[btc_pos],
    )
    analysis = _build_analysis(portfolio)
    assert any("élevée" in r for r in analysis.recommendations)
    assert analysis.risk_level == "élevé"


# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------

def test_btc_exposure_empty_positions():
    assert _btc_exposure([]) == 0.0


def test_concentration_score_single_position():
    from app.schemas.etoro import EtoroPosition
    pos = EtoroPosition(
        symbol="BTC", name="Bitcoin", weight_pct=100.0, performance_pct=0.0,
        invested=10000.0, current_value=10000.0, is_crypto=True,
    )
    score = _concentration_score([pos])
    assert score == 100.0


def test_concentration_score_equal_weights():
    from app.schemas.etoro import EtoroPosition
    positions = [
        EtoroPosition(symbol=s, name=s, weight_pct=25.0, performance_pct=0.0,
                      invested=2500.0, current_value=2500.0)
        for s in ["A", "B", "C", "D"]
    ]
    score = _concentration_score(positions)
    assert score == pytest.approx(0.0, abs=0.1)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def test_factory_returns_mock_by_default():
    # ETORO_API_ENABLED defaults to False → always mock
    assert isinstance(get_etoro_client(), MockEtoroClient)


def test_allow_real_orders_is_always_false_in_mock():
    assert MockEtoroClient().get_status().allow_real_orders is False
