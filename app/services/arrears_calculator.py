from datetime import date, timedelta
from decimal import Decimal


def weekdays_between(start: date, end: date) -> list[date]:
    """Every Monday–Friday date in the inclusive range start..end."""
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def calculate_arrears(
    disbursed_date: date,
    installment_amount: Decimal,
    payments_by_date: dict[date, Decimal],
    holidays: set[date],
    as_of: date | None = None,
) -> dict:
    as_of = as_of or date.today()

    # Arrears tracking starts the day AFTER disbursement, not on the disbursement day itself
    first_collection_day = disbursed_date + timedelta(days=1)
    scheduled_weekdays = set(weekdays_between(first_collection_day, as_of)) - holidays

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