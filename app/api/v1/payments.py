import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import loan as loan_crud
from app.crud import payment as crud
from app.schemas.payment import PaymentCreate, PaymentOut, PaymentUpdate
from app.schemas.loan import LoanSummary

router = APIRouter(tags=["payments"], dependencies=[Depends(get_current_user)])


@router.post("/payments/", response_model=PaymentOut, status_code=201)
def create_payment(payment_in: PaymentCreate, db: Session = Depends(get_db)):
    loan = loan_crud.get_loan(db, payment_in.loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Loan is already '{loan.status}' — cannot record further payments",
        )
    return crud.create_payment(db, loan, payment_in)


@router.get("/loans/{loan_id}/payments", response_model=list[PaymentOut])
def list_payments_for_loan(loan_id: uuid.UUID, db: Session = Depends(get_db)):
    loan = loan_crud.get_loan(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return crud.get_payments_for_loan(db, loan_id)


@router.put("/loans/{loan_id}/payments/{payment_id}", response_model=PaymentOut)
def update_payment(loan_id: uuid.UUID, payment_id: uuid.UUID, payment_in: PaymentUpdate, db: Session = Depends(get_db)):
    loan = loan_crud.get_loan(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    updated = crud.update_payment(
        db,
        loan_id=loan_id,
        payment_id=payment_id,
        amount_collected=payment_in.amount_collected,
        payment_date=payment_in.payment_date,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return updated


@router.delete("/loans/{loan_id}/payments/{payment_id}", status_code=204)
def delete_payment(loan_id: uuid.UUID, payment_id: uuid.UUID, db: Session = Depends(get_db)):
    loan = loan_crud.get_loan(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    deleted = crud.delete_payment(db, loan_id=loan_id, payment_id=payment_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return None


@router.get("/loans/{loan_id}/summary", response_model=LoanSummary)
def get_loan_summary(loan_id: uuid.UUID, db: Session = Depends(get_db)):
    loan = loan_crud.get_loan(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return crud.get_loan_summary(db, loan)