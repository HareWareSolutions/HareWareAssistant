import time
import random
from app.ia.gptOpenAi import ask_to_openai
from app.models.contato import buscar_contato, criar_contato
from app.models.pedido import buscar_pedido_id, criar_pedido, excluir_pedido, alterar_pedido
from app.models.agendamento import buscar_agendamentos_por_data, gravar_agendamento, buscar_agendamentos_por_contato_id_formatado, buscar_agendamentos_por_contato_id, deletar_agendamento, alterar_confirmacao_agendamento
from app.utils.validacoes import caracteres_invalidos, caracteres_numericos
from app.models.status import buscar_status, gravar_status, deletar_status
from app.utils.rotinasDatas import extrair_data, normalizar_data, transformar_data_e_hora
from app.utils.capturador import predicoes_arc, predicoes_iia
from app.utils.rotinasHoras import verificar_horarios
from app.utils.identificarDiaSemana import dia_da_semana
from datetime import datetime
from app.db.db import get_db
from app.ia.arc import arc_predict
from app.ia.iia import iia_predict
from app.ia.foundry import send_message_to_ai
from app.utils.zapi import send_message_zapi
import pytz


async def fluxo_conversa(env, prompt, telefone, nome_contato: str = None, id_contrato: int = None):
    async with get_db(env) as db:
        registro_status = await buscar_status(db, telefone)

        registro_contato = await buscar_contato(db, telefone)

        if registro_contato is None:
            novo_contato = await criar_contato(db, nome=nome_contato, numero_celular=telefone, email=None, pausa=False)
            registro_contato = await buscar_contato(db, telefone)

        if registro_contato is not None:
            if registro_contato.pausa == True:
                return {"PAUSA": "Contato em pausa de conversa."}

            intencao = await arc_predict(prompt)

            predicoes_arc(prompt, intencao)

            if intencao == 0 and not registro_status:
                resposta = await ask_to_openai(id_contrato, prompt)
                return resposta
            else:
                if registro_status is None:
                    intencao_cancelamento = await iia_predict(prompt)

                    predicoes_iia(prompt, intencao_cancelamento)

                    if intencao_cancelamento == 1:
                        predicoes_iia(prompt, intencao_cancelamento)
                        hora_atual = datetime.now().time().strftime("%H:%M:%S")
                        novo_status = await gravar_status(db, telefone, "CAG", hora_atual, None, None)
                        agendamentos = await buscar_agendamentos_por_contato_id_formatado(db, registro_contato.id)
                        if agendamentos is None:
                            await deletar_status(db, telefone)
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

                    if env == 'emyconsultorio':
                        hora_atual = datetime.now().time().strftime("%H:%M:%S")
                        novo_status = await gravar_status(db, telefone, "EPC", hora_atual, None, None)
                        print("retornei a lista")

                        return {"EPC": ["Profilaxia Dental (Limpeza)", "Clareamento a Laser (Em consultório)", "Restauração em Resina", "Extração de Dente", "Raspagem Gengival", "Atendimento Infantil", "Assessoria em Aleitamento Materno", "Outro"]}
                    else:
                        hora_atual = datetime.now().time().strftime("%H:%M:%S")
                        novo_status = await gravar_status(db, telefone, "IDT", hora_atual, None, None)

                        if env == 'emyconsultorio':
                            mensagem_retorno = ('Perfeito! Agora, por favor, informe uma data no formato dia/mês.\n\n'
                                                'Lembre-se, o agendamento aqui não há custo. \n\nPessoalmente, a Dra. Eminy explicará todos os detalhes que você precisa saber! 😀')
                        else:
                            mensagem_retorno = "Ótimo! Agora, escolha a data que for mais conveniente para você.\n\n Escreva no formato Dia/Mês"

                        return mensagem_retorno

                if registro_status.status == 'OPC': # OPC: Outro procedimento
                    procedimento = prompt
                    await deletar_status(db, telefone)
                    hora_atual = datetime.now().time().strftime("%H:%M:%S")
                    novo_status = await gravar_status(db, telefone, "IDT", hora_atual, None, procedimento)

                    if env == 'emyconsultorio':
                        mensagem_retorno = ('Perfeito! Agora, por favor, informe uma data no formato dia/mês.\n\n'
                                             'Lembre-se, o agendamento aqui não há custo. \n\nPessoalmente, a Dra. Eminy explicará todos os detalhes que você precisa saber! 😀')
                    else:
                        mensagem_retorno = "Ótimo! Agora, escolha a data que for mais conveniente para você.\n\n Escreva no formato Dia/Mês"

                    return mensagem_retorno

                if registro_status.status == 'IDT':  # IDT = Informando Data

                    if registro_status.observacao2 is not None:
                        escolha_procedimento = registro_status.observacao2
                    else:
                        escolha_procedimento = None

                    fuso_brasileiro = pytz.timezone('America/Sao_Paulo')
                    data_atual = datetime.now(fuso_brasileiro)

                    data = await extrair_data(prompt)

                    if data is None:
                        return "Data não encontrada ou inválida"

                    data_extraida = datetime.combine(data, datetime.min.time(), fuso_brasileiro)

                    if data_extraida.date() < data_atual.date():
                        await deletar_status(db, telefone)
                        hora_atual = datetime.now().time().strftime("%H:%M:%S")
                        novo_status = await gravar_status(db, telefone, "IDT", hora_atual, None, escolha_procedimento)
                        return "A data informada é anterior à data de hoje. Por favor escolha outra data..."

                    if data is None:
                        await deletar_status(db, telefone)
                        hora_atual = datetime.now().time().strftime("%H:%M:%S")
                        novo_status = await gravar_status(db, telefone, "IDT", hora_atual, None, escolha_procedimento)
                        return "Não entendi qual data você deseja agendar, poderia me informar novamente?"

                    dia_semana = await dia_da_semana(data)

                    if (env == 'emyconsultorio' or env == 'hareware') and (dia_semana == 'domingo' or dia_semana == 'sÃ¡bado' or dia_semana == 'sábado' or dia_semana == 'sabado'):
                        return "Desculpa, infelizmente não trabalhamos aos finais de semana, poderia informar outra data?"

                    await deletar_status(db, telefone)
                    hora_atual = datetime.now().time().strftime("%H:%M:%S")
                    novo_status = await gravar_status(db, telefone, "CDT", hora_atual, str(data), escolha_procedimento)
                    data_normalizada = await normalizar_data(data)

                    return {'CDT': data_normalizada}
        else:
            if registro_status is None:
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'CNC', hora_atual, None, None)

                if env == 'hareware':
                    return ("Olá, Seja bem-vindo a central de atendimento HareWare!\n\n"
                            "Percebi que você não está cadastrado na minha lista de contatos, poderia me dizer o seu nome?")
                elif env == 'malaman':
                    return ("E aí, parça! Seja bem-vindo à Barbearia do Malaman!\n\n"
                            "Não achei você na minha lista de contatos, qual é o seu nome, mano?")
                elif env == 'sjoicer':
                    return ("Olá, Seja bem-vinda (o) ao WhatsApp oficial da Joice Carolina Cílios!\n\n"
                            "Percebi que você não está cadastrada (o) na minha lista de contatos, poderia me dizer o seu nome?")

            if registro_status.status == 'CNC': #CNC = Cadastro de Nome de Contato
                if await caracteres_numericos(prompt) or await caracteres_invalidos(prompt):
                    return "Por favor, insira um nome válido."

                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'CNM', hora_atual, prompt, None)
                return {'CNM': f'Seu nome é {prompt}?'}


