from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database_file import get_db
from models.currency import Currency
from schemas.currency import CurrencyResponse, CurrencyCreate

router = APIRouter(prefix="/currencies", tags=["Currencies"])


@router.post("/", response_model=CurrencyResponse)
def create_currency(currency: CurrencyCreate, db: Session = Depends(get_db)):
    new_currency = Currency(**currency.dict())
    db.add(new_currency)
    db.commit()
    db.refresh(new_currency)
    return new_currency


@router.get("/", response_model=list[CurrencyResponse])
def get_all_currencies(db: Session = Depends(get_db)):
    return db.query(Currency).all()
