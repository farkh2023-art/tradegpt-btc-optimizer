from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.db.database import Base, engine
import app.models  # noqa: F401 — enregistre tous les modèles auprès de SQLAlchemy
from app.api.routes_strategies import router as strategies_router
from app.api.routes_ai import router as ai_router
from app.api.routes_backtests import router as backtests_router
from app.api.routes_optimization import router as optimization_router
from app.api.routes_reports import router as reports_router

# Création des tables SQLite au démarrage
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API de génération et d'optimisation de stratégies de trading Bitcoin en Pine Script v5.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(strategies_router)
app.include_router(ai_router)
app.include_router(backtests_router)
app.include_router(optimization_router)
app.include_router(reports_router)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "ok",
        "disclaimer": "Simulation uniquement — pas un conseil financier.",
    }


@app.get("/health")
def health():
    from app.services.ai_provider import get_ai_provider
    provider = get_ai_provider()
    return {
        "status": "healthy",
        "ai_provider": provider.provider_name,
        "ai_available": provider.is_available,
        "mode": "paper_trading_only",
    }


logger.info("TradeGPT BTC Optimizer démarré. Docs : http://localhost:8000/docs")
