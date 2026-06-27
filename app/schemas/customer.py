import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    shop_name: str
    phone: str
    owner_name: Optional[str] = None
    address: Optional[str] = None
    nic: Optional[str] = None
    location: Optional[str] = None


class CustomerCreate(CustomerBase):
    id: Optional[uuid.UUID] = None


class CustomerUpdate(BaseModel):
    shop_name: Optional[str] = None
    phone: Optional[str] = None
    owner_name: Optional[str] = None
    address: Optional[str] = None
    nic: Optional[str] = None
    location: Optional[str] = None


class CustomerOut(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime