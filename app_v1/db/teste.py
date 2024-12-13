from db import engine, Base
from appointments_models import Appointment
from customers_models import Customer

Base.metadata.create_all(bind=engine)
