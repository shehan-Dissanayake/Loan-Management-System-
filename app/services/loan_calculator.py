from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

MONTHLY_INTEREST_RATE = Decimal("6.6667")  # stored for display only
INTEREST_MONTHS = 3
TOTAL_INTEREST_RATE = Decimal("20")        # the actual precise flat rate used in calculation
LOAN_TERM_WEEKDAYS = 60                    # 60 weekday (Mon–Fri) collection days


def add_weekdays(start: date, weekdays: int) -> date:
    """Return the date that is exactly `weekdays` Mon–Fri days after `start`."""
    current = start
    counted = 0
    while counted < weekdays:
        current += timedelta(days=1)
        if current.weekday() < 5:   # 0=Mon … 4=Fri, 5=Sat, 6=Sun
            counted += 1
    return current


def calculate_loan(principal: Decimal, disbursed_date: date) -> dict:
    interest_amount = (
        principal * (TOTAL_INTEREST_RATE / Decimal("100"))
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    total_payable = principal + interest_amount

    installment_amount = (total_payable / Decimal(LOAN_TERM_WEEKDAYS)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Close date = disbursed date + 60 weekdays (weekends are not collection days)
    due_date = add_weekdays(disbursed_date, LOAN_TERM_WEEKDAYS)

    return {
        "monthly_interest_rate": MONTHLY_INTEREST_RATE,
        "interest_months": INTEREST_MONTHS,
        "interest_amount": interest_amount,
        "total_payable": total_payable,
        "installment_amount": installment_amount,
        "due_date": due_date,
    }