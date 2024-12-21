import time
import random
from app.models.contato import buscar_contato, criar_contato
from app.models.pedido import buscar_pedido_id, criar_pedido, excluir_pedido, alterar_pedido
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
    db = next(get_db('hareware'))

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
    db = next(get_db('hareware'))

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


def fluxo_conversa_foa(prompt, telefone):
    db = next(get_db('mmania'))

    registro_status = buscar_status(db, telefone)

    registro_contato = buscar_contato(db, telefone)

    if registro_contato is None:

        if registro_status is None:
            novo_status = gravar_status(db, telefone, 'CNC', datetime.now(), None)

            return ("Olá, Seja bem-vindo! Eu sou a atendente virtual da Mmania de Bolo!\n\n"
                    "Percebi que você não está cadastrado na minha lista de contatos, poderia me dizer o seu nome?")

        if registro_status.status == 'CNC': #CNC = Cadastro de Nome de Contato
            if caracteres_numericos(prompt) or caracteres_invalidos(prompt):
                return "Por favor, insira um nome válido."

            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'CNM', datetime.now(), prompt)
            return {'CNM': f'Seu nome é {prompt}?'}

    else:
        if registro_status is None:
            novo_status = gravar_status(db, telefone, 'EAC', datetime.now(), None)
            return {'EAC': ['Ver cardápio', 'Realizar pedido', 'Cancelar pedido'], 'mensagem': f'Olá {registro_contato.nome}!'}

        if registro_status.status == 'IPD': #IPD: Informar pedido
            if registro_status.observacao is None:
                pedido = criar_pedido(db=db, pedido=prompt, entrega=None, data_entrega=None, numero_cliente=telefone, nome_cliente=registro_contato.nome)
            else:
                pedido = buscar_pedido_id(db, int(registro_status.observacao))
                pedido_alterado = alterar_pedido(db, id=pedido.id, pedido=prompt)

            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'CPD', datetime.now(), pedido.id)
            return {'CPD': ['Confirmo meu pedido', 'Quero alterar', 'Desistir do pedido'], 'mensagem': f'Você confirma o seu pedido? \n\n{prompt}'}

        if registro_status.status == 'IED': #IED: Informar endereço
            pedido = buscar_pedido_id(db, int(registro_status.observacao))
            pedido_alterado = alterar_pedido(db, id=pedido.id, entrega=prompt)
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'CED', datetime.now(), pedido.id)
            return {'CED': ['Sim', 'Não'], 'mensagem': f'O seu endereço está correto?\n\n{prompt}'}

        if registro_status.status == 'IDT': #IDT: Informar data
            pedido = buscar_pedido_id(db, int(registro_status.observacao))
            pedido_alterado = alterar_pedido(db, id=pedido.id, data_entrega=prompt)
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'CDT', datetime.now(), pedido.id)
            return {'CDT': ['Sim', 'Não'], 'mensagem': f'Confirma a data de entrega do pedido? \n\n {prompt}'}


def fluxo_conversa_poll_foa(opcao, telefone):
    db = next(get_db('mmania'))

    registro_status = buscar_status(db, telefone)

    registro_contato = buscar_contato(db, telefone)

    if registro_status.status == 'CNM': #CNM: Confirmação de Nome
        if opcao == "Sim":
            nome = registro_status.observacao
            novo_contato = criar_contato(db, nome=registro_status.observacao, numero_celular=telefone, email=None)
            registro_contato = buscar_contato(db, telefone)
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'EAC', datetime.now(), None)
            return {'EAC': ['Ver cardápio', 'Realizar pedido', 'Cancelar pedido'], 'mensagem': f'Prazer em conhecê-lo {nome}!'}
        else:
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'CNC', datetime.now(), None)
            return {"texto": f'Você poderia me dizer o seu nome novamente?'}

    if registro_status.status == 'DRP': #DRP: Deseja realizar agendamento
        if opcao == "Sim":
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'IPD', datetime.now(), None)
            return {"texto": 'Ok! Escreva em uma única mensagem todo o seu pedido'}
        else:
            deletar_status(db, telefone)
            return {'texto': 'Tudo bem! Qualquer coisa é só mandar um oi...'}

    if registro_status.status == 'EAC': #EAC: Escolha de Ação
        if opcao == 'Ver cardápio':
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'DRP', datetime.now(), None)
            return {'DRP': ['Sim', 'Não'], 'cardapio': 'https://drive.google.com/uc?export=download&id=172Xbx55g_pLczsZT0PCjyCfw1cH6rswQ'}
        elif opcao == 'Realizar pedido':
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'IPD', datetime.now(), None)
            return {"opcao2": 'Ok! Escreva em uma única mensagem todo o seu pedido', 'cardapio': 'https://drive.google.com/uc?export=download&id=172Xbx55g_pLczsZT0PCjyCfw1cH6rswQ'}
        elif opcao == 'Cancelar pedido':
            deletar_status(db, telefone)
            return {'texto': 'Para cancelar um pedido ligue para este número: (19) 99670-5890'}
        else:
            deletar_status(db, telefone)
            return {'texto': 'Tudo bem! Qualquer coisa é só mandar um oi...'}

    if registro_status.status == 'CPD': #CPD: Confirmação de pedido
        if opcao == 'Confirmo meu pedido':
            id_pedido = registro_status.observacao
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'ERE', datetime.now(), id_pedido)
            return {'ERE': ['Entrega', 'Retirada'], 'mensagem': 'Você gostaria que seu pedido fosse entregue no endereço ou prefere retirar pessoalmente? Lembrando a entrega só é válida em Araras e está 15 reais.'}
        elif opcao == 'Quero alterar':
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'IPD', datetime.now(), None)
            return {'texto': 'Ok, escreva novamente o seu pedido completo em uma única mensagem'}
        else:
            deletar_status(db, telefone)
            return {'texto': 'Tudo bem! Qualquer coisa é só mandar um oi...'}

    if registro_status.status == 'ERE': #ERE: Escolha de entrega ou retirada
        if opcao == 'Entrega':
            id_pedido = registro_status.observacao
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'IED', datetime.now(), id_pedido)
            return {'texto': 'Certo, me informe o seu endereço'}
        else:
            pedido = buscar_pedido_id(db, int(registro_status.observacao))
            pedido_alterado = alterar_pedido(db, id=pedido.id, entrega='Retirada')
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'IDT', datetime.now(), pedido.id)
            return {'texto': 'Para quando é o pedido? \n(Caso tenha preferencia de horário pode escrever também)'}

    if registro_status.status == 'CED': #CED: Confirmação de endereço
        if opcao == 'Sim':
            id_pedido = int(registro_status.observacao)
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'IDT', datetime.now(), id_pedido)
            return {'texto': 'Para quando é o pedido? \n(Caso tenha preferencia de horário pode escrever também)'}
        else:
            id_pedido = int(registro_status.observacao)
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'IED', datetime.now(), id_pedido)
            return {'texto': 'Me informe o seu endereço novamente.'}

    if registro_status.status == 'CDT':
        if opcao == "Sim":
            id_pedido = int(registro_status.observacao)
            deletar_status(db, telefone)
            pedido = buscar_pedido_id(db, id_pedido)
            return {'finalizado': pedido}
        else:
            id_pedido = int(registro_status.observacao)
            deletar_status(db, telefone)
            novo_status = gravar_status(db, telefone, 'IDT', datetime.now(), id_pedido)
            return {'texto': 'Poderia me informar a data de entrega do pedido novamente?'}
