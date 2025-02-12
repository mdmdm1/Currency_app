from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.deposit import Deposit
from schemas.deposit import DepositCreate, DepositResponse
from database_file import get_db


router = APIRouter(prefix="/deposits", tags=["Deposits"])


@router.post("/", response_model=DepositResponse)
def create_deposit(deposit: DepositCreate, db: Session = Depends(get_db)):
    new_deposit = Deposit(**deposit.model_dump())
    db.add(new_deposit)
    db.commit()
    db.refresh(new_deposit)
    return new_deposit


@router.get("/", response_model=list[DepositResponse])
def get_all_deposits(db: Session = Depends(get_db)):
    return db.query(Deposit).all()
