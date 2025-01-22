from datetime import datetime, timedelta
from app.db.db import get_db
from app.models.agendamento import buscar_agendamentos_por_data
from app.models.contato import buscar_contato_id
from app.utils.zapi import send_message_zapi


def mensagem_env(env, nome, hora):
    match env:
        case 'hareware':
            return (f'Olá, {nome},\n\n'
                    f'Hoje você tem um compromisso marcado com a HareWare às {hora}.\n\n'
                    f'Contamos com a sua presença! até breve!')
        case 'joice':
            return (f'Olá, {nome},\n\n'
                    f'Hoje você tem um compromisso marcado no Salão da Joice às {hora}. \n\n'
                    f'Contamos com a sua presença! até breve!')
        case 'malaman':
            return (f'Olá, {nome},\n\n'
                    f'Hoje você tem um compromisso marcado na barbearia do Malaman às {hora}.\n\n'
                    f'Contamos com a sua presença! até breve!')


def is_round_hour():
    current_time = datetime.now()
    return current_time.minute == 0 and current_time.second == 0


def notificar():
    envs = ['hareware', 'malaman', 'joice']

    while True:
        if is_round_hour():
            for env in envs:
                db = next(get_db(env))
                try:
                    hoje = datetime.now().date()
                    agendamentos = buscar_agendamentos_por_data(db, hoje)
                    hora_atual = datetime.now()

                    for agendamento in agendamentos:
                        hora_agendada = datetime.strptime(agendamento, "%H:%M:%S")

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

                finally:
                    db.close()


notificar()
