from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerResponse
from database_file import get_db

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    new_customer = Customer(**customer.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


@router.get("/total")
def get_total_customers(db: Session = Depends(get_db)):
    customers_total = db.query(func.count(Customer.id)).scalar()
    if customers_total is None:
        raise HTTPException(status_code=404, detail="Currencies not found")

    return {"total_customers": customers_total}


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_by_id(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/by-identite/{customer_identite}", response_model=CustomerResponse)
def get_customer_by_identite(customer_identite: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.identite == customer_identite).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/", response_model=list[CustomerResponse])
def get_all_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}
