from sqlalchemy.orm import Session
from customers_models import Customer


def create_customer(db: Session, name: str, phone: str, email: str = None):
    new_customer = Customer(name=name, phone=phone, email=email)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


def get_customers(db: Session):
    return db.query(Customer).all()
