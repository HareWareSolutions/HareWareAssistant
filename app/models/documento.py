from sqlalchemy import Column, Integer, String, LargeBinary
from app.db.db import Base


class Documento(Base):
    __tablename__ = 'documento'
    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
