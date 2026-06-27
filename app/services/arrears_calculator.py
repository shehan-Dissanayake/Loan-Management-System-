from datetime import date, timedelta
from decimal import Decimal


def weekdays_between(start: date, end: date) -> list[date]:
    """Every Monday–Friday date in the inclusive range start..end."""
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:  # Mon=0 ... Fri=4, Sat/Sun excluded
            days.append(current)
        current += timedelta(days=1)
    return days


def calculate_arrears(
    disbursed_date: date,
    installment_amount: Decimal,
    payments_by_date: dict[date, Decimal],
    as_of: date | None = None,
) -> dict:
    """
    A day is checked if either:
      (a) it's a weekday in the loan's active range (expected to be visited), or
      (b) a payment was actually recorded on it, even if that's a weekend
          (proof he genuinely visited that day).
    Any checked day where amount collected < installment_amount counts as
    one missed/arrears day, contributing the shortfall (not necessarily the
    full installment) to the rupee total.
    """
    as_of = as_of or date.today()
    scheduled_weekdays = set(weekdays_between(disbursed_date, as_of))
    days_to_check = scheduled_weekdays | set(payments_by_date.keys())

    arrears_count = 0
    arrears_amount = Decimal("0")
    for day in sorted(days_to_check):
        collected = payments_by_date.get(day, Decimal("0"))
        shortfall = installment_amount - collected
        if shortfall > 0:
            arrears_count += 1
            arrears_amount += shortfall

    return {
        "arrears_count": arrears_count,
        "arrears_amount": arrears_amount.quantize(Decimal("0.01")),
    }