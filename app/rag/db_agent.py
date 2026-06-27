import re
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.crud import report as report_crud

MONTHS = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12,
}


def _format_currency(value: Decimal) -> str:
    return f"Rs {value:,.2f}"


def _parse_amount(question: str) -> Optional[Decimal]:
    text = question.lower().replace('rs.', '').replace('rs', '').replace('rupees', '')
    text = text.replace(',', '')
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
    if not match:
        return None
    try:
        return Decimal(match.group(1))
    except Exception:
        return None


def _parse_month_year(question: str) -> Optional[tuple[int, int]]:
    text = question.lower()
    for name, number in MONTHS.items():
        if name in text:
            year = date.today().year
            year_match = re.search(rf"{name}\s+(\d{{4}})", text)
            if year_match:
                year = int(year_match.group(1))
            return number, year
    return None


def _current_week_range(start_date: Optional[date] = None) -> tuple[date, date]:
    today = start_date or date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def _overdue_loans_response(db: Session) -> str:
    overdue = report_crud.get_overdue_loans(db)
    if not overdue:
        return "No overdue loans were found in the database."

    lines = [f"There are {len(overdue)} overdue loan(s):"]
    for item in overdue[:8]:
        lines.append(
            f"- {item['shop_name']}: balance { _format_currency(item['balance_due']) }, due {item['due_date'].isoformat()}"
        )
    if len(overdue) > 8:
        lines.append(f"...and {len(overdue) - 8} more overdue loan(s).")
    return "\n".join(lines)


def _payments_due_this_week_response(db: Session) -> str:
    week_start, week_end = _current_week_range()
    due = report_crud.get_payments_due_this_week(db, week_start, week_end)
    if not due:
        return f"No loans with due dates between {week_start.isoformat()} and {week_end.isoformat()} were found."

    lines = [
        f"Customers with loan due dates this week ({week_start.isoformat()} to {week_end.isoformat()}):"
    ]
    for item in due[:8]:
        lines.append(
            f"- {item['shop_name']}: balance { _format_currency(item['balance_due']) }, due {item['due_date'].isoformat()}"
        )
    if len(due) > 8:
        lines.append(f"...and {len(due) - 8} more customer(s).")
    return "\n".join(lines)


def _total_collection_response(db: Session, question: str) -> Optional[str]:
    parsed = _parse_month_year(question)
    if parsed is None:
        return None

    month, year = parsed
    total = report_crud.get_total_collection_in_month(db, year, month)
    month_name = next((name.title() for name, num in MONTHS.items() if num == month), str(month))
    return f"Total collection for {month_name} {year}: {_format_currency(total)}."


def _borrowed_more_than_response(db: Session, question: str) -> Optional[str]:
    amount = _parse_amount(question)
    if amount is None:
        return None

    customers = report_crud.get_customers_with_loans_above(db, amount)
    if not customers:
        return f"No customers were found with loan principal above {_format_currency(amount)}."

    lines = [
        f"Customers with loans above {_format_currency(amount)}:"
    ]
    for customer in customers[:8]:
        lines.append(f"- {customer['shop_name']}: {len(customer['loans'])} loan(s), total principal {_format_currency(customer['total_principal'])}")
    if len(customers) > 8:
        lines.append(f"...and {len(customers) - 8} more customer(s).")
    return "\n".join(lines)


def get_database_response(question: str, db: Session) -> Optional[str]:
    text = question.lower()

    if 'overdue loan' in text or 'who has overdue' in text:
        return _overdue_loans_response(db)

    if 'payments due this week' in text or 'due this week' in text:
        return _payments_due_this_week_response(db)

    if 'total collection' in text and any(month in text for month in MONTHS):
        return _total_collection_response(db, question)

    if 'borrowed more than' in text or 'borrowed above' in text or 'borrowed over' in text:
        return _borrowed_more_than_response(db, question)

    return None
