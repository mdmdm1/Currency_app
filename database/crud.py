from sqlalchemy.orm import Session
from database.models import Customer, Deposit


def get_customer_by_name(db: Session, name: str):
    return db.query(Customer).filter(Customer.name == name).first()


def create_customer(db: Session, name: str):
    customer = Customer(name=name)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def create_deposit(db: Session, person_name: str, amount: float, deposit_date: str):
    customer = get_customer_by_name(db, person_name)
    if not customer:
        customer = create_customer(db, person_name)

    deposit = Deposit(
        person_name=person_name,
        amount=amount,
        deposit_date=deposit_date,
        customer_id=customer.id,
    )
    db.add(deposit)
    db.commit()
    db.refresh(deposit)
    return deposit
