from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cpf = Column(String, nullable=False, unique=True)
    company_name = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)

    appointments = relationship("Appointment", back_populates="customer")
