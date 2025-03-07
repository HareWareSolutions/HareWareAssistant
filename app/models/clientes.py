from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.db import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    empresa = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    cpfcnpj = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    ativo = Column(Boolean, nullable=False)


async def criar_cliente(db: AsyncSession, nome: str, empresa: str, email: str, telefone: str, cpfcnpj: str, senha: str, ativo: bool):
    novo_cliente = Cliente(
        nome=nome,
        empresa=empresa,
        email=email,
        telefone=telefone,
        cpfcnpj=cpfcnpj,
        senha=senha,
        ativo=ativo
    )
    db.add(novo_cliente)
    await db.commit()
    await db.refresh(novo_cliente)
    return novo_cliente


async def listar_clientes(db: AsyncSession):
    result = await db.execute(select(Cliente))
    return result.scalars().all()


async def buscar_cliente(db: AsyncSession, cliente_id: int):
    result = await db.execute(select(Cliente).filter(Cliente.id == cliente_id))
    return result.scalar_one_or_none()


async def buscar_cliente_nome(db: AsyncSession, nome: str):
    result = await db.execute(select(Cliente).filter(Cliente.nome.ilike(f"%{nome}%")))
    return result.scalars().all()


async def deletar_cliente(db: AsyncSession, cliente_id: int):
    cliente = await db.execute(select(Cliente).filter(Cliente.id == cliente_id))
    cliente = cliente.scalar_one_or_none()
    if cliente:
        await db.delete(cliente)
        await db.commit()
        return True
    return False


async def buscar_cliente_cpfcnpj(db: AsyncSession, cpfcnpj: str):
    result = await db.execute(select(Cliente).filter(Cliente.cpfcnpj == cpfcnpj))
    return result.scalar_one_or_none()


async def buscar_cliente_email(db: AsyncSession, email: str):
    result = await db.execute(select(Cliente).filter(Cliente.email == email))
    return result.scalar_one_or_none()


async def editar_clientes(db: AsyncSession, cliente_id: int, **kwargs):
    result = await db.execute(select(Cliente).filter(Cliente.id == cliente_id))
    cliente = result.scalar_one_or_none()
    if not cliente:
        return None

    for key, value in kwargs.items():
        if hasattr(cliente, key):
            setattr(cliente, key, value)

    await db.commit()
    await db.refresh(cliente)
    return cliente
