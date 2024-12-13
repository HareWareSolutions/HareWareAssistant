from sqlalchemy import Column, Integer, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from db import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)

    customer = relationship("Customer", back_populates="appointments")
    user = relationship("User", back_populates="appointments")
