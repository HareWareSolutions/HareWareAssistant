from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from app.db.db import Base


class Pedido(Base):
    __tablename__ = "pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido = Column(String, nullable=True)
    entrega = Column(String, nullable=True)
    data_entrega = Column(String, nullable=True)
    numero_cliente = Column(String, nullable=True)
    nome_cliente = Column(String, nullable=True)


def criar_pedido(db: Session, pedido: str = None, entrega: str = None, data_entrega: str = None, numero_cliente: str = None,
                 nome_cliente: str = None):
    novo_pedido = Pedido(
        pedido=pedido,
        entrega=entrega,
        data_entrega=data_entrega,
        numero_cliente=numero_cliente,
        nome_cliente=nome_cliente
    )
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)
    return novo_pedido


def listar_pedidos(db: Session):
    return db.query(Pedido).all()


def buscar_pedido(db: Session, numero_cliente: str):
    return db.query(Pedido).filter(Pedido.numero_cliente == numero_cliente).all()


def buscar_pedido_id(db: Session, id: int):
    return db.query(Pedido).filter(Pedido.id == id).first()


def alterar_pedido(db: Session, id: int, pedido: str = None, entrega: str = None, data_entrega: str = None, numero_cliente: str = None,
                   nome_cliente: str = None):
    pedido_existente = db.query(Pedido).filter(Pedido.id == id).first()

    if not pedido_existente:
        return None

    if pedido is not None:
        pedido_existente.pedido = pedido
    if entrega is not None:
        pedido_existente.entrega = entrega
    if data_entrega is not None:
        pedido_existente.data_entrega = data_entrega
    if numero_cliente is not None:
        pedido_existente.numero_cliente = numero_cliente
    if nome_cliente is not None:
        pedido_existente.nome_cliente = nome_cliente

    db.commit()
    db.refresh(pedido_existente)
    return pedido_existente


def excluir_pedido(db: Session, id: int):
    pedido_existente = db.query(Pedido).filter(Pedido.id == id).first()

    if not pedido_existente:
        return None

    db.delete(pedido_existente)
    db.commit()
    return pedido_existente
