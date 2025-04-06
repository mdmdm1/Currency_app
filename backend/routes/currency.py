from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from utils.audit_logger import log_audit_entry
from database_file import get_db
from models.currency import Currency
from schemas.currency import (
    CurrencyConversionRequest,
    CurrencyResponse,
    CurrencyCreate,
    CurrencyUpdate,
)

router = APIRouter(prefix="/currencies", tags=["Currencies"])


@router.post("/", response_model=CurrencyResponse)
def create_currency(currency: CurrencyCreate, db: Session = Depends(get_db)):
    # Check if the currency or code already exists
    existing_currency = (
        db.query(Currency)
        .filter((Currency.name == currency.name) | (Currency.code == currency.code))
        .first()
    )
    if existing_currency:
        raise HTTPException(status_code=400, detail="Currency or code already exists")

    # Create a new currency
    new_currency = Currency(**currency.dict())
    db.add(new_currency)
    db.commit()
    db.refresh(new_currency)
    return new_currency


@router.get("/total")
def get_total_currencies(db: Session = Depends(get_db)):
    currency_total = db.query(func.sum(Currency.balance / Currency.rate)).scalar()
    if currency_total is None:
        raise HTTPException(status_code=404, detail="Currencies not found")

    return {"total_currencies": currency_total}


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

    # Update amounts

    if currency_data.input is not None:
        currency.input += currency_data.input

    if currency_data.output is not None:
        currency.output += currency_data.output

    if currency_data.input is not None or currency_data.output is not None:
        currency.balance = (
            currency.balance + (currency_data.input or 0) - (currency_data.output or 0)
        )

    if currency_data.rate is not None:
        currency.rate = currency_data.rate
    db.commit()
    db.refresh(currency)
    return currency


@router.get("/", response_model=list[CurrencyResponse])
def get_all_currencies(db: Session = Depends(get_db)):
    return db.query(Currency).all()


@router.post("/convert")
def convert_currency(
    conversion_data: CurrencyConversionRequest, db: Session = Depends(get_db)
):
    """Handle currency conversion and save the transaction."""
    source_currency = (
        db.query(Currency)
        .filter(Currency.code == conversion_data.source_currency)
        .first()
    )
    target_currency = (
        db.query(Currency)
        .filter(Currency.code == conversion_data.target_currency)
        .first()
    )

    if not source_currency or not target_currency:
        raise HTTPException(status_code=404, detail="Currency not found")

    # Check if target currency has sufficient balance
    if conversion_data.converted_amount > target_currency.balance:
        raise HTTPException(
            status_code=400, detail="Insufficient balance in target currency"
        )

    # Update amounts
    target_currency.balance -= conversion_data.converted_amount
    target_currency.output += conversion_data.converted_amount

    source_currency.balance += conversion_data.amount
    source_currency.input += conversion_data.amount

    # Log audit entry
    log_audit_entry(
        db_session=db,
        table_name="Currency",
        operation="EXCHANGE",
        record_id=target_currency.id,
        user_id=conversion_data.user_id,
        changes={
            "old": {
                "source": source_currency.code,
                "target": target_currency.code,
                "source_balance": source_currency.balance,
                "target_balance": target_currency.balance,
            },
            "new": {
                "source": source_currency.code,
                "target": target_currency.code,
                "source_balance": source_currency.balance + conversion_data.amount,
                "target_balance": target_currency.balance
                - conversion_data.converted_amount,
            },
        },
    )

    db.commit()
    return {"message": "Conversion successful"}


@router.delete("/{currency_id}")
def delete_currency(currency_id: int, db: Session = Depends(get_db)):
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")

    db.delete(currency)
    db.commit()
    return {"message": "Currency deleted successfully"}
