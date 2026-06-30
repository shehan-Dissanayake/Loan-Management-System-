from datetime import date as date_type
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import holiday as crud
from app.schemas.holiday import HolidayCreate, HolidayOut

router = APIRouter(prefix="/holidays", tags=["holidays"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[HolidayOut])
def list_holidays(db: Session = Depends(get_db)):
    return crud.get_holidays(db)


@router.post("/", response_model=HolidayOut, status_code=201)
def create_holiday(holiday_in: HolidayCreate, db: Session = Depends(get_db)):
    return crud.create_holiday(db, holiday_in)


@router.delete("/{holiday_date}", status_code=204)
def delete_holiday(holiday_date: date_type, db: Session = Depends(get_db)):
    crud.delete_holiday(db, holiday_date)