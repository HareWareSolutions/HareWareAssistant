from sqlalchemy.orm import Session
from appointments_models import Appointment


def create_appointment(db: Session, customer_id: int, date, time):
    new_appointment = Appointment(customer_id=customer_id, date=date, time=time)
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


def get_appointments_by_customer(db: Session, customer_id: int):
    return db.query(Appointment).filter(Appointment.customer_id == customer_id).all()


def get_appointments_by_date(db: Session, date):
    return db.query(Appointment).filter(Appointment.date == date).all()
