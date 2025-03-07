import sys
import os
import pytz
from datetime import datetime, timedelta
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.db import get_db
from models.agendamento import buscar_agendamentos_por_data_ntf
from models.contato import buscar_contato_id
from models.status import deletar_status, gravar_status
from utils.zapi import send_poll_zapi
from utils.rotinasDatas import normalizar_data

notificacoes_enviadas = {}


async def get_hora_brasil():
    brasil_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(brasil_tz)


async def mensagem_env(env, nome, hora, data):
    match env:
        case 'hareware':
            return (f'Olá, {nome},\n\n'
                    f'Você tem um compromisso marcado com a HareWare no dia {data} às {hora}.\n\n'
                    f'Você confirma a sua presença?')
        case 'emyconsultorio':
            return (f'Olá, {nome},\n\n'
                    f'Você tem uma consulta agendada com a Dra. Eminy Bezerra no dia {data} às {hora}. \n\n'
                    f'A clínica está localizada em Araras-SP, na Rua Marechal Deodoro, 704 - Centro, CEP 13600-110.\n\n'
                    f'Você confirma a sua presença?')


async def notificar():
    envs = ['hareware', 'emyconsultorio']

    while True:
        agora = await get_hora_brasil()
        for agendamento_id, hora_notificada in list(notificacoes_enviadas.items()):
            if agora - hora_notificada > timedelta(days=1):
                notificacoes_enviadas.pop(agendamento_id)

        for env in envs:
            async with get_db(env) as db:
                try:
                    hoje = agora.date()
                    agendamentos = await buscar_agendamentos_por_data_ntf(db, hoje)
                    hora_atual = agora
                    limite = hora_atual + timedelta(hours=3)

                    for agendamento in agendamentos:
                        hora_agendada = datetime.combine(hoje, agendamento.hora)
                        hora_agendada = hora_agendada.replace(
                            tzinfo=pytz.timezone('America/Sao_Paulo').localize(datetime.now()).tzinfo
                        )

                        if hora_atual <= hora_agendada <= limite and agendamento.id not in notificacoes_enviadas and agendamento.confirmacao != True:
                            contato = await buscar_contato_id(db, agendamento.contato_id)

                            data_normalizada = normalizar_data(agendamento.data)

                            dados = {
                                'id': agendamento.id,
                                'hora': agendamento.hora,
                                'data': data_normalizada,
                                'nome_cliente': contato.nome,
                                'celular': contato.numero_celular
                            }

                            mensagem = await mensagem_env(env, dados.get('nome_cliente'), dados.get('hora'), dados.get('data'))

                            await deletar_status(db, dados.get('celular'))
                            hora_atual_status = datetime.now().time().strftime("%H:%M:%S")
                            status = gravar_status(db, dados.get('celular'), 'CPA', hora_atual_status, dados.get('id'), None)

                            opcoes = ['Sim', 'Não']

                            options = [{'name': opcao} for opcao in opcoes]

                            await send_poll_zapi(
                                env=env,
                                number=dados.get('celular'),
                                question=mensagem,
                                options=options
                            )

                            notificacoes_enviadas[agendamento.id] = agora
                except Exception as e:
                    print("status: error ", "message", str(e))
                #finally:
                #    db.close()

        time.sleep(3600)

if __name__ == "__main__":
    notificar()
