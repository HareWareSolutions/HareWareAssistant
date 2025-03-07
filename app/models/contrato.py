from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from app.db.db import Base


class Contrato(Base):
    __tablename__ = "contrato"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)
    pagamento = Column(Boolean, nullable=False)
    pacote = Column(String, nullable=False)
    tokens_utilizados = Column(Integer, nullable=False, default=0)
    data_ultimo_pagamento = Column(Date, nullable=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    assistant_id = Column(String, nullable=True)
    api_key_ia = Column(String, nullable=True)

    cliente = relationship("Cliente")


async def criar_contrato(
    db: AsyncSession,
    tipo: str,
    pagamento: bool,
    pacote: str,
    tokens_utilizados: int,
    data_ultimo_pagamento,
    id_cliente: int,
    assistant_id: str = None,
    api_key_ia: str = None,
):
    novo_contrato = Contrato(
        tipo=tipo,
        pagamento=pagamento,
        pacote=pacote,
        tokens_utilizados=tokens_utilizados,
        data_ultimo_pagamento=data_ultimo_pagamento,
        id_cliente=id_cliente,
        assistant_id=assistant_id,
        api_key_ia=api_key_ia,
    )
    db.add(novo_contrato)
    await db.commit()
    await db.refresh(novo_contrato)
    return novo_contrato


async def editar_contrato(
    db: AsyncSession,
    contrato_id: int,
    tipo: str = None,
    pagamento: bool = None,
    pacote: str = None,
    tokens_utilizados: int = None,
    data_ultimo_pagamento=None,
    assistant_id: str = None,
    api_key_ia: str = None,
):
    result = await db.execute(select(Contrato).filter(Contrato.id == contrato_id))
    contrato = result.scalar_one_or_none()

    if contrato:
        if tipo is not None:
            contrato.tipo = tipo
        if pagamento is not None:
            contrato.pagamento = pagamento
        if pacote is not None:
            contrato.pacote = pacote
        if tokens_utilizados is not None:
            contrato.tokens_utilizados = tokens_utilizados
        if data_ultimo_pagamento is not None:
            contrato.data_ultimo_pagamento = data_ultimo_pagamento
        if assistant_id is not None:
            contrato.assistant_id = assistant_id
        if api_key_ia is not None:
            contrato.api_key_ia = api_key_ia

        await db.commit()
        await db.refresh(contrato)
        return contrato
    return None


async def listar_contratos(db: AsyncSession):
    result = await db.execute(select(Contrato))
    return result.scalars().all()


async def deletar_contrato(db: AsyncSession, contrato_id: int):
    result = await db.execute(select(Contrato).filter(Contrato.id == contrato_id))
    contrato = result.scalar_one_or_none()

    if contrato:
        await db.delete(contrato)
        await db.commit()
        return True
    return False


async def buscar_contrato_por_id(db: AsyncSession, contrato_id: int):
    result = await db.execute(select(Contrato).filter(Contrato.id == contrato_id))
    return result.scalar_one_or_none()


async def buscar_contrato_por_id_cliente(db: AsyncSession, id_cliente: int):
    result = await db.execute(select(Contrato).filter(Contrato.id_cliente == id_cliente))
    return result.scalars().all()
