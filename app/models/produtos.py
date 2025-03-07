from sqlalchemy import Column, Integer, String, LargeBinary, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.db import Base


class Produto(Base):
    __tablename__ = 'produto'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    texto_promocional = Column(String, nullable=True)
    imagem_1 = Column(LargeBinary, nullable=True)
    imagem_2 = Column(LargeBinary, nullable=True)
    imagem_3 = Column(LargeBinary, nullable=True)
    ativo = Column(Boolean, default=True)
    acesso = Column(Integer, nullable=False, default=0)


async def criar_produto(db: AsyncSession, nome: str, descricao: str, texto_promocional: str = None,
                        imagem_1: bytes = None,
                        imagem_2: bytes = None, imagem_3: bytes = None, ativo: bool = True, acesso: int = 0):
    novo_produto = Produto(
        nome=nome,
        descricao=descricao,
        texto_promocional=texto_promocional,
        imagem_1=imagem_1,
        imagem_2=imagem_2,
        imagem_3=imagem_3,
        ativo=ativo,
        acesso=acesso
    )
    db.add(novo_produto)
    await db.commit()
    await db.refresh(novo_produto)
    return novo_produto


async def buscar_produto_por_id(db: AsyncSession, produto_id: int):
    result = await db.execute(select(Produto).filter(Produto.id == produto_id))
    return result.scalar_one_or_none()


async def buscar_produtos(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Produto).offset(skip).limit(limit))
    return result.scalars().all()


async def deletar_produto(db: AsyncSession, produto_id: int):
    result = await db.execute(select(Produto).filter(Produto.id == produto_id))
    produto = result.scalar_one_or_none()
    if produto:
        await db.delete(produto)
        await db.commit()
        return produto
    return None


async def alterar_produto(db: AsyncSession, produto_id: int, nome: str = None, descricao: str = None,
                          texto_promocional: str = None, imagem_1: bytes = None, imagem_2: bytes = None,
                          imagem_3: bytes = None, ativo: bool = None, acesso: int = None):
    result = await db.execute(select(Produto).filter(Produto.id == produto_id))
    produto = result.scalar_one_or_none()

    if produto:
        if nome:
            produto.nome = nome
        if descricao:
            produto.descricao = descricao
        if texto_promocional:
            produto.texto_promocional = texto_promocional
        if imagem_1:
            produto.imagem_1 = imagem_1
        if imagem_2:
            produto.imagem_2 = imagem_2
        if imagem_3:
            produto.imagem_3 = imagem_3
        if ativo is not None:
            produto.ativo = ativo
        if acesso is not None:
            produto.acesso = acesso

        await db.commit()
        await db.refresh(produto)
        return produto
    return None
