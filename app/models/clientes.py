from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Session
from app.db.db import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    empresa = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    cpfcnpj = Column(String, nullable=False)
    ativo = Column(Boolean, nullable=False)


def criar_cliente(db: Session, nome: str, empresa: str, email: str, telefone: str, cpfcnpj: str, ativo: bool):
    novo_cliente = Cliente(
        nome=nome,
        empresa=empresa,
        email=email,
        telefone=telefone,
        cpfcnpj=cpfcnpj,
        ativo=ativo
    )
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return novo_cliente


def listar_clientes(db: Session):
    return db.query(Cliente).all()


def buscar_cliente(db: Session, cliente_id: int):
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()


def buscar_cliente_nome(db: Session, nome: str):
    return db.query(Cliente).filter(Cliente.nome.ilike(f"%{nome}%")).all()


def deletar_cliente(db: Session, cliente_id: int):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente:
        db.delete(cliente)
        db.commit()
        return True
    return False


def buscar_cliente_cpfcnpj(db: Session, cpfcnpj: str):
    return db.query(Cliente).filter(Cliente.cpfcnpj == cpfcnpj).first()

