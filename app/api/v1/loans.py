import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import customer as customer_crud
from app.crud import loan as crud
from app.schemas.loan import LoanCreate, LoanOut, LoanStatusUpdate

VALID_LOAN_STATUSES = {"active", "completed", "overdue", "deactivated"}

router = APIRouter(prefix="/loans", tags=["loans"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=LoanOut, status_code=201)
def create_loan(loan_in: LoanCreate, db: Session = Depends(get_db)):
    customer = customer_crud.get_customer(db, loan_in.customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    existing = crud.get_active_loan_for_customer(db, loan_in.customer_id)
    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Customer already has an active loan ({existing.id})",
        )

    return crud.create_loan(db, loan_in)


@router.get("/", response_model=list[LoanOut])
def list_loans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_loans(db, skip=skip, limit=limit)


@router.get("/{loan_id}", response_model=LoanOut)
def get_loan(loan_id: uuid.UUID, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.put("/{loan_id}/status", response_model=LoanOut)
def update_loan_status(loan_id: uuid.UUID, status_in: LoanStatusUpdate, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return crud.update_loan_status(db, loan, status_in.status)