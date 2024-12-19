import time
import random
from app.models.contato import buscar_contato, criar_contato
from app.models.agendamento import buscar_agendamentos_por_data, gravar_agendamento, buscar_agendamentos_por_contato_id_formatado, buscar_agendamentos_por_contato_id, deletar_agendamento
from app.utils.validacoes import caracteres_invalidos, caracteres_numericos
from app.models.status import buscar_status, gravar_status, deletar_status
from app.utils.rotinasDatas import extrair_data, normalizar_data, transformar_data_e_hora
from app.utils.rotinasHoras import verificar_horarios
from datetime import datetime
from app.db.db import get_db
from app.ia.arc import arc_predict
from app.ia.iia import iia_predict
from app.ia.foundry import send_message_to_ai


def fluxo_conversa(prompt, telefone):
    db = next(get_db())

    registro_status = buscar_status(db, telefone)

    registro_contato = buscar_contato(db, telefone)

    if registro_contato is not None:
        intencao = arc_predict(prompt)

        if intencao == 0 and not registro_status:
            resposta = send_message_to_ai(prompt)
            return resposta
        else:
            if registro_status is None:
                intencao_cancelamento = iia_predict(prompt)

                if intencao_cancelamento == 1:
                    novo_status = gravar_status(db, telefone, "CAG", datetime.now(), None)
                    agendamentos = buscar_agendamentos_por_contato_id_formatado(db, registro_contato.id)
                    if agendamentos is None:
                        deletar_status(db, telefone)
                        return f'Você não tem nenhum horário agendado.'

                    elif len(agendamentos) > 10:
                        agendamentos.sort()
                        opcoes_cancelamento = agendamentos[:10]
                        opcoes_cancelamento.append('Desistir de cancelar agendamento')
                        return {"CAG": opcoes_cancelamento}

                    else:
                        agendamentos.sort()
                        agendamentos.append('Desistir de cancelar agendamento.')
                        return {"CAG": agendamentos}

                novo_status = gravar_status(db, telefone, "IDT", datetime.now(), None)
                return "Certo, poderia me informar uma data?"

            if registro_status.status == 'IDT': #IDT = Informando Data
                data = extrair_data(prompt)

                if data is None:
                    return "Não entendi qual data você deseja agendar, poderia me informar novamente?"

                deletar_status(db, telefone)
                novo_status = gravar_status(db, telefone, "CDT", datetime.now(), str(data))
                data_normalizada = normalizar_data(data)

                return {'CDT': data_normalizada}
    else:
        if registro_status is None:
            novo_status = gravar_status(db, telefone, 'CNC', datetime.now(), None)

            return ("Olá, Seja bem-vindo a central de atendimento da HareWare!\n\n"
                    "Percebi que você não está cadastrado na minha lista de contatos, poderia me dizer o seu nome?")

        if registro_status.status == 'CNC': #CNC = Cadastro de Nome de Contato
            if caracteres_numericos(prompt) or caracteres_invalidos(prompt):
                return "Por favor, insira um nome válido."

            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'CNM', datetime.now(), prompt)
            return {'CNM': f'Seu nome é {prompt}?'}


