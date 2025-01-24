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


def calcular_espera_ate_meia_noite():
    agora = get_hora_brasil()
    proxima_meia_noite = datetime.combine(agora.date() + timedelta(days=1), datetime.min.time(), tzinfo=pytz.timezone('America/Sao_Paulo'))
    return (proxima_meia_noite - agora).total_seconds()


def limpar_agendamentos():
    envs = ['hareware']

    while True:
        espera_segundos = calcular_espera_ate_meia_noite()
        time.sleep(espera_segundos)

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


if __name__ == "__main__":
    limpar_agendamentos()