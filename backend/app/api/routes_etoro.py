from fastapi import APIRouter, HTTPException

from app.integrations.etoro_client import get_etoro_client
from app.schemas.etoro import EtoroAnalyzeRequest, EtoroAnalysis, EtoroPortfolio, EtoroStatus

router = APIRouter(prefix="/api/etoro", tags=["etoro"])


@router.get("/status", response_model=EtoroStatus)
def etoro_status():
    return get_etoro_client().get_status()


@router.get("/portfolio", response_model=EtoroPortfolio)
def etoro_portfolio():
    try:
        return get_etoro_client().get_portfolio()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur eToro portfolio : {exc}")


@router.get("/positions")
def etoro_positions():
    try:
        client = get_etoro_client()
        positions = client.get_positions()
        return {"positions": [p.model_dump() for p in positions], "count": len(positions)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur eToro positions : {exc}")


@router.post("/analyze", response_model=EtoroAnalysis)
def etoro_analyze(req: EtoroAnalyzeRequest):
    try:
        return get_etoro_client().analyze()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur analyse eToro : {exc}")
