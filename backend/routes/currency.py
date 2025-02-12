from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database_file import get_db
from models.currency import Currency
from schemas.currency import CurrencyResponse, CurrencyCreate, CurrencyUpdate

router = APIRouter(prefix="/currencies", tags=["Currencies"])


@router.post("/", response_model=CurrencyResponse)
def create_currency(currency: CurrencyCreate, db: Session = Depends(get_db)):
    new_currency = Currency(**currency.dict())
    db.add(new_currency)
    db.commit()
    db.refresh(new_currency)
    return new_currency


@router.get("/{currency_id}", response_model=CurrencyResponse)
def get_currency(currency_id: int, db: Session = Depends(get_db)):
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Customer not found")
    return currency


@router.put("/{currency_id}", response_model=CurrencyResponse)
def update_currency(
    currency_id: int, currency_data: CurrencyUpdate, db: Session = Depends(get_db)
):
    currency = db.query(Currency).filter(Currency.id == currency_id).first()

    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")

    # Update only the provided fields
    for key, value in currency_data.model_dump(exclude_unset=True).items():
        setattr(currency, key, value)

    db.commit()
    db.refresh(currency)
    return currency


@router.get("/", response_model=list[CurrencyResponse])
def get_all_currencies(db: Session = Depends(get_db)):
    return db.query(Currency).all()
