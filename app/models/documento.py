from sqlalchemy import Column, Integer, String, LargeBinary, func
from sqlalchemy.orm import Session
from app.db.db import Base


class Documento(Base):
    __tablename__ = 'documento'
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    quantidade_tokens = Column(Integer, nullable=False)
    pdf_original = Column(LargeBinary, nullable=False)
    pdf_processado = Column(LargeBinary, nullable=False)


def gravar_documento(db: Session, titulo: str, quantidade_tokens: int, pdf_original: bytes, pdf_processado: bytes):
    novo_documento = Documento(titulo=titulo, quantidade_tokens=quantidade_tokens, pdf_original=pdf_original, pdf_processado=pdf_processado)
    db.add(novo_documento)
    db.commit()
    db.refresh(novo_documento)
    return novo_documento


def ler_documentos(db: Session):
    return db.query(Documento).all()


def ler_documento(db: Session, id: int):
    return db.query(Documento).filter(Documento.id == id).first()


def somar_quantidade_tokens(db: Session):
    soma = db.query(func.sum(Documento.quantidade_tokens)).scalar()
    return soma
