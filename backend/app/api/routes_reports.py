from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.strategy import Strategy
from app.models.version import StrategyVersion
from app.models.backtest import Backtest
from app.models.report import Report
from app.schemas.report import GenerateReportRequest, ReportOut
from app.services.report_generator import generate_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate", response_model=ReportOut)
def generate(req: GenerateReportRequest, db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter(Strategy.id == req.strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Stratégie introuvable")

    version = db.query(StrategyVersion).filter(
        StrategyVersion.strategy_id == req.strategy_id,
        StrategyVersion.is_current == True,
    ).first()

    backtest = None
    if req.backtest_id:
        backtest = db.query(Backtest).filter(Backtest.id == req.backtest_id).first()
    else:
        backtest = db.query(Backtest).filter(
            Backtest.strategy_id == req.strategy_id
        ).order_by(Backtest.created_at.desc()).first()

    content = generate_report(strategy, version, backtest)

    report = Report(strategy_id=req.strategy_id, content=content)
    db.add(report)
    db.commit()
    db.refresh(report)
    return ReportOut.model_validate(report)


@router.get("/strategy/{strategy_id}", response_model=list[ReportOut])
def list_reports(strategy_id: int, db: Session = Depends(get_db)):
    reports = db.query(Report).filter(
        Report.strategy_id == strategy_id
    ).order_by(Report.created_at.desc()).all()
    return [ReportOut.model_validate(r) for r in reports]


@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(Report).filter(Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Rapport introuvable")
    return ReportOut.model_validate(r)


@router.get("/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(Report).filter(Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Rapport introuvable")
    filename = f"rapport_strategie_{r.strategy_id}_{report_id}.md"
    return Response(
        content=r.content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("")
def list_all_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).limit(50).all()
    return [ReportOut.model_validate(r) for r in reports]
