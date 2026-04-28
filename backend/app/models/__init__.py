# Importer tous les modèles ici pour que SQLAlchemy résolve les forward references
from app.models.strategy import Strategy
from app.models.version import StrategyVersion
from app.models.backtest import Backtest
from app.models.report import Report

__all__ = ["Strategy", "StrategyVersion", "Backtest", "Report"]
