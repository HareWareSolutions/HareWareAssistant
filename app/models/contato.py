from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship, Session
from app.db.db import Base


class Contato(Base):
    __tablename__ = "contato"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    numero_celular = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True)
    pausa = Column(Boolean, default=False)

    agendamentos = relationship("Agendamento", back_populates="contato", cascade="all, delete-orphan")


def criar_contato(db: Session, nome: str, numero_celular: str, email: str = None, pausa: bool = False):
    novo_contato = Contato(nome=nome, numero_celular=numero_celular, email=email, pausa=pausa)
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
    return False


def editar_contato(db: Session, id: int, nome: str = None, numero_celular: str = None, email: str = None, pausa: bool = None):
    contato = db.query(Contato).filter(Contato.id == id).first()

    if contato:
        if nome:
            contato.nome = nome
        if numero_celular:
            contato.numero_celular = numero_celular
        if email:
            contato.email = email
        if pausa is not None:
            contato.pausa = pausa

        db.commit()
        db.refresh(contato)
        return contato
    else:
        return None
