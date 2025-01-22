from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time
from sqlalchemy.orm import Session, relationship
from app.db.db import Base
from datetime import datetime


class Agendamento(Base):
    __tablename__ = 'agendamento'

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    contato_id = Column(Integer, ForeignKey('contato.id'), nullable=False)

    contato = relationship("Contato", back_populates="agendamento")


def gravar_agendamento(db: Session, data, hora, contato_id: int):
    novo_agendamento = Agendamento(data=data, hora=hora, contato_id=contato_id)
    db.add(novo_agendamento)
    db.commit()
    db.refresh(novo_agendamento)
    return novo_agendamento


def deletar_agendamento(db: Session, agendamento_id: int):
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not agendamento:
        raise ValueError("Agendamento não encontrado.")
    db.delete(agendamento)
    db.commit()
    return {"message": "Agendamento deletado com sucesso."}


def buscar_agendamentos_por_data(db: Session, data):
    agendamentos = db.query(Agendamento.hora).filter(Agendamento.data == data).all()
    agendamentos = [agendamento[0].strftime("%H:%M:%S") for agendamento in agendamentos]
    return agendamentos


def buscar_agendamentos_por_data_ntf(db: Session, data):
    agendamentos = db.query(Agendamento).filter(Agendamento.data == data).all()  # Retorna objetos completos
    return agendamentos


def buscar_agendamentos_por_data_api(db: Session, data):
    data_formatada = datetime.strptime(data, "%d/%m/%Y").date()

    agendamentos = db.query(
        Agendamento.id,
        Agendamento.data,
        Agendamento.hora,
        Agendamento.contato_id
    ).filter(Agendamento.data == data_formatada).all()

    return [
        {
            "id_agendamento": agendamento.id,
            "data": agendamento.data,
            "hora": agendamento.hora,
            "id_contato": agendamento.contato_id
        }
        for agendamento in agendamentos
    ]


def buscar_agendamentos_por_contato_id(db: Session, contato_id: int):
    agendamentos = db.query(Agendamento).filter(Agendamento.contato_id == contato_id).all()
    if not agendamentos:
        return None
    return [
        {
            "id": agendamento.id,
            "data": agendamento.data.strftime("%Y-%m-%d"),
            "hora": agendamento.hora.strftime("%H:%M:%S")
        }
        for agendamento in agendamentos
    ]


def buscar_agendamentos_por_contato_id_formatado(db: Session, contato_id: int):
    agendamentos = db.query(Agendamento).filter(Agendamento.contato_id == contato_id).all()
    if not agendamentos:
        return None
    return [
        f"{agendamento.data.strftime('%d/%m/%Y')} {agendamento.hora.strftime('%H:%M')}"
        for agendamento in agendamentos
    ]