import sys
import os
import pytz
from datetime import datetime, timedelta
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.db import get_db
from models.agendamento import buscar_agendamentos_por_data_ntf, deletar_agendamento


def get_hora_brasil():
    brasil_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(brasil_tz)


def limpar_agendamentos():
    envs = ['hareware']

    while True:
        agora = get_hora_brasil()
        if agora.strftime("%H:%M:%S") == '00:00:00':
            for env in envs:
                db = next(get_db(env))
                try:
                    agendamentos = buscar_agendamentos_por_data_ntf(db, agora.date())

                    for agendamento in agendamentos:
                        if agendamento.data < agora.date():
                            deletar_agendamento(db, agendamento.id)

                except Exception as e:
                    print(f"Erro ao limpar agendamentos: {e}")
                finally:
                    db.close()

        time.sleep(60)
