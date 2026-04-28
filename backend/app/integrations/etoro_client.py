"""Client eToro — lecture seule uniquement. Aucun ordre réel ne peut être exécuté."""
from abc import ABC, abstractmethod

import httpx

from app.core.config import settings
from app.core.logging import logger
from app.schemas.etoro import EtoroAnalysis, EtoroPortfolio, EtoroPosition, EtoroStatus

# ---------------------------------------------------------------------------
# Données mock — portefeuille BTC-centré réaliste
# ---------------------------------------------------------------------------

_MOCK_POSITIONS: list[EtoroPosition] = [
    EtoroPosition(
        symbol="BTC", name="Bitcoin", weight_pct=36.4, performance_pct=24.7,
        invested=3500.0, current_value=4362.5,
        buy_price=45000.0, sell_price=56100.0, is_crypto=True,
    ),
    EtoroPosition(
        symbol="ETH", name="Ethereum", weight_pct=19.5, performance_pct=11.3,
        invested=2100.0, current_value=2336.5,
        buy_price=2800.0, sell_price=3116.0, is_crypto=True,
    ),
    EtoroPosition(
        symbol="AAPL", name="Apple Inc.", weight_pct=15.0, performance_pct=5.8,
        invested=1700.0, current_value=1798.8,
        buy_price=175.0, sell_price=185.2, is_crypto=False,
    ),
    EtoroPosition(
        symbol="GOLD", name="Gold ETF", weight_pct=8.2, performance_pct=-1.4,
        invested=1000.0, current_value=986.0, is_crypto=False,
    ),
    EtoroPosition(
        symbol="NVDA", name="NVIDIA Corp.", weight_pct=14.2, performance_pct=42.1,
        invested=1200.0, current_value=1705.2,
        buy_price=480.0, sell_price=682.1, is_crypto=False,
    ),
]

_MOCK_TOTAL = 12000.0   # sum(current_value) + cash = 11189 + 811
_MOCK_CASH  = 811.0


# ---------------------------------------------------------------------------
# Fonctions de calcul partagées
# ---------------------------------------------------------------------------

def _btc_exposure(positions: list[EtoroPosition]) -> float:
    return round(sum(p.weight_pct for p in positions if p.symbol == "BTC"), 2)


def _concentration_score(positions: list[EtoroPosition]) -> float:
    """Indice HHI normalisé : 0 = diversifié, 100 = concentré."""
    if not positions:
        return 0.0
    weights = [p.weight_pct / 100 for p in positions]
    hhi = sum(w ** 2 for w in weights)
    n = len(positions)
    min_hhi = 1.0 / n
    if min_hhi >= 1.0:
        return 100.0
    return round((hhi - min_hhi) / (1.0 - min_hhi) * 100, 1)


def _build_analysis(portfolio: EtoroPortfolio) -> EtoroAnalysis:
    btc  = portfolio.btc_exposure_pct
    conc = portfolio.concentration_score
    recs: list[str] = []

    if btc > 40:
        recs.append(f"Exposition BTC élevée ({btc:.1f} %) — envisagez une diversification.")
    elif btc < 10:
        recs.append(f"Exposition BTC faible ({btc:.1f} %) — peu alignée avec une stratégie BTC Optimizer.")
    else:
        recs.append(f"Exposition BTC acceptable ({btc:.1f} %) — dans la fourchette cible (10–40 %).")

    if conc > 60:
        recs.append("Concentration élevée : le portefeuille manque de diversification.")
    elif conc < 30:
        recs.append("Bonne diversification entre actifs.")

    if portfolio.performance_pct < 0:
        recs.append("Performance globale négative — revoyez les positions perdantes.")
    elif portfolio.performance_pct > 20:
        recs.append("Performance solide — envisagez de sécuriser une partie des gains.")

    cash_ratio = portfolio.cash / portfolio.total_value if portfolio.total_value else 0
    if cash_ratio > 0.3:
        recs.append(f"Cash élevé ({cash_ratio * 100:.0f} %) — opportunité de déploiement progressif.")

    risk = (
        "élevé"  if btc > 50 or conc > 70 else
        "modéré" if btc > 25 or conc > 40 else
        "faible"
    )
    summary = (
        f"Portefeuille de {portfolio.total_value:,.0f} $ avec {len(portfolio.positions)} positions. "
        f"Exposition BTC : {btc:.1f} %. Score de concentration : {conc:.0f}/100. "
        f"Niveau de risque estimé : {risk}."
    )
    return EtoroAnalysis(
        btc_exposure_pct=btc,
        concentration_score=conc,
        recommendations=recs,
        risk_level=risk,
        summary=summary,
        disclaimer="Analyse automatique basée sur les données du portefeuille. Pas un conseil financier.",
    )


