from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from app.db.db import Base


class Status(Base):
    __tablename__ = "status"

    id = Column(Integer, primary_key=True, index=True)
    numero_celular = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False)
    hora = Column(String, nullable=False)
    observacao = Column(String, nullable=True)
    observacao2 = Column(String, nullable=True)


def gravar_status(db: Session, numero_celular: str, status: str, hora: str, observacao: str, observacao2: str):
    novo_status = Status(numero_celular=numero_celular, status=status, hora=hora, observacao=observacao, observacao2=observacao2)
    db.add(novo_status)
    db.commit()
    db.refresh(novo_status)
    return novo_status


def deletar_status(db: Session, numero_celular: str):
    status = db.query(Status).filter(Status.numero_celular == numero_celular).first()
    if status:
        db.delete(status)
        db.commit()
        return True
    return False


def buscar_status(db: Session, numero_celular: str):
    return db.query(Status).filter(Status.numero_celular == numero_celular).first()
