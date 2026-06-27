"""recalculate_due_date_60_weekdays

Revision ID: a2e165a7d7ff
Revises: f0cd718050b4
Create Date: 2026-06-26

Re-computes the due_date for every existing loan using the
"60 weekdays (Mon–Fri) from disbursed_date" rule instead of
the old "60 calendar days" rule.
"""
from typing import Sequence, Union
from datetime import timedelta

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'a2e165a7d7ff'
down_revision: Union[str, Sequence[str], None] = 'f0cd718050b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LOAN_TERM_WEEKDAYS = 60


def add_weekdays(start, weekdays: int):
    """Return the date that is exactly `weekdays` Mon–Fri days after `start`."""
    from datetime import timedelta
    current = start
    counted = 0
    while counted < weekdays:
        current += timedelta(days=1)
        if current.weekday() < 5:   # 0=Mon … 4=Fri
            counted += 1
    return current


def upgrade() -> None:
    """Recalculate due_date for all existing loans using 60-weekday rule."""
    conn = op.get_bind()
    loans = conn.execute(text("SELECT id, disbursed_date FROM loans")).fetchall()

    for loan in loans:
        new_due = add_weekdays(loan.disbursed_date, LOAN_TERM_WEEKDAYS)
        conn.execute(
            text("UPDATE loans SET due_date = :due WHERE id = :id"),
            {"due": new_due, "id": loan.id}
        )

    print(f"  Recalculated due_date for {len(loans)} loan(s).")


def downgrade() -> None:
    """Revert to 60 calendar days (best-effort)."""
    conn = op.get_bind()
    conn.execute(text(
        "UPDATE loans SET due_date = disbursed_date + INTERVAL '60 days'"
    ))