# ---------------------------------------------------------------------------
# Classe abstraite
# ---------------------------------------------------------------------------

class EtoroClient(ABC):
    @abstractmethod
    def get_status(self) -> EtoroStatus:
        pass

    @abstractmethod
    def get_portfolio(self) -> EtoroPortfolio:
        pass

    @abstractmethod
    def get_positions(self) -> list[EtoroPosition]:
        pass

    def analyze(self) -> EtoroAnalysis:
        return _build_analysis(self.get_portfolio())

    def _guard_no_orders(self) -> None:
        """Garde structurelle : lève une exception si les ordres réels sont activés."""
        if settings.ETORO_ALLOW_REAL_ORDERS:
            raise RuntimeError(
                "ETORO_ALLOW_REAL_ORDERS=true est interdit dans cette application. "
                "Remettez-le à false pour continuer."
            )


# ---------------------------------------------------------------------------
# MockEtoroClient
# ---------------------------------------------------------------------------

class MockEtoroClient(EtoroClient):
    def get_status(self) -> EtoroStatus:
        return EtoroStatus(
            enabled=False, mode="read_only",
            connected=False, allow_real_orders=False, mock=True,
        )

    def get_portfolio(self) -> EtoroPortfolio:
        positions = _MOCK_POSITIONS
        invested = sum(p.invested for p in positions)
        current  = sum(p.current_value for p in positions)
        perf     = round((current - invested) / invested * 100, 2) if invested else 0.0
        return EtoroPortfolio(
            total_value=_MOCK_TOTAL,
            cash=_MOCK_CASH,
            invested=round(invested, 2),
            performance_pct=perf,
            btc_exposure_pct=_btc_exposure(positions),
            concentration_score=_concentration_score(positions),
            currency="USD",
            positions=positions,
        )

    def get_positions(self) -> list[EtoroPosition]:
        return _MOCK_POSITIONS


# ---------------------------------------------------------------------------
# RealEtoroClient (lecture seule, ordres bloqués structurellement)
# ---------------------------------------------------------------------------

class RealEtoroClient(EtoroClient):
    def __init__(self) -> None:
        self._guard_no_orders()
        # Les clés API transitent uniquement dans les headers HTTP, jamais dans les logs.
        self._http = httpx.Client(
            base_url=settings.ETORO_API_BASE_URL,
            headers={
                "X-API-KEY":  settings.ETORO_PUBLIC_API_KEY or "",
                "X-USER-KEY": settings.ETORO_USER_KEY or "",
            },
            timeout=10.0,
        )

    def _get(self, path: str) -> dict:
        resp = self._http.get(path)
        resp.raise_for_status()
        return resp.json()

    def get_status(self) -> EtoroStatus:
        try:
            self._get("/v1/status")
            connected = True
        except Exception:
            connected = False
        return EtoroStatus(
            enabled=True, mode=settings.ETORO_MODE,
            connected=connected, allow_real_orders=False, mock=False,
        )

    def get_portfolio(self) -> EtoroPortfolio:
        data = self._get(f"/v1/users/{settings.ETORO_USER_KEY}/portfolio")
        positions = [
            EtoroPosition(
                symbol=p["instrumentId"],
                name=p.get("instrumentName", p["instrumentId"]),
                weight_pct=float(p.get("allocation", 0)),
                performance_pct=float(p.get("pnlPercent", 0)),
                invested=float(p.get("invested", 0)),
                current_value=float(p.get("netValue", 0)),
                is_crypto=p.get("assetType", "") == "crypto",
            )
            for p in data.get("positions", [])
        ]
        invested = sum(p.invested for p in positions)
        current  = sum(p.current_value for p in positions)
        perf     = round((current - invested) / invested * 100, 2) if invested else 0.0
        return EtoroPortfolio(
            total_value=float(data.get("totalValue", 0)),
            cash=float(data.get("availableCash", 0)),
            invested=round(invested, 2),
            performance_pct=perf,
            btc_exposure_pct=_btc_exposure(positions),
            concentration_score=_concentration_score(positions),
            positions=positions,
        )

    def get_positions(self) -> list[EtoroPosition]:
        return self.get_portfolio().positions


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_etoro_client() -> EtoroClient:
    if (
        settings.ETORO_API_ENABLED
        and settings.ETORO_PUBLIC_API_KEY
        and settings.ETORO_USER_KEY
        and not settings.ETORO_ALLOW_REAL_ORDERS
    ):
        try:
            logger.info("Client eToro : mode réel (lecture seule)")
            return RealEtoroClient()
        except Exception as exc:
            logger.warning("Connexion eToro échouée (%s) — bascule sur le mode mock", exc)
    logger.info("Client eToro : mode mock")
    return MockEtoroClient()
