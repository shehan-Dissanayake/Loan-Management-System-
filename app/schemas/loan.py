import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class LoanCreate(BaseModel):
    # Only what the lender actually decides. Everything else (interest,
    # total payable, installment, due date) is calculated server-side.
    customer_id: uuid.UUID
    principal_amount: Decimal
    disbursed_date: Optional[date] = None  # defaults to today if omitted


class LoanStatusUpdate(BaseModel):
    status: Literal["active", "completed", "overdue", "deactivated"]


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    loan_number: Optional[int] = None
    customer_id: uuid.UUID
    principal_amount: Decimal
    monthly_interest_rate: Decimal
    interest_months: int
    interest_amount: Decimal
    total_payable: Decimal
    installment_amount: Decimal
    disbursed_date: date
    due_date: date
    status: str
    created_at: datetime

class LoanSummary(LoanOut):
    """LoanOut plus computed, real-time figures — used for the field collection screen and the receipt."""
    balance_due: Decimal
    arrears_count: int
    arrears_amount: Decimal