from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.debt import Debt
from schemas.debt import (
    DebtCreate,
    DebtResponse,
    DebtResponseWithCustomerId,
    DebtUpdate,
)
from database_file import get_db

router = APIRouter(prefix="/debts", tags=["Debts"])


@router.post("/", response_model=DebtResponse)
def create_debt(debt: DebtCreate, db: Session = Depends(get_db)):
    new_debt = Debt(**debt.model_dump())
    db.add(new_debt)
    db.commit()
    db.refresh(new_debt)
    return new_debt


@router.get("/", response_model=list[DebtResponse])
def get_all_debts(db: Session = Depends(get_db)):
    return db.query(Debt).all()


@router.get("/total")
def get_total_debts(db: Session = Depends(get_db)):
    debts_total = db.query(func.sum(Debt.current_debt)).scalar()
    if debts_total is None:
        raise HTTPException(status_code=404, detail="Debts not found")

    return {"total_debts": debts_total}


@router.get("/{debt_id}", response_model=DebtResponse)
def get_debt(debt_id: int, db: Session = Depends(get_db)):
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return debt


@router.get("/by-customer-id/{customer_id}", response_model=DebtResponseWithCustomerId)
def get_debt(customer_id: str, db: Session = Depends(get_db)):
    debt = db.query(Debt).filter(Debt.customer_id == customer_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return debt


@router.put("/{debt_id}", response_model=DebtResponse)
def update_debt(debt_id: int, debt_data: DebtUpdate, db: Session = Depends(get_db)):
    debt = db.query(Debt).filter(Debt.id == debt_id).first()

    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")

    # Update only the provided fields
    update_data = debt_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(debt, key, value)

    db.commit()
    db.refresh(debt)
    return debt


@router.delete("/{debt_id}")
def delete_debt(debt_id: int, db: Session = Depends(get_db)):
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")

    db.delete(debt)
    db.commit()
    return {"message": "Debt deleted successfully"}
