import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.loan import Loan
from app.models.payment import Payment
from app.models.customer import Customer


def _total_paid_map(db: Session, loan_ids: list) -> dict:
    if not loan_ids:
        return {}
    rows = (
        db.query(Payment.loan_id, func.coalesce(func.sum(Payment.amount_collected), 0))
        .filter(Payment.loan_id.in_(loan_ids))
        .group_by(Payment.loan_id)
        .all()
    )
    return {loan_id: Decimal(total) for loan_id, total in rows}


def get_outstanding_loans(db: Session) -> list[dict]:
    rows = (
        db.query(Loan, Customer)
        .join(Customer, Loan.customer_id == Customer.id)
        .filter(Loan.status == "active")
        .all()
    )
    loan_ids = [loan.id for loan, _ in rows]
    paid_map = _total_paid_map(db, loan_ids)

    today = date.today()
    results = []
    for loan, customer in rows:
        paid = paid_map.get(loan.id, Decimal("0"))
        balance_due = loan.total_payable - paid
        days_remaining = (loan.due_date - today).days
        results.append({
            "loan_id": loan.id,
            "customer_id": customer.id,
            "shop_name": customer.shop_name,
            "principal_amount": loan.principal_amount,
            "total_payable": loan.total_payable,
            "balance_due": balance_due,
            "installment_amount": loan.installment_amount,
            "due_date": loan.due_date,
            "days_remaining": days_remaining,
        })
    return results


def get_overdue_loans(db: Session) -> list[dict]:
    outstanding = get_outstanding_loans(db)
    return [item for item in outstanding if item["days_remaining"] < 0 and item["balance_due"] > 0]


def get_todays_route(db: Session) -> list[dict]:
    outstanding = get_outstanding_loans(db)
    today = date.today()
    loan_ids = [item["loan_id"] for item in outstanding]

    paid_today_ids = set()
    if loan_ids:
        rows = (
            db.query(Payment.loan_id)
            .filter(Payment.loan_id.in_(loan_ids), Payment.payment_date == today)
            .all()
        )
        paid_today_ids = {row[0] for row in rows}

    for item in outstanding:
        item["visited_today"] = item["loan_id"] in paid_today_ids

    outstanding.sort(key=lambda i: i["visited_today"])
    return outstanding


def get_daily_collection(db: Session, report_date: Optional[date] = None) -> dict:
    report_date = report_date or date.today()
    rows = (
        db.query(Payment, Loan, Customer)
        .join(Loan, Payment.loan_id == Loan.id)
        .join(Customer, Loan.customer_id == Customer.id)
        .filter(Payment.payment_date == report_date)
        .all()
    )
    items = [
        {
            "payment_id": payment.id,
            "loan_id": loan.id,
            "customer_id": customer.id,
            "shop_name": customer.shop_name,
            "amount_collected": payment.amount_collected,
            "payment_date": payment.payment_date,
        }
        for payment, loan, customer in rows
    ]
    total = sum((i["amount_collected"] for i in items), Decimal("0"))
    return {"date": report_date, "items": items, "total_collected": total}


def get_cash_flow_summary(
    db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None
) -> dict:
    end_date = end_date or date.today()
    start_date = start_date or date(end_date.year, end_date.month, 1)

    total_disbursed = (
        db.query(func.coalesce(func.sum(Loan.principal_amount), 0))
        .filter(Loan.disbursed_date >= start_date, Loan.disbursed_date <= end_date)
        .scalar()
    )
    total_collected = (
        db.query(func.coalesce(func.sum(Payment.amount_collected), 0))
        .filter(Payment.payment_date >= start_date, Payment.payment_date <= end_date)
        .scalar()
    )
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_disbursed": Decimal(total_disbursed),
        "total_collected": Decimal(total_collected),
        "net": Decimal(total_collected) - Decimal(total_disbursed),
    }


def get_customer_history(db: Session, customer_id: uuid.UUID) -> list[dict]:
    loans = (
        db.query(Loan)
        .filter(Loan.customer_id == customer_id)
        .order_by(Loan.disbursed_date.desc())
        .all()
    )
    loan_ids = [loan.id for loan in loans]

    payments = []
    if loan_ids:
        payments = (
            db.query(Payment)
            .filter(Payment.loan_id.in_(loan_ids))
            .order_by(Payment.payment_date)
            .all()
        )

    payments_by_loan: dict = {}
    for p in payments:
        payments_by_loan.setdefault(p.loan_id, []).append(p)

    return [
        {"loan": loan, "payments": payments_by_loan.get(loan.id, [])}
        for loan in loans
    ]


def get_payments_due_this_week(db: Session, week_start: date, week_end: date) -> list[dict]:
    rows = (
        db.query(Loan, Customer)
        .join(Customer, Loan.customer_id == Customer.id)
        .filter(
            Loan.status == "active",
            Loan.due_date >= week_start,
            Loan.due_date <= week_end,
        )
        .all()
    )
    loan_ids = [loan.id for loan, _ in rows]
    paid_map = _total_paid_map(db, loan_ids)

    results = []
    for loan, customer in rows:
        paid = paid_map.get(loan.id, Decimal("0"))
        balance_due = loan.total_payable - paid
        if balance_due <= 0:
            continue
        results.append({
            "loan_id": loan.id,
            "customer_id": customer.id,
            "shop_name": customer.shop_name,
            "balance_due": balance_due,
            "due_date": loan.due_date,
        })
    return results


def get_total_collection_in_month(db: Session, year: int, month: int) -> Decimal:
    total = (
        db.query(func.coalesce(func.sum(Payment.amount_collected), 0))
        .filter(
            func.extract('year', Payment.payment_date) == year,
            func.extract('month', Payment.payment_date) == month,
        )
        .scalar()
    )
    return Decimal(total)


def get_customers_with_loans_above(db: Session, amount: Decimal) -> list[dict]:
    rows = (
        db.query(Customer, func.coalesce(func.sum(Loan.principal_amount), 0).label('total_principal'), func.count(Loan.id).label('loan_count'))
        .join(Loan, Loan.customer_id == Customer.id)
        .group_by(Customer.id)
        .having(func.coalesce(func.sum(Loan.principal_amount), 0) > amount)
        .all()
    )
    return [
        {
            "customer_id": customer.id,
            "shop_name": customer.shop_name,
            "total_principal": Decimal(total_principal),
            "loans": loan_count,
        }
        for customer, total_principal, loan_count in rows
    ]
