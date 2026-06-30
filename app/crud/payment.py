import uuid
from datetime import date as date_type
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.payment import Payment
from app.models.loan import Loan
from app.schemas.payment import PaymentCreate
from app.services.arrears_calculator import calculate_arrears
from app.crud.holiday import get_holiday_dates_set


def get_payments_for_loan(db: Session, loan_id: uuid.UUID) -> list[Payment]:
    return db.query(Payment).filter(Payment.loan_id == loan_id).order_by(Payment.payment_date).all()


def get_total_paid(db: Session, loan_id: uuid.UUID) -> Decimal:
    total = db.query(func.coalesce(func.sum(Payment.amount_collected), 0)).filter(
        Payment.loan_id == loan_id
    ).scalar()
    return Decimal(total)


def _recalculate_loan_payments(db: Session, loan: Loan) -> None:
    payments = (
        db.query(Payment)
          .filter(Payment.loan_id == loan.id)
          .order_by(Payment.payment_date, Payment.created_at, Payment.id)
          .all()
    )

    total_paid = Decimal("0")
    for payment in payments:
        total_paid += payment.amount_collected
        payment.balance_after_payment = loan.total_payable - total_paid

    if loan.status != "deactivated":
        if total_paid >= loan.total_payable:
            loan.status = "completed"
        elif loan.status == "completed":
            loan.status = "active"
        elif loan.status not in {"active", "overdue"}:
            loan.status = "active"

    db.commit()


def create_payment(db: Session, loan: Loan, payment_in: PaymentCreate) -> Payment:
    payment_date = payment_in.payment_date or date_type.today()

    payment = Payment(
        loan_id=loan.id,
        amount_collected=payment_in.amount_collected,
        payment_date=payment_date,
        balance_after_payment=loan.total_payable - payment_in.amount_collected,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    _recalculate_loan_payments(db, loan)
    db.refresh(payment)
    return payment


def update_payment(
    db: Session,
    loan_id: uuid.UUID,
    payment_id: uuid.UUID,
    amount_collected: Decimal | None = None,
    payment_date: date_type | None = None,
) -> Payment | None:
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id, Payment.loan_id == loan_id)
        .one_or_none()
    )
    if payment is None:
        return None

    if amount_collected is not None:
        payment.amount_collected = amount_collected
    if payment_date is not None:
        payment.payment_date = payment_date

    db.commit()
    loan = db.query(Loan).filter(Loan.id == loan_id).one()
    _recalculate_loan_payments(db, loan)
    db.refresh(payment)
    return payment


def delete_payment(db: Session, loan_id: uuid.UUID, payment_id: uuid.UUID) -> Payment | None:
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id, Payment.loan_id == loan_id)
        .one_or_none()
    )
    if payment is None:
        return None

    loan = db.query(Loan).filter(Loan.id == loan_id).one()
    db.delete(payment)
    db.commit()
    _recalculate_loan_payments(db, loan)
    return payment


def get_loan_summary(db: Session, loan: Loan) -> dict:
    payments = get_payments_for_loan(db, loan.id)
    total_paid = sum((p.amount_collected for p in payments), Decimal("0"))
    balance_due = loan.total_payable - total_paid

    payments_by_date: dict = {}
    for p in payments:
        payments_by_date[p.payment_date] = payments_by_date.get(p.payment_date, Decimal("0")) + p.amount_collected

    holidays = get_holiday_dates_set(db)
    arrears = calculate_arrears(loan.disbursed_date, loan.installment_amount, payments_by_date, holidays)

    return {
        **loan.__dict__,
        "balance_due": balance_due,
        "arrears_count": arrears["arrears_count"],
        "arrears_amount": arrears["arrears_amount"],
    }