from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship, Session
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


def criar_contrato(
    db: Session,
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
    db.commit()
    db.refresh(novo_contrato)
    return novo_contrato


def editar_contrato(
    db: Session,
    contrato_id: int,
    tipo: str = None,
    pagamento: bool = None,
    pacote: str = None,
    tokens_utilizados: int = None,
    data_ultimo_pagamento=None,
    assistant_id: str = None,
    api_key_ia: str = None,
):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
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
        db.commit()
        db.refresh(contrato)
        return contrato
    return None


def listar_contratos(db: Session):
    return db.query(Contrato).all()


def deletar_contrato(db: Session, contrato_id: int):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if contrato:
        db.delete(contrato)
        db.commit()
        return True
    return False


def buscar_contrato_por_id(db: Session, contrato_id: int):
    return db.query(Contrato).filter(Contrato.id == contrato_id).first()


def buscar_contrato_por_id_cliente(db: Session, id_cliente: int):
    return db.query(Contrato).filter(Contrato.id_cliente == id_cliente).all()

