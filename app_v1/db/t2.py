from db import get_db
from appointments_crud import create_appointment, get_appointments_by_customer
from customer_crud import create_customer, get_customers
from sqlalchemy.orm import Session
from datetime import date, time

db: Session = next(get_db())

customer = create_customer(db, name="John Doe", phone="123456789", email="john.doe@example.com")
print(f"Customer created: {customer}")

appointment = create_appointment(db, customer_id=customer.id, date=date(2024, 12, 5), time=time(14, 30))
print(f"Appointment created: {appointment}")

customers = get_customers(db)
print(f"All customers: {customers}")

appointments = get_appointments_by_customer(db, customer_id=customer.id)
print(f"Appointments for {customer.name}: {appointments}")
