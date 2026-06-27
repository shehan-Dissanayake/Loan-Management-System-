import uuid
from datetime import date
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.loan import LoanOut
from app.schemas.payment import PaymentOut


class OutstandingLoanItem(BaseModel):
    loan_id: uuid.UUID
    customer_id: uuid.UUID
    shop_name: str
    principal_amount: Decimal
    total_payable: Decimal
    balance_due: Decimal
    installment_amount: Decimal
    due_date: date
    days_remaining: int


class RouteItem(OutstandingLoanItem):
    visited_today: bool


class DailyCollectionItem(BaseModel):
    payment_id: uuid.UUID
    loan_id: uuid.UUID
    customer_id: uuid.UUID
    shop_name: str
    amount_collected: Decimal
    payment_date: date


class DailyCollectionReport(BaseModel):
    date: date
    items: List[DailyCollectionItem]
    total_collected: Decimal


class CashFlowSummary(BaseModel):
    start_date: date
    end_date: date
    total_disbursed: Decimal
    total_collected: Decimal
    net: Decimal


class CustomerLoanHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    loan: LoanOut
    payments: List[PaymentOut]