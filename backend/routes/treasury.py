from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.treasury import TreasuryOperation
from schemas.treasury import TreasuryOperationCreate, TreasuryOperationResponse
from database_file import get_db


router = APIRouter(prefix="/treasury_operations", tags=["Treasury Operations"])


@router.post("/", response_model=TreasuryOperationResponse)
def create_treasury_operation(
    treasury: TreasuryOperationCreate, db: Session = Depends(get_db)
):
    new_operation = TreasuryOperation(**treasury.dict())
    db.add(new_operation)
    db.commit()
    db.refresh(new_operation)
    return new_operation


@router.get("/", response_model=list[TreasuryOperationResponse])
def get_all_treasury_operations(db: Session = Depends(get_db)):
    return db.query(TreasuryOperation).all()
