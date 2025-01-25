from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Session
from app.db.db import Base


class Contato(Base):
    __tablename__ = "contato"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    numero_celular = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True)

    agendamento = relationship("Agendamento", back_populates="contato")


def criar_contato(db: Session, nome: str, numero_celular: str, email: str = None):
    novo_contato = Contato(nome=nome, numero_celular=numero_celular, email=email)
    db.add(novo_contato)
    db.commit()
    db.refresh(novo_contato)
    return novo_contato


def listar_contatos(db: Session):
    return db.query(Contato).all()


def buscar_contato(db: Session, numero_celular: str):
    return db.query(Contato).filter(Contato.numero_celular == numero_celular).first()


def buscar_contato_id(db: Session, id: int):
    return db.query(Contato).filter(Contato.id == id).first()


def deletar_contato(db: Session, id: int):
    contato = db.query(Contato).filter(Contato.id == id).first()

    if contato:
        db.delete(contato)
        db.commit()
        return True
    else:
        return False


