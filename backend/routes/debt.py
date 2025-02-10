from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.debt import Debt
from schemas.debt import DebtCreate, DebtResponse
from database_file import get_db

router = APIRouter(prefix="/debts", tags=["Debts"])


@router.post("/", response_model=DebtResponse)
def create_debt(debt: DebtCreate, db: Session = Depends(get_db)):
    new_debt = Debt(**debt.dict())
    db.add(new_debt)
    db.commit()
    db.refresh(new_debt)
    return new_debt


@router.get("/", response_model=list[DebtResponse])
def get_all_debts(db: Session = Depends(get_db)):
    return db.query(Debt).all()