async def fluxo_conversa_poll(env, opcao, telefone):
    async with get_db(env) as db:
        registro_status = await buscar_status(db, telefone)
        print(registro_status.status)

        registro_contato = await buscar_contato(db, telefone)
        if registro_contato.pausa == True:
            return {"PAUSA": "Contato em pausa de conversa."}

        if registro_status.status == "CDT": #CDT: Confirmação de data

            if registro_status.observacao2 is not None:
                escolha_procedimento = registro_status.observacao2
            else:
                escolha_procedimento = None

            if opcao == "Sim":
                data = registro_status.observacao
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'IHR', hora_atual, data, escolha_procedimento)

                data_agendamento = datetime.strptime(data, "%Y-%m-%d").date()
                agendamentos = await buscar_agendamentos_por_data(db, data_agendamento)

                data_normalizada = await normalizar_data(data_agendamento)

                horarios_livres = await verificar_horarios(env, agendamentos, data_normalizada)

                if not horarios_livres:
                    await deletar_status(db, telefone)
                    hora_atual = datetime.now().time().strftime("%H:%M:%S")
                    novo_status = await gravar_status(db, telefone, 'IDT', hora_atual, None, escolha_procedimento)
                    data_normalizada = await normalizar_data(data_agendamento)
                    return f'Infelizmente, todos os meus horários para o dia {data_normalizada} já estão preenchidos.\n\nPoderia informar outra data?'
                return {"IHR": horarios_livres}
            else:
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'CDA', hora_atual, None, escolha_procedimento)
                return {"CDA": 'Ainda deseja agendar algum dia?'}

        elif registro_status.status == "EPC": # EPC: Escolha de Procedimento
            await deletar_status(db, telefone)
            if opcao != 'Outro':
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, "IDT", hora_atual, None, opcao)

                if env == 'emyconsultorio':
                    mensagem_retorno = ('Perfeito! Agora, por favor, informe uma data no formato dia/mês.\n\n'
                                        'Lembre-se, o agendamento aqui não há custo. \n\nPessoalmente, a Dra. Eminy explicará todos os detalhes que você precisa saber! 😀')
                else:
                    mensagem_retorno = "Ótimo! Agora, escolha a data que for mais conveniente para você.\n\n Escreva no formato Dia/Mês"

                return mensagem_retorno
            else:
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, "OPC", hora_atual, None, None)
                return "Ótimo! Poderia me informar, em poucas palavras, qual é o principal objetivo da sua consulta?"

        elif registro_status.status == "IHR": #IHR: Informar hora

            if registro_status.observacao2 is not None:
                escolha_procedimento = registro_status.observacao2
            else:
                escolha_procedimento = None

            if opcao != 'Nenhum desses horários é compatível comigo.':
                data_agendamento = datetime.strptime(registro_status.observacao, "%Y-%m-%d").date()
                data_normalizada = await normalizar_data(data_agendamento)
                hora_agendamento = datetime.strptime(opcao, "%H:%M").time()

                data_normalizada = await normalizar_data(data_agendamento)

                tempo = random.uniform(1, 3)
                time.sleep(tempo)
                agendamentos = await buscar_agendamentos_por_data(db, data_agendamento)

                horarios_disponiveis = await verificar_horarios(env, agendamentos, data_normalizada)

                if not horarios_disponiveis:
                    await deletar_status(db, telefone)
                    hora_atual = datetime.now().time().strftime("%H:%M:%S")
                    novo_status = await gravar_status(db, telefone, 'IDT', hora_atual, None, escolha_procedimento)
                    return f'Infelizmente, os horários para o dia {data_normalizada} se esgotaram neste exato momento.\n\nPoderia escolher outra data?'

                hora_formatada = hora_agendamento.strftime('%H:%M')

                if hora_formatada in horarios_disponiveis:
                    agendamento = await gravar_agendamento(db, data_agendamento, hora_agendamento, registro_contato.id, False, escolha_procedimento)
                    await deletar_status(db, telefone)

                    if env == 'hareware':
                        numero_cliente = ['5519997581672', '5519995869852']
                        notificacao_cliente = f'{registro_contato.nome} marcou um horário para o dia {data_normalizada} às {opcao}.'
                    elif env == 'emyconsultorio':
                        numero_cliente = ['5513991701738']
                        notificacao_cliente = f'{registro_contato.nome} marcou um horário para o dia {data_normalizada} às {opcao}, procedimento: {escolha_procedimento}.'

                    for n_cliente in numero_cliente:

                        await send_message_zapi(
                            env=env,
                            number=n_cliente,
                            message=notificacao_cliente
                        )

                    if env == 'emyconsultorio':
                        mensagem_agendamento = (f'Estou feliz por você ter dado este passo importante para seu autocuidado 😍🙏\n\n'
                                                f'Agendamento realizado para o dia {data_normalizada} às {opcao}.')
                    elif env == 'hareware':
                        mensagem_agendamento = f'Agendamento realizado para o dia {data_normalizada} às {opcao}.'

                    return mensagem_agendamento
                else:
                    data = registro_status.observacao
                    data_agendamento = datetime.strptime(data, "%Y-%m-%d").date()
                    await deletar_status(db, telefone)
                    hora_atual = datetime.now().time().strftime("%H:%M:%S")
                    novo_status = await gravar_status(db, telefone, 'IHR', hora_atual, data_agendamento, escolha_procedimento)
                    agendamentos = await buscar_agendamentos_por_data(db, data)

                    horarios_livres = await verificar_horarios(env, agendamentos, data_normalizada)

                    if not horarios_livres:
                        await deletar_status(db, telefone)
                        hora_atual = datetime.now().time().strftime("%H:%M:%S")
                        novo_status = await gravar_status(db, telefone, 'IDT', hora_atual, None, escolha_procedimento)
                        data_normalizada = await normalizar_data(data)
                        return f'Infelizmente, os horários para o dia {data_normalizada} se esgotaram neste exato momento.\n\nPoderia escolher outra data?'
                    return {"IHR2": horarios_livres}

            else:
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, "IDT", hora_atual, None, escolha_procedimento)
                return "Tudo bem, poderia me informar uma nova data?"

        elif registro_status.status == 'CDA': #CDA: Confirmação de desejo de agendamento
            await deletar_status(db, telefone)

            if opcao == 'Sim':
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'IDT', hora_atual, None, None)
                return "Ok, poderia informar a data novamente?"

            return "Ok, em que mais posso ajudá-lo?"

        elif registro_status.status == 'CAG': #CAG: Cancelar agendamento

            if opcao == 'Desistir de cancelar agendamento.':
                await deletar_status(db, telefone)
                return "Ok, se precisar de algo, estou à disposição!"

            await deletar_status(db, telefone)

            data_cancelamento, hora_cancelamento = await transformar_data_e_hora(opcao)

            agendamentos = await buscar_agendamentos_por_contato_id(db, registro_contato.id)

            for agendamento in agendamentos:

                if agendamento.get('data') == str(data_cancelamento) and agendamento.get('hora') == str(hora_cancelamento):
                    id_agendamento = agendamento['id']
                    await deletar_agendamento(db, id_agendamento)
                    hora_atual = datetime.now().time().strftime("%H:%M:%S")
                    novo_status = await gravar_status(db, telefone, 'RA2', hora_atual, None, None)

                    if env == 'hareware':
                        numero_cliente = ['5519997581672', '5519995869852']
                    elif env == 'emyconsultorio':
                        numero_cliente = ['5513991701738']

                    data_cancelamento_normalizada = await normalizar_data(data_cancelamento)

                    notificacao_cliente = f'{registro_contato.nome} cancelou um horário para o dia {data_cancelamento_normalizada} às {hora_cancelamento}.'

                    for n_cliente in numero_cliente:

                        await send_message_zapi(
                            env=env,
                            number=n_cliente,
                            message=notificacao_cliente
                        )

                    return {'RA2': 'Agendamento cancelado com sucesso, Gostaria de remarcar?'}

        elif registro_status.status == 'RA2': # Remarcar agendamento 2
            await deletar_status(db, telefone)
            if opcao == 'Sim':
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, "IDT", hora_atual, None, None)
                return "Certo, escolha a melhor data para você!\n\n Escreva no formato Dia/Mês"
            else:
                return 'Tudo bem... precisando de mais alguma coisa é só chamar!'

        elif registro_status.status == 'CNM': #Confirmação de nome
            if opcao == 'Sim':
                nome = registro_status.observacao
                novo_contato = await criar_contato(db, nome=registro_status.observacao, numero_celular=telefone, email=None, pausa=False)
                registro_contato = await buscar_contato(db, telefone)
                await deletar_status(db, telefone)

                if env == 'hareware':
                    mensagem_retorno = (f'Prazer em conhecê-lo (a) {nome}, como posso te ajudar?\n\n'
                                        f'Aqui você pode:\n\n'
                                        f'- Sanar suas dúvidas sobre a HareWare\n\n'
                                        f'- Agendar um horário com a frase de ativação: "Quero agendar um horário"\n\n'
                                        f'- Solicitar o cancelamento de um agendamento com a frase de ativação: "Quero cancelar um agendamento"')
                elif env == "malaman":
                    mensagem_retorno = (f'Blz mano, como posso te ajudar?\n\n'
                                        f'Aqui você pode: \n\n'
                                        f'- Agendar um horário na barbearia com a frase de ativação: "Quero marcar um horário"\n\n'
                                        f'- Cancelar um horário marcado com a frase de ativação: "Quero cancelar um agendamento"\n\n'
                                        f'- Sanar suas dúvidas sobre a Barbearia Malaman.')
                elif env == "sjoicer":
                    mensagem_retorno = (f'Prazer em conhecê-la (o) {nome}, como posso te ajudar?\n\n'
                                        f'Aqui você pode:\n\n'
                                        f'- Sanar suas dúvidas sobre o meu Curso e sobre o meu salão.\n\n'
                                        f'- Agendar um horário no meu salão com a frase de ativação: "Quero agendar um horário"\n\n'
                                        f'- Solicitar o cancelamento de um agendamento com a frase de ativação: "Quero cancelar um agendamento"')
                return mensagem_retorno
        elif registro_status.status == 'CPA': # Confirmação de presença
            await deletar_status(db, telefone)
            if opcao == 'Sim':
                agendamento_confirmado = await alterar_confirmacao_agendamento(db, int(registro_status.observacao), True)
                return f'Obrigado pela confirmação!'
            else:
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'RAG', hora_atual, registro_status.observacao, None)
                return {"RAG": [{'name': 'Sim'}, {'name': 'Não'}]}

        elif registro_status.status == 'RAG':
            await deletar_status(db, telefone)
            if opcao == 'Sim':
                sucesso = await deletar_agendamento(db, int(registro_status.observacao))
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, "IDT", hora_atual, None, None)
                return "Certo, escolha a melhor data para você!\n\n Escreva no formato DD/MM/YYYY"
            else:
                sucesso = await deletar_agendamento(db, int(registro_status.observacao))
                return f'O seu agendamento foi cancelado, precisando de mais alguma coisa é só chamar!'
        else:
            await deletar_status(db, telefone)
            hora_atual = datetime.now().time().strftime("%H:%M:%S")
            novo_status = await gravar_status(db, telefone, 'CNC', hora_atual, None, None)
            return f'Você poderia me dizer o seu nome novamente?'


