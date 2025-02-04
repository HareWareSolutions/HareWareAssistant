import sys
import os
import pytz
from datetime import datetime, timedelta
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.db import get_db
from models.agendamento import buscar_agendamentos_por_data_ntf
from models.contato import buscar_contato_id
from utils.zapi import send_message_zapi

notificacoes_enviadas = {}


def get_hora_brasil():
    brasil_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(brasil_tz)


def mensagem_env(env, nome, hora):
    match env:
        case 'hareware':
            return (f'Olá, {nome},\n\n'
                    f'Hoje você tem um compromisso marcado com a HareWare às {hora}.\n\n'
                    f'Contamos com a sua presença! até breve!')
        case 'sjoicer':
            return (f'Olá, {nome},\n\n'
                    f'Hoje você tem um compromisso marcado no Salão da Joice às {hora}. \n\n'
                    f'Contamos com a sua presença! até breve!')
        case 'malaman':
            return (f'Olá, {nome},\n\n'
                    f'Hoje você tem um compromisso marcado na barbearia do Malaman às {hora}.\n\n'
                    f'Contamos com a sua presença! até breve!')


def is_round_hour():
    current_time = get_hora_brasil()
    return current_time.minute == 0 and current_time.second == 0


def notificar():
    envs = ['hareware', 'sjoicer']

    while True:
        if is_round_hour():
            agora = get_hora_brasil()
            for agendamento_id, hora_notificada in list(notificacoes_enviadas.items()):
                if agora - hora_notificada > timedelta(hours=1):
                    notificacoes_enviadas.pop(agendamento_id)

            for env in envs:
                db = next(get_db(env))
                try:
                    hoje = agora.date()
                    agendamentos = buscar_agendamentos_por_data_ntf(db, hoje)
                    hora_atual = agora

                    for agendamento in agendamentos:
                        if agendamento.id in notificacoes_enviadas:
                            continue

                        hora_agendada = datetime.combine(hoje, agendamento.hora)
                        hora_agendada = hora_agendada.replace(
                            tzinfo=pytz.timezone('America/Sao_Paulo').localize(datetime.now()).tzinfo
                        )

                        if hora_agendada - timedelta(hours=1) <= hora_atual <= hora_agendada:
                            contato = buscar_contato_id(db, agendamento.contato_id)

                            dados = {
                                'hora': agendamento.hora,
                                'nome_cliente': contato.nome,
                                'celular': contato.numero_celular
                            }

                            mensagem = mensagem_env(env, dados.get('nome_cliente'), dados.get('hora'))

                            send_message_zapi(
                                env=env,
                                number=dados.get('celular'),
                                message=mensagem,
                                delay_typing=2
                            )

                            notificacoes_enviadas[agendamento.id] = agora

                finally:
                    db.close()
        else:
            time.sleep(1)


if __name__ == "__main__":
    notificar()
