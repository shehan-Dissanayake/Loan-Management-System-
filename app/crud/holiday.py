from datetime import date as date_type
from sqlalchemy.orm import Session
from app.models.holiday import Holiday
from app.schemas.holiday import HolidayCreate


def get_holidays(db: Session) -> list[Holiday]:
    return db.query(Holiday).order_by(Holiday.date).all()


def get_holiday_dates_set(db: Session) -> set:
    return {h.date for h in db.query(Holiday).all()}


def create_holiday(db: Session, holiday_in: HolidayCreate) -> Holiday:
    holiday = Holiday(**holiday_in.model_dump())
    db.merge(holiday)
    db.commit()
    return db.query(Holiday).filter(Holiday.date == holiday_in.date).first()


def delete_holiday(db: Session, holiday_date: date_type) -> None:
    db.query(Holiday).filter(Holiday.date == holiday_date).delete()
    db.commit()