async def fluxo_conversa_foa(prompt, telefone):
    async with get_db('mmania') as db:
        registro_status = await buscar_status(db, telefone)

        registro_contato = await buscar_contato(db, telefone)

        if registro_contato is None:

            if registro_status is None:
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'CNC', hora_atual, None, None)

                return ("Olá, Seja bem-vindo! Eu sou a atendente virtual da Mmania de Bolo!\n\n"
                        "Percebi que você não está cadastrado na minha lista de contatos, poderia me dizer o seu nome?")

            if registro_status.status == 'CNC': #CNC = Cadastro de Nome de Contato
                if await caracteres_numericos(prompt) or await caracteres_invalidos(prompt):
                    return "Por favor, insira um nome válido."

                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'CNM', hora_atual, prompt, None)
                return {'CNM': f'Seu nome é {prompt}?'}

        else:
            if registro_status is None:
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'EAC', hora_atual, None, None)
                return {'EAC': ['Ver cardápio', 'Realizar pedido', 'Cancelar pedido'], 'mensagem': f'Olá {registro_contato.nome}!'}

            if registro_status.status == 'IPD': #IPD: Informar pedido
                if registro_status.observacao is None:
                    pedido = await criar_pedido(db=db, pedido=prompt, entrega=None, data_entrega=None, numero_cliente=telefone, nome_cliente=registro_contato.nome)
                else:
                    pedido = await buscar_pedido_id(db, int(registro_status.observacao))
                    pedido_alterado = await alterar_pedido(db, id=pedido.id, pedido=prompt)

                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'CPD', hora_atual, pedido.id, None)
                return {'CPD': ['Confirmo meu pedido', 'Quero alterar', 'Desistir do pedido'], 'mensagem': f'Você confirma o seu pedido? \n\n{prompt}'}

            if registro_status.status == 'IED': #IED: Informar endereço
                pedido = await buscar_pedido_id(db, int(registro_status.observacao))
                pedido_alterado = await alterar_pedido(db, id=pedido.id, entrega=prompt)
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'CED', hora_atual, pedido.id, None)
                return {'CED': ['Sim', 'Não'], 'mensagem': f'O seu endereço está correto?\n\n{prompt}'}

            if registro_status.status == 'IDT': #IDT: Informar data
                pedido = await buscar_pedido_id(db, int(registro_status.observacao))
                pedido_alterado = await alterar_pedido(db, id=pedido.id, data_entrega=prompt)
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'CDT', hora_atual, pedido.id, None)
                return {'CDT': ['Sim', 'Não'], 'mensagem': f'Confirma a data de entrega do pedido? \n\n {prompt}'}


