import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    loan_id: uuid.UUID
    amount_collected: Decimal = Field(..., gt=0, description="Amount collected must be greater than 0")
    payment_date: Optional[date] = None  # defaults to today if omitted


class PaymentUpdate(BaseModel):
    amount_collected: Optional[Decimal] = Field(None, gt=0, description="Amount collected must be greater than 0")
    payment_date: Optional[date] = None


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    loan_id: uuid.UUID
    amount_collected: Decimal
    payment_date: date
    balance_after_payment: Decimal
    created_at: datetime