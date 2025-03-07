from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from app.db.db import Base


class Contato(Base):
    __tablename__ = "contato"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    numero_celular = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True)
    pausa = Column(Boolean, default=False)

    agendamentos = relationship("Agendamento", back_populates="contato", cascade="all, delete-orphan")


async def criar_contato(db: AsyncSession, nome: str, numero_celular: str, email: str = None, pausa: bool = False):
    novo_contato = Contato(nome=nome, numero_celular=numero_celular, email=email, pausa=pausa)
    db.add(novo_contato)
    await db.commit()
    await db.refresh(novo_contato)
    return novo_contato


async def listar_contatos(db: AsyncSession):
    result = await db.execute(select(Contato))
    return result.scalars().all()


async def buscar_contato(db: AsyncSession, numero_celular: str):
    result = await db.execute(select(Contato).filter(Contato.numero_celular == numero_celular))
    return result.scalar_one_or_none()


async def buscar_contato_id(db: AsyncSession, id: int):
    result = await db.execute(select(Contato).filter(Contato.id == id))
    return result.scalar_one_or_none()


async def deletar_contato(db: AsyncSession, id: int):
    result = await db.execute(select(Contato).filter(Contato.id == id))
    contato = result.scalar_one_or_none()

    if contato:
        await db.delete(contato)
        await db.commit()
        return True
    return False


async def editar_contato(db: AsyncSession, id: int, nome: str = None, numero_celular: str = None, email: str = None, pausa: bool = None):
    result = await db.execute(select(Contato).filter(Contato.id == id))
    contato = result.scalar_one_or_none()

    if contato:
        if nome:
            contato.nome = nome
        if numero_celular:
            contato.numero_celular = numero_celular
        if email:
            contato.email = email
        if pausa is not None:
            contato.pausa = pausa

        await db.commit()
        await db.refresh(contato)
        return contato
    else:
        return None
