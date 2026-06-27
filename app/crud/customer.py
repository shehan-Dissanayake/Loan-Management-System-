import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


def get_customer(db: Session, customer_id: uuid.UUID) -> Optional[Customer]:
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100) -> list[Customer]:
    return db.query(Customer).order_by(Customer.shop_name).offset(skip).limit(limit).all()


def create_customer(db: Session, customer_in: CustomerCreate) -> Customer:
    data = customer_in.model_dump(exclude_unset=True)
    if data.get("id") is None:
        data.pop("id", None)

    customer = Customer(**data)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer: Customer, customer_in: CustomerUpdate) -> Customer:
    updates = customer_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer: Customer) -> None:
    db.delete(customer)
    db.commit()