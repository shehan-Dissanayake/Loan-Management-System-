from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from app.models.loan import Loan
from app.models.payment import Payment
from app.models.customer import Customer
from app.services.arrears_calculator import calculate_arrears


def compute_customer_risk(db: Session, customer_id) -> dict:
    """
    Compute a rule-based risk score for a customer on the fly.

    Rules implemented:
    - late/arrears count across all loans: +15 points per arrears day
    - each overdue loan: +20 points
    - high outstanding principal scales additional points

    Returns: { score: int, level: 'LOW'|'MEDIUM'|'HIGH', reasons: [str] }
    """
    # Gather loans for customer
    loans: List[Loan] = db.query(Loan).filter(Loan.customer_id == customer_id).all()

    total_arrears = 0
    overdue_count = 0
    outstanding_total = Decimal("0")

    reasons: List[str] = []

    for loan in loans:
        payments: List[Payment] = db.query(Payment).filter(Payment.loan_id == loan.id).all()
        payments_by_date = {p.payment_date: p.amount_collected for p in payments}

        arrears_info = calculate_arrears(loan.disbursed_date, loan.installment_amount, payments_by_date)
        total_arrears += int(arrears_info.get("arrears_count", 0))

        if loan.status == "overdue":
            overdue_count += 1

        paid = sum((p.amount_collected for p in payments), Decimal("0"))
        remaining = loan.total_payable - paid
        if remaining > 0:
            outstanding_total += remaining

    # Base score from late payments
    score = total_arrears * 15

    if total_arrears > 0:
        reasons.append(f"{total_arrears} late payment day(s) found (+{total_arrears * 15} pts)")

    # Overdue loans penalty
    if overdue_count > 0:
        add = overdue_count * 20
        score += add
        reasons.append(f"{overdue_count} overdue loan(s) (+{add} pts)")

    # Outstanding principal factor (small scaling)
    if outstanding_total > 0:
        # add 1 point per 10000 outstanding, capped at 50
        scale = int(outstanding_total / Decimal("10000"))
        add = min(50, scale)
        score += add
        reasons.append(f"Outstanding balance {outstanding_total:.2f} adds {add} pts")

    # Compose risk level
    level = "LOW"
    if score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"

    # If no reasons, give positive reason
    if not reasons:
        reasons = ["No late payments or overdue loans found."]

    return {
        "score": int(score),
        "level": level,
        "reasons": reasons,
    }
