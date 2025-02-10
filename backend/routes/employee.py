from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.employee import Employee
from schemas.employee import EmployeeCreate, EmployeeResponse
from database_file import get_db


router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("/", response_model=EmployeeResponse)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    new_employee = Employee(**employee.dict())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


@router.get("/", response_model=list[EmployeeResponse])
def get_all_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()
