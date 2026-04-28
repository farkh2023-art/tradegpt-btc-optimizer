from datetime import datetime
from sqlalchemy import Text, DateTime, Integer, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class Backtest(Base):
    __tablename__ = "backtests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    strategy_id: Mapped[int] = mapped_column(ForeignKey("strategies.id"))
    version_id: Mapped[int | None] = mapped_column(ForeignKey("strategy_versions.id"), nullable=True)

    params: Mapped[str] = mapped_column(Text, default="{}")
    initial_capital: Mapped[float] = mapped_column(Float, default=10000.0)
    final_capital: Mapped[float] = mapped_column(Float, default=0.0)
    return_pct: Mapped[float] = mapped_column(Float, default=0.0)
    num_trades: Mapped[int] = mapped_column(Integer, default=0)
    win_rate: Mapped[float] = mapped_column(Float, default=0.0)
    max_drawdown: Mapped[float] = mapped_column(Float, default=0.0)
    profit_factor: Mapped[float] = mapped_column(Float, default=0.0)
    sharpe_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(50), default="local")
    equity_curve: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    strategy: Mapped["Strategy"] = relationship(back_populates="backtests")
    version: Mapped["StrategyVersion | None"] = relationship(back_populates="backtests")
