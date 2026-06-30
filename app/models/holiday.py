from sqlalchemy import Column, Date, String
from app.core.database import Base


class Holiday(Base):
    __tablename__ = "holidays"

    date = Column(Date, primary_key=True)
    description = Column(String, nullable=True)