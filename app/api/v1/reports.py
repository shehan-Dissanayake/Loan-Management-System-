import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import report as crud
from app.schemas.report import (
    OutstandingLoanItem,
    RouteItem,
    DailyCollectionReport,
    CashFlowSummary,
    CustomerLoanHistoryItem,
)
from app.services.risk_calculator import compute_customer_risk
from app.models.customer import Customer

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/outstanding", response_model=list[OutstandingLoanItem])
def outstanding_loans(db: Session = Depends(get_db)):
    return crud.get_outstanding_loans(db)


@router.get("/overdue", response_model=list[OutstandingLoanItem])
def overdue_loans(db: Session = Depends(get_db)):
    return crud.get_overdue_loans(db)


@router.get("/route-today", response_model=list[RouteItem])
def todays_route(db: Session = Depends(get_db)):
    return crud.get_todays_route(db)


@router.get("/daily-collection", response_model=DailyCollectionReport)
def daily_collection(
    report_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    return crud.get_daily_collection(db, report_date)


@router.get("/cash-flow", response_model=CashFlowSummary)
def cash_flow(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_cash_flow_summary(db, start_date, end_date)


@router.get("/customers/{customer_id}/history", response_model=list[CustomerLoanHistoryItem])
def customer_history(customer_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.get_customer_history(db, customer_id)


@router.get("/risk-summary")
def risk_summary(db: Session = Depends(get_db)):
    """Return counts of LOW/MEDIUM/HIGH risk customers for dashboard display."""
    rows = db.query(Customer).all()
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for c in rows:
        r = compute_customer_risk(db, c.id)
        counts[r["level"]] = counts.get(r["level"], 0) + 1
    counts["total"] = len(rows)
    return counts