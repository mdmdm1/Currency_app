from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.deposit import Deposit
from schemas.deposit import (
    DepositCreate,
    DepositResponse,
    DepositResponseWithCustomerId,
    DepositUpdate,
)
from database_file import get_db


router = APIRouter(prefix="/deposits", tags=["Deposits"])


@router.post("/", response_model=DepositResponse)
def create_deposit(deposit: DepositCreate, db: Session = Depends(get_db)):
    new_deposit = Deposit(**deposit.model_dump())
    db.add(new_deposit)
    db.commit()
    db.refresh(new_deposit)
    return new_deposit


@router.get(
    "/by-customer-id/{customer_id}", response_model=DepositResponseWithCustomerId
)
def get_deposit(customer_id: str, db: Session = Depends(get_db)):
    deposit = db.query(Deposit).filter(Deposit.customer_id == customer_id).first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    return deposit


@router.get("/", response_model=list[DepositResponse])
def get_all_deposits(db: Session = Depends(get_db)):
    return db.query(Deposit).all()


@router.put("/{deposit_id}", response_model=DepositResponse)
def update_deposit(
    deposit_id: int, deposit_data: DepositUpdate, db: Session = Depends(get_db)
):
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()

    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    # Update only the provided fields
    update_data = deposit_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(deposit, key, value)

    db.commit()
    db.refresh(deposit)
    return deposit


@router.get("/total")
def get_total_deposits(db: Session = Depends(get_db)):
    deposits_total = db.query(func.sum(Deposit.current_debt)).scalar()
    if deposits_total is None:
        raise HTTPException(status_code=404, detail="Deposits not found")

    return {"total_deposits": deposits_total}


@router.delete("/{deposit_id}")
def delete_deposit(deposit_id: int, db: Session = Depends(get_db)):
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    db.delete(deposit)
    db.commit()
    return {"message": "Deposit deleted successfully"}
