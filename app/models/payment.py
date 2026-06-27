import uuid
from datetime import datetime, date as date_type

from sqlalchemy import Column, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"), nullable=False)

    amount_collected = Column(Numeric(12, 2), nullable=False)
    payment_date = Column(Date, nullable=False, default=date_type.today)

    # Snapshot, calculated once at entry time, never recalculated later —
    # this is what guarantees the printed receipt always matches the DB.
    balance_after_payment = Column(Numeric(12, 2), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)