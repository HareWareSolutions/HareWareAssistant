from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Boolean
from sqlalchemy.orm import Session, relationship
from app.db.db import Base
from datetime import datetime
import pytz


class Agendamento(Base):
    __tablename__ = 'agendamento'

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    contato_id = Column(Integer, ForeignKey('contato.id', ondelete="CASCADE"), nullable=False)
    confirmacao = Column(Boolean, default=False)

    contato = relationship("Contato", back_populates="agendamentos")


def gravar_agendamento(db: Session, data, hora, contato_id: int, confirmacao: bool = False):
    novo_agendamento = Agendamento(data=data, hora=hora, contato_id=contato_id, confirmacao=confirmacao)
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
    agendamentos = db.query(Agendamento).filter(Agendamento.data == data).all()
    return agendamentos


def buscar_agendamentos_por_data_api(db: Session, data):
    data_formatada = datetime.strptime(data, "%d/%m/%Y").date()

    agendamentos = db.query(
        Agendamento.id,
        Agendamento.data,
        Agendamento.hora,
        Agendamento.contato_id,
        Agendamento.confirmacao
    ).filter(Agendamento.data == data_formatada).all()

    return [
        {
            "id_agendamento": agendamento.id,
            "data": agendamento.data,
            "hora": agendamento.hora,
            "id_contato": agendamento.contato_id,
            "confirmacao": agendamento.confirmacao
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
            "hora": agendamento.hora.strftime("%H:%M:%S"),
            "confirmacao": agendamento.confirmacao
        }
        for agendamento in agendamentos
    ]


def buscar_agendamentos_por_contato_id_formatado(db: Session, contato_id: int):
    fuso_brasileiro = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_brasileiro)

    agendamentos = (
        db.query(Agendamento)
        .filter(
            Agendamento.contato_id == contato_id,
            (Agendamento.data > agora.date()) |
            ((Agendamento.data == agora.date()) & (Agendamento.hora > agora.time()))
        )
        .all()
    )

    if not agendamentos:
        return None

    return [
        f"{agendamento.data.strftime('%d/%m/%Y')} {agendamento.hora.strftime('%H:%M')}"
        for agendamento in agendamentos
    ]


def deletar_agendamento_por_data_hora(db: Session, data: str, hora: str):
    data_formatada = datetime.strptime(data, "%d/%m/%Y").date()
    hora_formatada = datetime.strptime(hora, "%H:%M").time()

    agendamento = db.query(Agendamento).filter(
        Agendamento.data == data_formatada,
        Agendamento.hora == hora_formatada
    ).first()

    if not agendamento:
        raise ValueError("Nenhum agendamento encontrado para a data e hora especificadas.")

    db.delete(agendamento)
    db.commit()

    return {"message": "Agendamento cancelado com sucesso."}


def alterar_confirmacao_agendamento(db: Session, agendamento_id: int, confirmacao: bool):
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not agendamento:
        raise ValueError("Agendamento não encontrado.")
    agendamento.confirmacao = confirmacao
    db.commit()
    db.refresh(agendamento)
    return agendamento


def buscar_agendamento_por_id(db: Session, agendamento_id: int):
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()

    if not agendamento:
        raise ValueError("Agendamento não encontrado.")

    return {
        "id_agendamento": agendamento.id,
        "data": agendamento.data.strftime("%Y-%m-%d"),
        "hora": agendamento.hora.strftime("%H:%M:%S"),
        "id_contato": agendamento.contato_id,
        "confirmacao": agendamento.confirmacao
    }

