import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.strategy import Strategy
from app.models.version import StrategyVersion
from app.schemas.strategy import GenerateStrategyRequest, GenerateStrategyResponse, StrategyOut, StrategyList
from app.schemas.version import CreateVersionRequest, VersionOut
from app.services.pine_generator import generate_strategy, ALL_TEMPLATES, get_template_schema, get_template_pine_script

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("/templates")
def list_templates():
    return {"templates": ALL_TEMPLATES}


@router.get("/templates/{key}")
def get_template(key: str):
    try:
        return get_template_schema(key)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/templates/{key}/generate")
def generate_from_template(key: str, params: dict = {}):
    try:
        pine = get_template_pine_script(key, params)
        schema = get_template_schema(key)
        return {"pine_script": pine, "template": key, **schema}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/generate", response_model=GenerateStrategyResponse)
async def generate(req: GenerateStrategyRequest, db: Session = Depends(get_db)):
    try:
        result = await generate_strategy(req.prompt, req.template, req.risk_profile)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur génération IA : {exc}")

    strategy = Strategy(
        name=result.get("name", "Nouvelle stratégie"),
        description=result.get("description", ""),
        prompt=req.prompt,
        template=req.template,
        risk_profile=req.risk_profile,
    )
    db.add(strategy)
    db.flush()

    version = StrategyVersion(
        strategy_id=strategy.id,
        version_number=1,
        pine_script=result.get("pine_script", ""),
        parameters=json.dumps(result.get("parameters", {})),
        explanation=result.get("explanation", ""),
        is_current=True,
    )
    db.add(version)
    db.commit()
    db.refresh(strategy)
    db.refresh(version)

    return GenerateStrategyResponse(
        strategy_id=strategy.id,
        name=strategy.name,
        description=strategy.description,
        pine_script=version.pine_script,
        parameters=result.get("parameters", {}),
        explanation=version.explanation,
        indicators=result.get("indicators", []),
    )


@router.get("", response_model=StrategyList)
def list_strategies(db: Session = Depends(get_db)):
    items = db.query(Strategy).order_by(Strategy.created_at.desc()).all()
    return StrategyList(items=[StrategyOut.model_validate(s) for s in items], total=len(items))


@router.get("/{strategy_id}", response_model=StrategyOut)
def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    s = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Stratégie introuvable")
    return StrategyOut.model_validate(s)


@router.delete("/{strategy_id}")
def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    s = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Stratégie introuvable")
    db.delete(s)
    db.commit()
    return {"deleted": strategy_id}


@router.post("/{strategy_id}/versions", response_model=VersionOut)
def create_version(strategy_id: int, req: CreateVersionRequest, db: Session = Depends(get_db)):
    s = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Stratégie introuvable")

    # Marquer les versions existantes comme non courantes
    db.query(StrategyVersion).filter(
        StrategyVersion.strategy_id == strategy_id
    ).update({"is_current": False})

    last = db.query(StrategyVersion).filter(
        StrategyVersion.strategy_id == strategy_id
    ).order_by(StrategyVersion.version_number.desc()).first()
    next_v = (last.version_number + 1) if last else 1

    version = StrategyVersion(
        strategy_id=strategy_id,
        version_number=next_v,
        pine_script=req.pine_script,
        parameters=json.dumps(req.parameters),
        explanation=req.explanation,
        is_current=True,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return VersionOut.model_validate(version)


@router.get("/{strategy_id}/versions", response_model=list[VersionOut])
def list_versions(strategy_id: int, db: Session = Depends(get_db)):
    versions = db.query(StrategyVersion).filter(
        StrategyVersion.strategy_id == strategy_id
    ).order_by(StrategyVersion.version_number.desc()).all()
    return [VersionOut.model_validate(v) for v in versions]


@router.get("/{strategy_id}/versions/{version_id}", response_model=VersionOut)
def get_version(strategy_id: int, version_id: int, db: Session = Depends(get_db)):
    v = db.query(StrategyVersion).filter(
        StrategyVersion.id == version_id,
        StrategyVersion.strategy_id == strategy_id,
    ).first()
    if not v:
        raise HTTPException(status_code=404, detail="Version introuvable")
    return VersionOut.model_validate(v)
