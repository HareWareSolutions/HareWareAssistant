from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.db import Base


class Status(Base):
    __tablename__ = "status"

    id = Column(Integer, primary_key=True, index=True)
    numero_celular = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False)
    hora = Column(String, nullable=False)
    observacao = Column(String, nullable=True)
    observacao2 = Column(String, nullable=True)


async def gravar_status(db: AsyncSession, numero_celular: str, status: str, hora: str, observacao: str, observacao2: str):
    novo_status = Status(numero_celular=numero_celular, status=status, hora=hora, observacao=observacao, observacao2=observacao2)
    db.add(novo_status)
    await db.commit()
    await db.refresh(novo_status)
    return novo_status


async def deletar_status(db: AsyncSession, numero_celular: str):
    result = await db.execute(select(Status).filter(Status.numero_celular == numero_celular))
    status = result.scalars().first()
    if status:
        await db.delete(status)
        await db.commit()
        return True
    return False


async def buscar_status(db: AsyncSession, numero_celular: str):
    result = await db.execute(select(Status).filter(Status.numero_celular == numero_celular))
    return result.scalars().first()
