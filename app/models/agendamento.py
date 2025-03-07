from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
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
    observacao = Column(String, nullable=True)

    contato = relationship("Contato", back_populates="agendamentos")


async def gravar_agendamento(db: AsyncSession, data, hora, contato_id: int, confirmacao: bool = False, observacao: str = None):
    novo_agendamento = Agendamento(data=data, hora=hora, contato_id=contato_id, confirmacao=confirmacao, observacao=observacao)
    db.add(novo_agendamento)
    await db.commit()
    await db.refresh(novo_agendamento)
    return novo_agendamento


async def deletar_agendamento(db: AsyncSession, agendamento_id: int):
    agendamento = await db.execute(db.query(Agendamento).filter(Agendamento.id == agendamento_id))
    agendamento = agendamento.scalar_one_or_none()
    if not agendamento:
        raise ValueError("Agendamento não encontrado.")
    await db.delete(agendamento)
    await db.commit()
    return {"message": "Agendamento deletado com sucesso."}


async def buscar_agendamentos_por_data(db: AsyncSession, data):
    agendamentos = await db.execute(db.query(Agendamento.hora).filter(Agendamento.data == data))
    agendamentos = [agendamento[0].strftime("%H:%M:%S") for agendamento in agendamentos]
    return agendamentos


async def buscar_agendamentos_por_data_ntf(db: AsyncSession, data):
    agendamentos = await db.execute(db.query(Agendamento).filter(Agendamento.data == data))
    return agendamentos.scalars().all()


async def buscar_agendamentos_por_data_api(db: AsyncSession, data):
    data_formatada = datetime.strptime(data, "%d/%m/%Y").date()

    agendamentos = await db.execute(
        db.query(
            Agendamento.id,
            Agendamento.data,
            Agendamento.hora,
            Agendamento.contato_id,
            Agendamento.confirmacao,
            Agendamento.observacao
        ).filter(Agendamento.data == data_formatada)
    )

    return [
        {
            "id_agendamento": agendamento.id,
            "data": agendamento.data,
            "hora": agendamento.hora,
            "id_contato": agendamento.contato_id,
            "confirmacao": agendamento.confirmacao,
            "observacao": agendamento.observacao
        }
        for agendamento in agendamentos.scalars().all()
    ]


async def buscar_agendamentos_por_contato_id(db: AsyncSession, contato_id: int):
    agendamentos = await db.execute(db.query(Agendamento).filter(Agendamento.contato_id == contato_id))
    agendamentos = agendamentos.scalars().all()
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


async def buscar_agendamentos_por_contato_id_formatado(db: AsyncSession, contato_id: int):
    fuso_brasileiro = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_brasileiro)

    agendamentos = await db.execute(
        db.query(Agendamento)
        .filter(
            Agendamento.contato_id == contato_id,
            (Agendamento.data > agora.date()) |
            ((Agendamento.data == agora.date()) & (Agendamento.hora > agora.time()))
        )
    )

    agendamentos = agendamentos.scalars().all()

    if not agendamentos:
        return None

    return [
        f"{agendamento.data.strftime('%d/%m/%Y')} {agendamento.hora.strftime('%H:%M')}"
        for agendamento in agendamentos
    ]


async def deletar_agendamento_por_data_hora(db: AsyncSession, data: str, hora: str):
    data_formatada = datetime.strptime(data, "%d/%m/%Y").date()
    hora_formatada = datetime.strptime(hora, "%H:%M").time()

    agendamento = await db.execute(
        db.query(Agendamento).filter(
            Agendamento.data == data_formatada,
            Agendamento.hora == hora_formatada
        )
    )
    agendamento = agendamento.scalar_one_or_none()

    if not agendamento:
        raise ValueError("Nenhum agendamento encontrado para a data e hora especificadas.")

    await db.delete(agendamento)
    await db.commit()

    return {"message": "Agendamento cancelado com sucesso."}


async def alterar_confirmacao_agendamento(db: AsyncSession, agendamento_id: int, confirmacao: bool):
    agendamento = await db.execute(db.query(Agendamento).filter(Agendamento.id == agendamento_id))
    agendamento = agendamento.scalar_one_or_none()
    if not agendamento:
        raise ValueError("Agendamento não encontrado.")
    agendamento.confirmacao = confirmacao
    await db.commit()
    await db.refresh(agendamento)
    return agendamento


async def buscar_agendamento_por_id(db: AsyncSession, agendamento_id: int):
    agendamento = await db.execute(db.query(Agendamento).filter(Agendamento.id == agendamento_id))
    agendamento = agendamento.scalar_one_or_none()

    if not agendamento:
        raise ValueError("Agendamento não encontrado.")

    return {
        "id_agendamento": agendamento.id,
        "data": agendamento.data.strftime("%Y-%m-%d"),
        "hora": agendamento.hora.strftime("%H:%M:%S"),
        "id_contato": agendamento.contato_id,
        "confirmacao": agendamento.confirmacao
    }
