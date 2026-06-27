import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Date, Numeric, Integer, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_number = Column(Integer, Sequence('loan_number_seq'), unique=True, nullable=True)  # sequential receipt number
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)

    principal_amount = Column(Numeric(12, 2), nullable=False)

    # Snapshot of the rate/months used for THIS loan, copied at creation time.
    monthly_interest_rate = Column(Numeric(6, 4), nullable=False)
    interest_months = Column(Integer, nullable=False)

    interest_amount = Column(Numeric(12, 2), nullable=False)
    total_payable = Column(Numeric(12, 2), nullable=False)
    installment_amount = Column(Numeric(12, 2), nullable=False)

    disbursed_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)

    status = Column(String, nullable=False, default="active")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)