async def fluxo_conversa_poll_foa(opcao, telefone):
    async with get_db('mmania') as db:
        registro_status = await buscar_status(db, telefone)

        registro_contato = await buscar_contato(db, telefone)

        if registro_status.status == 'CNM': #CNM: Confirmação de Nome
            if opcao == "Sim":
                nome = registro_status.observacao
                novo_contato = await criar_contato(db, nome=registro_status.observacao, numero_celular=telefone, email=None, pausa=False)
                registro_contato = await buscar_contato(db, telefone)
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'EAC', hora_atual, None, None)
                return {'EAC': ['Ver cardápio', 'Realizar pedido', 'Cancelar pedido'], 'mensagem': f'Prazer em conhecê-lo {nome}!'}
            else:
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'CNC', hora_atual, None, None)
                return {"texto": f'Você poderia me dizer o seu nome novamente?'}

        if registro_status.status == 'DRP': #DRP: Deseja realizar agendamento
            if opcao == "Sim":
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'IPD', hora_atual, None, None)
                return {"texto": 'Ok! Escreva em uma única mensagem todo o seu pedido'}
            else:
                await deletar_status(db, telefone)
                return {'texto': 'Tudo bem! Qualquer coisa é só mandar um oi...'}

        if registro_status.status == 'EAC': #EAC: Escolha de Ação
            if opcao == 'Ver cardápio':
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'DRP', hora_atual, None, None)
                return {'DRP': ['Sim', 'Não'], 'cardapio': 'https://drive.google.com/uc?export=download&id=172Xbx55g_pLczsZT0PCjyCfw1cH6rswQ'}
            elif opcao == 'Realizar pedido':
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'IPD', hora_atual, None, None)
                return {"opcao2": 'Ok! Escreva em uma única mensagem todo o seu pedido', 'cardapio': 'https://drive.google.com/uc?export=download&id=172Xbx55g_pLczsZT0PCjyCfw1cH6rswQ'}
            elif opcao == 'Cancelar pedido':
                await deletar_status(db, telefone)
                return {'texto': 'Para cancelar um pedido ligue para este número: (19) 99670-5890'}
            else:
                await deletar_status(db, telefone)
                return {'texto': 'Tudo bem! Qualquer coisa é só mandar um oi...'}

        if registro_status.status == 'CPD': #CPD: Confirmação de pedido
            if opcao == 'Confirmo meu pedido':
                id_pedido = registro_status.observacao
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'ERE', hora_atual, id_pedido, None)
                return {'ERE': ['Entrega', 'Retirada', 'Desistir do pedido'], 'mensagem': 'Você gostaria que seu pedido fosse entregue no endereço ou prefere retirar pessoalmente? Lembrando a entrega só é válida em Araras e está 08 reais.'}
            elif opcao == 'Quero alterar':
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'IPD', hora_atual, None, None)
                return {'texto': 'Ok, escreva novamente o seu pedido completo em uma única mensagem'}
            else:
                await deletar_status(db, telefone)
                return {'texto': 'Tudo bem! Qualquer coisa é só mandar um oi...'}

        if registro_status.status == 'ERE': #ERE: Escolha de entrega ou retirada
            if opcao == 'Entrega':
                id_pedido = registro_status.observacao
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'IED', hora_atual, id_pedido, None)
                return {'texto': 'Certo, me informe o seu endereço'}
            elif opcao == "Retirada":
                pedido = await buscar_pedido_id(db, int(registro_status.observacao))
                pedido_alterado = await alterar_pedido(db, id=pedido.id, entrega='Retirada')
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'IDT', hora_atual, pedido.id, None)
                return {'texto': 'Para quando é o pedido? \n(Caso tenha preferencia de horário pode escrever também)'}
            else:
                pedido = await buscar_pedido_id(db, int(registro_status.observacao))
                await excluir_pedido(db, pedido.id)
                await deletar_status(db, telefone)
                return {'texto': 'Que pena! Caso mude de ideia mande um oi! Até a próxima!!!'}

        if registro_status.status == 'CED': #CED: Confirmação de endereço
            if opcao == 'Sim':
                id_pedido = int(registro_status.observacao)
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'IDT', hora_atual, id_pedido, None)
                return {'texto': 'Para quando é o pedido? \n(Caso tenha preferencia de horário pode escrever também)'}
            else:
                id_pedido = int(registro_status.observacao)
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'IED', hora_atual, id_pedido, None)
                return {'texto': 'Me informe o seu endereço novamente.'}

        if registro_status.status == 'CDT':
            if opcao == "Sim":
                id_pedido = int(registro_status.observacao)
                await deletar_status(db, telefone)
                pedido = await buscar_pedido_id(db, id_pedido)
                return {'finalizado': pedido}
            else:
                id_pedido = int(registro_status.observacao)
                await deletar_status(db, telefone)
                hora_atual = datetime.now().time().strftime("%H:%M:%S")
                novo_status = await gravar_status(db, telefone, 'IDT', hora_atual, id_pedido, None)
                return {'texto': 'Poderia me informar a data de entrega do pedido novamente?'}
