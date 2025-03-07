from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.db import Base


class Pedido(Base):
    __tablename__ = "pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido = Column(String, nullable=True)
    entrega = Column(String, nullable=True)
    data_entrega = Column(String, nullable=True)
    numero_cliente = Column(String, nullable=True)
    nome_cliente = Column(String, nullable=True)


async def criar_pedido(db: AsyncSession, pedido: str = None, entrega: str = None, data_entrega: str = None, numero_cliente: str = None,
                        nome_cliente: str = None):
    novo_pedido = Pedido(
        pedido=pedido,
        entrega=entrega,
        data_entrega=data_entrega,
        numero_cliente=numero_cliente,
        nome_cliente=nome_cliente
    )
    db.add(novo_pedido)
    await db.commit()
    await db.refresh(novo_pedido)
    return novo_pedido


async def listar_pedidos(db: AsyncSession):
    result = await db.execute(select(Pedido))
    return result.scalars().all()


async def buscar_pedido(db: AsyncSession, numero_cliente: str):
    result = await db.execute(select(Pedido).filter(Pedido.numero_cliente == numero_cliente))
    return result.scalars().all()


async def buscar_pedido_id(db: AsyncSession, id: int):
    result = await db.execute(select(Pedido).filter(Pedido.id == id))
    return result.scalar_one_or_none()


async def alterar_pedido(db: AsyncSession, id: int, pedido: str = None, entrega: str = None, data_entrega: str = None, numero_cliente: str = None,
                          nome_cliente: str = None):
    result = await db.execute(select(Pedido).filter(Pedido.id == id))
    pedido_existente = result.scalar_one_or_none()

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

    await db.commit()
    await db.refresh(pedido_existente)
    return pedido_existente


async def excluir_pedido(db: AsyncSession, id: int):
    result = await db.execute(select(Pedido).filter(Pedido.id == id))
    pedido_existente = result.scalar_one_or_none()

    if not pedido_existente:
        return None

    await db.delete(pedido_existente)
    await db.commit()
    return pedido_existente