def fluxo_conversa_poll(opcao, telefone):
    db = next(get_db())

    registro_status = buscar_status(db, telefone)

    registro_contato = buscar_contato(db, telefone)

    if registro_status.status == "CDT": #CDT: Confirmação de data
        if opcao == "Sim":
            data = registro_status.observacao
            data_agendamento = datetime.strptime(data, "%Y-%m-%d").date()
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'IHR', datetime.now(), data)
            agendamentos = buscar_agendamentos_por_data(db, data_agendamento)
            horarios_livres = verificar_horarios(agendamentos)

            if not horarios_livres:
                deletar_status(db, telefone)
                novo_status = gravar_status(db, telefone, 'IDT', datetime.now(), None)
                data_normalizada = normalizar_data(data_agendamento)
                return f'Infelizmente, todos os meus horários para o dia {data_normalizada} já estão preenchidos.\n\nPoderia informar outra data?'
            return {"IHR": horarios_livres}
        else:
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'CDA', datetime.now(), None)
            return {"CDA": 'Ainda deseja agendar algum dia?'}

    elif registro_status.status == "IHR": #IHR: Informar hora
        if opcao != 'Nenhum desses horários é compatível comigo.':
            data_agendamento = datetime.strptime(registro_status.observacao, "%Y-%m-%d").date()
            hora_agendamento = datetime.strptime(opcao, "%H:%M").time()

            data_normalizada = normalizar_data(data_agendamento)

            tempo = random.uniform(1, 3)
            time.sleep(tempo)
            agendamentos = buscar_agendamentos_por_data(db, data_agendamento)
            horarios_disponiveis = verificar_horarios(agendamentos)

            if not horarios_disponiveis:
                deletar_status(db, telefone)
                novo_status = gravar_status(db, telefone, 'IDT', datetime.now(), None)
                return f'Infelizmente, os horários para o dia {data_normalizada} se esgotaram neste exato momento.\n\nPoderia escolher outra data?'

            hora_formatada = hora_agendamento.strftime('%H:%M')

            print(hora_formatada, type(hora_formatada))
            print(horarios_disponiveis, type(horarios_disponiveis), type(horarios_disponiveis[0]))
            if hora_formatada in horarios_disponiveis:
                agendamento = gravar_agendamento(db, data_agendamento, hora_agendamento, registro_contato.id)
                deletar_status(db, telefone)
                return f"Agendamento realizado para o dia {data_normalizada} às {opcao}."
            else:
                data = registro_status.observacao
                data_agendamento = datetime.strptime(data, "%Y-%m-%d").date()
                deletar_status(db, telefone)
                novo_status = gravar_status(db, telefone, 'IHR', datetime.now(), data_agendamento)
                agendamentos = buscar_agendamentos_por_data(db, data)
                horarios_livres = verificar_horarios(agendamentos)

                if not horarios_livres:
                    deletar_status(db, telefone)
                    novo_status = gravar_status(db, telefone, 'IDT', datetime.now(), None)
                    data_normalizada = normalizar_data(data)
                    return f'Infelizmente, os horários para o dia {data_normalizada} se esgotaram neste exato momento.\n\nPoderia escolher outra data?'
                return {"IHR2": horarios_livres}

        else:
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, "IDT", datetime.now(), None)
            return "Tudo bem, poderia me informar uma nova data?"

    elif registro_status.status == 'CDA': #CDA: Confirmação de desejo de agendamento
        deletar_status(db, telefone)

        if opcao == 'Sim':
            novo_status = gravar_status(db, telefone, 'IDT', datetime.now(), None)
            return "Ok, poderia informar a data novamente?"

        return "Ok, em que mais posso ajudá-lo?"

    elif registro_status.status == 'CAG': #CAG: Cancelar agendamento

        if opcao == 'Desistir de cancelar agendamento.':
            deletar_status(db, telefone)
            return "Ok, se precisar de algo, estou à disposição!"

        deletar_status(db, telefone)

        data_cancelamento, hora_cancelamento = transformar_data_e_hora(opcao)

        agendamentos = buscar_agendamentos_por_contato_id(db, registro_contato.id)

        for agendamento in agendamentos:

            if agendamento.get('data') == str(data_cancelamento) and agendamento.get('hora') == str(hora_cancelamento):
                id_agendamento = agendamento['id']
                deletar_agendamento(db, id_agendamento)
                return f'Agendamento cancelado com sucesso, posso te ajudar em mais alguma coisa?'

    elif registro_status.status == 'CNM': #Confirmação de nome
        if opcao == 'Sim':
            nome = registro_status.observacao
            novo_contato = criar_contato(db, nome=registro_status.observacao, numero_celular=telefone, email=None)
            registro_contato = buscar_contato(db, telefone)
            deletar_status(db, telefone)
            return f"Prazer em conhecê-lo {nome}, como posso te ajudar?"
        else:
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'CNC', datetime.now(), None)
            return f'Você poderia me dizer o seu nome novamente?'