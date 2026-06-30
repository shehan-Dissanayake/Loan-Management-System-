from datetime import date as date_type
from typing import Optional
from pydantic import BaseModel, ConfigDict


class HolidayCreate(BaseModel):
    date: date_type
    description: Optional[str] = None


class HolidayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    date: date_type
    description: Optional[str] = None