import uuid
from datetime import date as date_type
from typing import Optional

from sqlalchemy.orm import Session

from app.models.loan import Loan
from app.schemas.loan import LoanCreate
from app.services.loan_calculator import calculate_loan


def get_loan(db: Session, loan_id: uuid.UUID) -> Optional[Loan]:
    return db.query(Loan).filter(Loan.id == loan_id).first()


def get_loans(db: Session, skip: int = 0, limit: int = 100) -> list[Loan]:
    return db.query(Loan).order_by(Loan.disbursed_date.desc()).offset(skip).limit(limit).all()


def get_active_loan_for_customer(db: Session, customer_id: uuid.UUID) -> Optional[Loan]:
    return (
        db.query(Loan)
        .filter(Loan.customer_id == customer_id, Loan.status == "active")
        .first()
    )


def create_loan(db: Session, loan_in: LoanCreate) -> Loan:
    disbursed_date = loan_in.disbursed_date or date_type.today()
    calculated = calculate_loan(loan_in.principal_amount, disbursed_date)

    loan = Loan(
        customer_id=loan_in.customer_id,
        principal_amount=loan_in.principal_amount,
        disbursed_date=disbursed_date,
        status="active",
        **calculated,
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def update_loan_status(db: Session, loan: Loan, status: str) -> Loan:
    loan.status = status
    db.commit()
    db.refresh(loan)
    return loan