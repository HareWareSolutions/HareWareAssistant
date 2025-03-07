from sqlalchemy import Column, Integer, String, LargeBinary, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.db import Base


class Documento(Base):
    __tablename__ = 'documento'
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    quantidade_tokens = Column(Integer, nullable=False)
    pdf_original = Column(LargeBinary, nullable=False)
    pdf_processado = Column(LargeBinary, nullable=False)


async def gravar_documento(db: AsyncSession, titulo: str, quantidade_tokens: int, pdf_original: bytes, pdf_processado: bytes):
    novo_documento = Documento(titulo=titulo, quantidade_tokens=quantidade_tokens, pdf_original=pdf_original, pdf_processado=pdf_processado)
    db.add(novo_documento)
    await db.commit()
    await db.refresh(novo_documento)
    return novo_documento


async def ler_documentos(db: AsyncSession):
    result = await db.execute(select(Documento))
    return result.scalars().all()


async def ler_documento(db: AsyncSession, id: int):
    result = await db.execute(select(Documento).filter(Documento.id == id))
    return result.scalar_one_or_none()


async def somar_quantidade_tokens(db: AsyncSession):
    result = await db.execute(select(func.sum(Documento.quantidade_tokens)))
    return result.scalar_one_or_none()
