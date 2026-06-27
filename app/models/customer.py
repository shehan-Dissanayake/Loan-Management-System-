import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    shop_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    owner_name = Column(String, nullable=True)
    address = Column(String, nullable=True)
    nic = Column(String, nullable=True)
    location = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)