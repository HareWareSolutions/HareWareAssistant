import logging
import os
import tiktoken
from datetime import datetime, date, timedelta, time
from app.db.db import get_db
from app.utils.relatorio_ag import gerar_relatorio_pdf
from app.models.contato import buscar_contato_id, criar_contato, listar_contatos, deletar_contato, editar_contato, buscar_contato
from app.models.agendamento import buscar_agendamentos_por_data, buscar_agendamentos_por_data_api, gravar_agendamento, deletar_agendamento
from app.models.clientes import buscar_cliente_cpfcnpj, criar_cliente, buscar_cliente_email, listar_clientes, editar_clientes, buscar_cliente
from app.models.contrato import criar_contrato, editar_contrato, deletar_contrato, listar_contratos, buscar_contrato_por_id
from app.flow import fluxo_conversa, fluxo_conversa_poll, fluxo_conversa_poll_foa, fluxo_conversa_foa
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from app.utils.zapi import send_message_zapi, send_poll_zapi, send_document_zapi
from app.utils.rotinasHoras import verificar_horarios
from app.utils.validador_documento import validar_documento
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from threading import Lock
from app.utils.rotinasDatas import normalizar_data

logging.basicConfig(level=logging.INFO)

encoding = tiktoken.get_encoding("cl100k_base")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://hareinteract.com.br",
        "https://hareinteract.com.br",
        "https://api.z-api.io",
        "https://hareware.com.br"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ids_mensagens_processados = {}
lock = Lock()
TTL = timedelta(minutes=1)


def limpar_ids():
    hora_atual = datetime.now()
    with lock:
        ids_para_deletar = [id_mensagem for id_mensagem, timestamp in ids_mensagens_processados.items() if hora_atual - timestamp > TTL]
        for id_mensagem in ids_para_deletar:
            del ids_mensagens_processados[id_mensagem]


@app.post("/webhook-zapi-foa")
async def receber_mensagem_foa(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        logging.info(f"Dados recebidos: {data}")

        id_mensagem = data.get("messageId")
        if not id_mensagem:
            logging.error("ID da mensagem não encontrado.")
            return {"error": "ID da mensagem não encontrado."}

        with lock:
            if id_mensagem in ids_mensagens_processados:
                logging.info(f"Mensagem duplicada ignorada")
                return {"status": "Mensagem duplicada ignorada."}
            ids_mensagens_processados[id_mensagem] = datetime.now()

        background_tasks.add_task(limpar_ids)

        numero_celular = data.get("phone")
        if not numero_celular:
            logging.info(f"Número de telefone não encontrado.")
            return {"status": "error", "message": "Número de telefone não encontrado"}

        if data.get("type") == "ReceivedCallback" and data.get("pollVote"):

            poll_data = data["pollVote"]
            poll_message_id = poll_data.get("pollMessageId")
            opcao_votada = poll_data.get("options", [])
            opcao_votada = opcao_votada[0].get("name", "")

            resposta = fluxo_conversa_poll_foa(opcao_votada, numero_celular)

            if 'EAC' in resposta:
                mensagem = resposta['mensagem']
                pergunta = 'Como posso te ajudar hoje?'
                opcoes = [{'name': opcao} for opcao in resposta['EAC']]
                opcoes.append({'name': 'Não quero realizar nenhuma ação.'})

                send_message_zapi(
                    env='mmania',
                    number=numero_celular,
                    message=mensagem,
                    delay_typing=1
                )

            if 'DRP' in resposta:
                mensagem = 'Aqui está o cardápio!'
                cardapio = resposta['cardapio']
                pergunta = 'Deseja realizar um pedido?'
                opcoes = [{'name': opcao} for opcao in resposta['DRP']]

                send_message_zapi(
                    env='mmania',
                    number=numero_celular,
                    message=mensagem,
                    delay_typing=1
                )

                send_document_zapi(
                    env='mmania',
                    number=numero_celular,
                    document_url=cardapio,
                    file_name='cardapio_mmania_de_bolo.pdf'
                )

            if 'ERE' in resposta:
                pergunta = resposta['mensagem']
                opcoes = [{'name': opcao} for opcao in resposta['ERE']]

            if 'texto' in resposta:
                mensagem = resposta['texto']

                send_message_zapi(
                    env='mmania',
                    number=numero_celular,
                    message=mensagem,
                    delay_typing=1
                )

                return {"status": "success"}

            if 'opcao2' in resposta:
                mensagem = resposta['opcao2']
                cardapio = resposta['cardapio']

                send_document_zapi(
                    env='mmania',
                    number=numero_celular,
                    document_url=cardapio,
                    file_name='cardapio_mmania_de_bolo.pdf'
                )

                send_message_zapi(
                    env='mmania',
                    number=numero_celular,
                    message=mensagem,
                    delay_typing=1
                )

                return {"status": "success"}

            if 'finalizado' in resposta:
                id_pedido = resposta['finalizado'].id
                pedido = resposta['finalizado'].pedido
                entrega = resposta['finalizado'].entrega
                data_entrega = resposta['finalizado'].data_entrega
                celular_cliente = resposta['finalizado'].numero_cliente
                nome_cliente = resposta['finalizado'].nome_cliente

                mensagem_cliente = (f'Código do pedido: {id_pedido}\n\n'
                                    f'Pedido: {pedido}\n\n'
                                    f'Entrega: {entrega}\n\n'
                                    f'Data do pedido: {data_entrega}\n\n'
                                    f'Pedido concluido, o pagamento será após a entrega do bolo.\n'
                                    f'Guarde o código do pedido.')

                send_message_zapi(
                    env='mmania',
                    number=numero_celular,
                    message=mensagem_cliente,
                    delay_typing=1
                )

                mensagem_restaurante = (f'Código do pedido: {id_pedido}\n\n'
                                        f'Pedido: {pedido}\n\n'
                                        f'Entrega: {entrega}\n\n'
                                        f'Data do pedido: {data_entrega}\n\n'
                                        f'Telefone do cliente: {celular_cliente}\n\n'
                                        f'Nome do cliente: {nome_cliente}')

                send_message_zapi(
                    env='mmania',
                    number=5519996705890,
                    message=mensagem_restaurante,
                    delay_typing=1
                )

                return {"status": "success"}

            send_poll_zapi(
                env='mmania',
                number=numero_celular,
                question=pergunta,
                options=opcoes
            )

            return {"status": "success"}

        imagem_url = data.get("image", {}).get("imageUrl")
        captions = data.get("image", {}).get("caption")

        if imagem_url:
            logging.info(f"Imagem recebida: {imagem_url}")
            if captions:
                logging.info(f"Captions da imagem: {captions}")
            resposta = "Infelizmente no momento ainda não consigo analisar imagens..."

            send_message_zapi(
                env='mmania',
                number=numero_celular,
                message=resposta,
                delay_typing=1
            )

        prompt = data.get("text", {}).get("message")
        if prompt:
            logging.info(f"Mensagem de texto recebida: {prompt}")

            resposta = fluxo_conversa_foa(prompt, numero_celular)

            if 'EAC' in resposta:
                mensagem = resposta['mensagem']
                pergunta = 'Como posso te ajudar hoje?'
                opcoes = [{'name': opcao} for opcao in resposta['EAC']]
                opcoes.append({'name': 'Não quero realizar nenhuma ação.'})

                send_message_zapi(
                    env='mmania',
                    number=numero_celular,
                    message=mensagem,
                    delay_typing=1
                )

                send_poll_zapi(
                    env='mmania',
                    number=numero_celular,
                    question=pergunta,
                    options=opcoes
                )

                return {"status": "success"}

            if 'CPD' in resposta:
                pergunta = resposta['mensagem']
                opcoes = [{'name': opcao} for opcao in resposta['CPD']]

                send_poll_zapi(
                    env='mmania',
                    number=numero_celular,
                    question=pergunta,
                    options=opcoes
                )

                return {"status": "success"}

            if 'CED' in resposta:
                pergunta = resposta['mensagem']
                opcoes = [{'name': opcao} for opcao in resposta['CED']]

                send_poll_zapi(
                    env='mmania',
                    number=numero_celular,
                    question=pergunta,
                    options=opcoes
                )

                return {"status": "success"}

            if 'CDT' in resposta:
                pergunta = resposta['mensagem']
                opcoes = [{'name': opcao} for opcao in resposta['CDT']]

                send_poll_zapi(
                    env='mmania',
                    number=numero_celular,
                    question=pergunta,
                    options=opcoes
                )

                return {"status": "success"}

            elif 'CNM' in resposta:
                pergunta = resposta['CNM']
                opcoes = [{'name': 'Sim'}, {'name': 'Não'}]

                send_poll_zapi(
                    env='mmania',
                    number=numero_celular,
                    question=pergunta,
                    options=opcoes
                )

                return {"status": "success"}

            send_message_zapi(
                env='mmania',
                number=numero_celular,
                message=resposta,
                delay_typing=1
            )

            return {"status": "success"}

    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/webhook-zapi-sa")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    db = next(get_db('hwadmin'))
    try:
        data = await request.json()
        logging.info(f"Dados recebidos: {data}")

        id_mensagem = data.get("messageId")
        if not id_mensagem:
            logging.error("ID da mensagem não encontrado.")
            return {"error": "ID da mensagem não encontrado."}

        with lock:
            if id_mensagem in ids_mensagens_processados:
                logging.info(f"Mensagem duplicada ignorada")
                return {"status": "Mensagem duplicada ignorada."}
            ids_mensagens_processados[id_mensagem] = datetime.now()

        background_tasks.add_task(limpar_ids)

        grupo = data.get("isGroup")
        if grupo:
            logging.info("Mensagem de grupo ignorada.")
            return {"status": "Mensagem de grupo ignorada"}

        numero_celular = data.get("phone")
        if not numero_celular:
            logging.error("Número de telefone não encontrado.")
            return {"status": "error", "message": "Número de telefone não encontrado."}

        destino = data.get("connectedPhone")
        if not destino:
            logging.error("Número de destino não encontrado.")
            return {"status": "error", "message": "Número de destino não encontrato."}

        match destino:
            case "5519999344528":
                env = 'hareware'
                id_contrato = 1
            case "5519971501387":
                env = 'malaman'
                id_contrato = 5
            case "5519984574859":
                env = 'joice'
                id_contrato = 2
            case other:
                return {"status": "error", "message": "Número de destino inválido."}

        if data.get("type") == "ReceivedCallback" and data.get("pollVote"):

            poll_data = data["pollVote"]
            poll_message_id = poll_data.get("pollMessageId")
            opcao_votada = poll_data.get("options", [])
            opcao_votada = opcao_votada[0].get("name", "")

            resposta = fluxo_conversa_poll(env, opcao_votada, numero_celular)

            if 'IHR' in resposta and isinstance(resposta['IHR'], list):
                pergunta = 'Escolha um dos horários disponíveis:'
                opcoes = [{'name': opcao} for opcao in resposta['IHR']]
                opcoes.append({'name': 'Nenhum desses horários é compatível comigo.'})

            elif 'PAUSA' in resposta:
                logging.info(f"Mensagem de contato em pausa.")
                return {"status": "Mensagem de contato em pausa."}

            elif 'IHR2' in resposta and isinstance(resposta['IHR2'], list):
                desculpa = 'Desculpe, acabamos de registrar um agendamento para esse horário. Poderia, por gentileza, escolher outro horário disponível?'

                send_message_zapi(
                    env=env,
                    number=numero_celular,
                    message=desculpa,
                    delay_typing=1
                )

                pergunta = 'Escolha um dos horários disponíveis:'
                opcoes = [{'name': opcao} for opcao in resposta['IHR2']]
                opcoes.append({'name': 'Nenhum desses horários é compatível comigo.'})
            elif 'CDA' in resposta:
                pergunta = resposta['CDA']
                opcoes = [{'name': 'Sim'}, {'name': 'Não'}]

            else:
                send_message_zapi(
                    env=env,
                    number=numero_celular,
                    message=resposta,
                    delay_typing=1
                )

                return {"status": "success"}

            send_poll_zapi(
                env=env,
                number=numero_celular,
                question=pergunta,
                options=opcoes
            )

            return {"status": "success"}

        imagem_url = data.get("image", {}).get("imageUrl")
        captions = data.get("image", {}).get("caption")

        if imagem_url:
            logging.info(f"Imagem recebida: {imagem_url}")
            if captions:
                logging.info(f"Captions da imagem: {captions}")
            resposta = "Infelizmente no momento ainda não consigo analisar imagens..."
            logging.info("Mensagens de imagem.")
            return {"Retorno": "Ignorado, mensagem de imagem."}

            send_message_zapi(
                env=env,
                number=numero_celular,
                message=resposta,
                delay_typing=1
            )

        prompt = data.get("text", {}).get("message")
        if prompt:
            logging.info(f"Mensagem de texto recebida: {prompt}")

            tokens_entrada = encoding.encode(prompt)
            num_tokens = len(tokens_entrada)

            resposta = fluxo_conversa(env, prompt, numero_celular)

            if 'CDT' in resposta:
                pergunta = f'Você deseja realizar um agendamento na data de {resposta["CDT"]}?'
                opcoes = [{'name': 'Sim'}, {'name': 'Não'}]

                send_poll_zapi(
                    env=env,
                    number=numero_celular,
                    question=pergunta,
                    options=opcoes
                )

                return {"status": "success"}

            elif 'PAUSA' in resposta:
                logging.info(f"Mensagem de contato em pausa.")
                return {"status": "Mensagem de contato em pausa."}

            elif 'CAG' in resposta and isinstance(resposta['CAG'], list):
                pergunta = 'Escolha um dos agendamentos para cancelar:'
                opcoes = [{'name': opcao} for opcao in resposta['CAG']]

                send_poll_zapi(
                    env=env,
                    number=numero_celular,
                    question=pergunta,
                    options=opcoes
                )

                return {"status": "success"}

            elif 'CNM' in resposta:
                pergunta = resposta['CNM']
                opcoes = [{'name': 'Sim'}, {'name': 'Não'}]

                send_poll_zapi(
                    env=env,
                    number=numero_celular,
                    question=pergunta,
                    options=opcoes
                )

                return {"status": "success"}

            resposta_token = resposta
            if isinstance(resposta_token, list):
                resposta_token = resposta_token[0].text.value

            tokens_saida = encoding.encode(resposta_token)

            num_tokens_saida = len(tokens_saida)
            total_tokens_acao = num_tokens + num_tokens_saida

            contrato = buscar_contrato_por_id(db, id_contrato)

            total_tokens_contrato = contrato.tokens_utilizados

            atualizacao_tokens = total_tokens_contrato + total_tokens_acao

            atualizacao_contrato = editar_contrato(
                db,
                id_contrato,
                None,
                None,
                None,
                atualizacao_tokens,
                None
            )

            send_message_zapi(
                env=env,
                number=numero_celular,
                message=resposta,
                delay_typing=1
            )

        return {"status": "success"}

    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@app.post("/incluir-agendamento")
async def incluir_agendamento(empresa: str, data: str, hora: str, contato: int):
    try:
        data_convertida = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de 'data' inválido. Use 'DD/MM/YYYY'.")

    try:
        datetime.strptime(hora, "%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de 'hora' inválido. Use 'HH:MM'.")

    db = next(get_db(empresa))
    try:
        data_agendamento = datetime.strptime(data, "%d/%m/%Y").date()
        agendamentos = buscar_agendamentos_por_data(db, data_agendamento)
        horarios_disponiveis = verificar_horarios(empresa, agendamentos, data)

        hora_agendamento = datetime.strptime(hora, "%H:%M").time()
        hora_formatada = hora_agendamento.strftime("%H:%M")

        if hora_formatada in horarios_disponiveis:
            sucesso = gravar_agendamento(db, data_convertida, hora, contato)
            if sucesso:
                return {"status": "success", "message": "Agendamento incluído com sucesso."}
            else:
                raise HTTPException(status_code=500, detail="Erro ao gravar o agendamento.")
        else:
            raise HTTPException(status_code=500, detail="Já há um agendamento para esse horário nesta data.")
    finally:
        db.close()


@app.post("/cancelar-agendamento")
async def cancelarAgendamento(empresa: str, id_agendamento: int):
    db = next(get_db(empresa))
    try:
        sucesso = deletar_agendamento(db, id_agendamento)
        if sucesso:
            return {"status": "success", "message": "Agendamento cancelado com sucesso."}
        else:
            raise HTTPException(status_code=500, detail="Erro ao deletar o agendamento.")
    finally:
        db.close()


@app.post("/pesquisar-agenda-dia")
async def pesquisarAgendaDia(empresa: str, data: str):
    db = next(get_db(empresa))
    try:
        agendamentos = buscar_agendamentos_por_data_api(db, data)

        if agendamentos is not None:
            agendamentos_dia = []
            for agendamento in agendamentos:
                id_agendamento = agendamento.get("id_agendamento")
                data_obj = agendamento.get("data")
                hora_obj = agendamento.get("hora")
                id_contato = agendamento.get("id_contato")

                if isinstance(data_obj, datetime):
                    data_formatada = data_obj.strftime("%d/%m/%Y")
                elif isinstance(data_obj, date):
                    data_formatada = data_obj.strftime("%d/%m/%Y")
                else:
                    data_formatada = data_obj

                if isinstance(hora_obj, time):
                    hora_formatada = hora_obj.strftime("%H:%M")
                else:
                    try:
                        hora_formatada = datetime.strptime(hora_obj, "%H:%M:%S").strftime("%H:%M")
                    except ValueError:
                        hora_formatada = hora_obj

                contato = buscar_contato_id(db, id_contato)

                reserva = {
                    "id_agendamento": id_agendamento,
                    "data": data_formatada,
                    "hora": hora_formatada,
                    "id_contato": id_contato,
                    "telefone": contato.numero_celular,
                    "nome": contato.nome
                }

                agendamentos_dia.append(reserva)

            agendamentos_dia.sort(key=lambda x: x["hora"])

            return {"retorno": agendamentos_dia}
        else:
            return {"retorno": "Não há agendamentos para esta data."}
    finally:
        db.close()


@app.post("/horarios-disponiveis")
async def horarios_disponiveis(empresa: str, data: str):
    db = next(get_db(empresa))
    try:
        if "/" in data:
            data_agendamento = datetime.strptime(data, "%d/%m/%Y").date()
        else:
            return {"erro": "Formato de data inválido. Use 'DD/MM/YYYY'."}

        agendamentos = buscar_agendamentos_por_data(db, data_agendamento)
        data_formatada = data_agendamento.strftime("%d/%m/%Y")
        horarios_disponiveis = verificar_horarios(empresa, agendamentos, data_formatada)

        if horarios_disponiveis:
            return {"retorno": horarios_disponiveis}
        else:
            return {"retorno": None}
    finally:
        db.close()


@app.post("/contato-pesquisa")
async def pesquisa_contato(empresa: str, id_contato: int):
    db = next(get_db(empresa))
    try:
        contato = buscar_contato_id(db, id_contato)
        if contato:
            dados_contato = {"id": contato.id, "nome": contato.nome}
            return {"retorno": dados_contato}
        else:
            return {"retorno": "Nenhum Contato foi encontrado."}
    finally:
        db.close()


@app.post("/dados-contato")
async def procurar_dados_contato(empresa: str, id_contato: int):
    db = next(get_db(empresa))
    try:
        contato = buscar_contato_id(db, id_contato)
        if contato:
            dados_contato = {
                "id": contato.id,
                "nome": contato.nome,
                "telefone": contato.numero_celular,
                "email": contato.email,
                "pausa": contato.pausa
                }

            return {"retorno": dados_contato}
        else:
            return {"retorno": "Nenhum Contato foi encontrado."}
    finally:
        db.close()


@app.post("/logar")
async def logar(usuario: str, senha: str):
    db = next(get_db('hwadmin'))
    try:
        usuario_dados = buscar_cliente_email(db, usuario)

        if usuario_dados is not None:
            senha_usuario = usuario_dados.senha
            if senha_usuario == senha:
                return {
                    "id": usuario_dados.id,
                    "nome": usuario_dados.nome,
                    "empresa": usuario_dados.empresa
                }
            else:
                return {"status": "Usuário ou senha incorretos"}
        else:
            return {"status": "Usuário ou senha incorretos"}
    finally:
        db.close()


@app.post("/gerar-relatorio-agendamento")
async def relatorio_agendamento(empresa: str, nome_empresa: str, data: str, background_tasks: BackgroundTasks):

    db = next(get_db(empresa))
    try:
        agendamentos = buscar_agendamentos_por_data_api(db, data)

        if agendamentos is not None:
            agendamentos_dia = []
            for agendamento in agendamentos:
                id_agendamento = agendamento.get("id_agendamento")
                data_obj = agendamento.get("data")
                hora_obj = agendamento.get("hora")
                id_contato = agendamento.get("id_contato")

                if isinstance(data_obj, datetime):
                    data_formatada = data_obj.strftime("%d/%m/%Y")
                elif isinstance(data_obj, date):
                    data_formatada = data_obj.strftime("%d/%m/%Y")
                else:
                    data_formatada = data_obj

                if isinstance(hora_obj, time):
                    hora_formatada = hora_obj.strftime("%H:%M")
                else:
                    try:
                        hora_formatada = datetime.strptime(hora_obj, "%H:%M:%S").strftime("%H:%M")
                    except ValueError:
                        hora_formatada = hora_obj

                contato = buscar_contato_id(db, id_contato)

                reserva = {
                    "id_agendamento": id_agendamento,
                    "data": data_formatada,
                    "hora": hora_formatada,
                    "id_contato": id_contato,
                    "telefone": contato.numero_celular,
                    "nome": contato.nome
                }

                agendamentos_dia.append(reserva)

            agendamentos_dia.sort(key=lambda x: x["hora"])

            nome_arquivo = f"relatorio_agendamentos_{nome_empresa}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            caminho_pdf = f"C:/APIs/HareWareAssistant/app/relatorios/{nome_arquivo}"
            relatorio = gerar_relatorio_pdf(nome_empresa, agendamentos_dia, data)

            with open(caminho_pdf, "wb") as f:
                f.write(relatorio.getvalue())

            response = FileResponse(caminho_pdf, media_type='application/pdf', headers={
                "Content-Disposition": f"attachment; filename={nome_arquivo}"
            })

            background_tasks.add_task(remover_arquivo, caminho_pdf)

            return response
        else:
            return {"retorno": "Não há agendamentos para esta data."}
    finally:
        db.close()


@app.post("/visualizar-contatos")
async def visualizar_contatos(empresa: str):
    db = next(get_db(empresa))
    try:
        contatos = listar_contatos(db)

        lista_contatos = []
        for contato in contatos:
            dados_contato = {
                "id": contato.id,
                "nome": contato.nome,
                "numero_celular": contato.numero_celular,
                "email": contato.email
            }

            lista_contatos.append(dados_contato)

        return {"retorno": lista_contatos}

    finally:
        db.close()


@app.post("/cadastrar-contato")
async def cadastrar_contato(empresa: str, nome: str, numero_celular: str, email: str = None):
    db = next(get_db(empresa))
    try:
        sucesso = criar_contato(db, nome, numero_celular, email, False)
        if sucesso:
            return {"status": "sucess", "message": "Contato cadastrado com sucesso."}
        else:
            raise HTTPException(status_code=500, detail="Erro ao cadastrar o contato.")
    finally:
        db.close()


@app.post("/excluir-contato")
async def excluir_contato(empresa: str, id: int):
    db = next(get_db(empresa))
    try:
        sucesso = deletar_contato(db, id)
        if sucesso:
            return {"status": "sucess", "message": "Contato excluido com sucesso."}
        else:
            raise HTTPException(status_code=500, detail="Erro ao excluir contato.")
    finally:
        db.close()


@app.post("/editar-contato")
async def editar_contato_endpoint(empresa: str, id: int, nome: str = None, numero_celular: str = None, email: str = None, pausa: bool = None):
    db = next(get_db(empresa))
    try:
        contato_atualizado = editar_contato(db, id, nome, numero_celular, email, pausa)
        if contato_atualizado:
            return {"message": "Contato atualizado com sucesso", "contato": contato_atualizado}
        else:
            raise HTTPException(status_code=404, detail="Contato não encontrado")
    finally:
        db.close()


def remover_arquivo(caminho_pdf: str):
    try:
        os.remove(caminho_pdf)
        print(f"Arquivo {caminho_pdf} removido com sucesso.")
    except Exception as e:
        print(f"Erro ao excluir o arquivo {caminho_pdf}: {e}")


# PAINEL ADMINISTRATIVO HAREWARE

@app.post("/cadastrar-cliente")
async def cadastrar_cliente(cod_hw: str, nome: str, empresa: str, email: str, telefone: str, cpfcnpj: str, senha: str, ativo: bool):
    db = next(get_db(cod_hw))
    try:
        documento_valido = validar_documento(cpfcnpj)
        if documento_valido:
            documento_existente = buscar_cliente_cpfcnpj(db, cpfcnpj)
            if documento_existente is None:
                sucesso = criar_cliente(db, nome, empresa, email, telefone, cpfcnpj, senha, ativo)
                if sucesso:
                    return {"status": "success", "message": "Cliente cadastrado com sucesso."}
                else:
                    raise HTTPException(status_code=500, detail="Erro ao cadastrar o cliente.")
            else:
                return {"retorno": "Esse CPF ou CNPJ já está cadastrado."}
        else:
            return {"retorno": "Por favor informe um documento válido."}
    finally:
        db.close()


@app.post("/visualizar-clientes")
async def visualizar_clientes(cod_hw: str):
    db = next(get_db(cod_hw))
    try:
        clientes = listar_clientes(db)

        lista_clientes = []
        for cliente in clientes:
            if cliente.ativo == 0:
                ativo = "Inativo"
            else:
                ativo = "Ativo"

            dados_formatados = {
                "id": cliente.id,
                "nome": cliente.nome,
                "email": cliente.email,
                "telefone": cliente.telefone,
                "cpfcnpj": cliente.cpfcnpj,
                "ativo": ativo
            }

            lista_clientes.append(dados_formatados)

        return {"retorno": lista_clientes}
    finally:
        db.close()


@app.post("/alterar-cliente")
async def alterar_cliente(cod_hw: str, cliente_id: int, nome: str = None, empresa: str = None, email: str = None,
                          telefone: str = None, cpfcnpj: str = None, senha: str = None, ativo: bool = None):
    db = next(get_db(cod_hw))
    try:

        cliente_existente = buscar_cliente(db, cliente_id)
        if cliente_existente is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")

        if cpfcnpj:
            documento_valido = validar_documento(cpfcnpj)
            if not documento_valido:
                return {"retorno": "Por favor informe um documento válido."}

            outro_cliente = buscar_cliente_cpfcnpj(db, cpfcnpj)
            if outro_cliente and outro_cliente.id != cliente_id:
                return {"retorno": "Esse CPF ou CNPJ já está cadastrado por outro cliente."}

        campos_para_atualizar = {
            "nome": nome,
            "empresa": empresa,
            "email": email,
            "telefone": telefone,
            "cpfcnpj": cpfcnpj,
            "senha": senha,
            "ativo": ativo,
        }

        campos_para_atualizar = {k: v for k, v in campos_para_atualizar.items() if v is not None}

        cliente_atualizado = editar_clientes(db, cliente_id, **campos_para_atualizar)
        if cliente_atualizado:
            return {"status": "success", "message": "Cliente alterado com sucesso."}
        else:
            raise HTTPException(status_code=500, detail="Erro ao alterar o cliente.")
    finally:
        db.close()


@app.post("/buscar-cliente-cpfcnpj")
async def buscar_cliente_por_cpfcnpj(cod_hw: str, cpfcnpj: str):
    db = next(get_db(cod_hw))
    try:
        documento_valido = validar_documento(cpfcnpj)
        if not documento_valido:
            return {"retorno": "Por favor informe um documento válido."}

        cliente = buscar_cliente_cpfcnpj(db, cpfcnpj)
        if cliente:
            return {"status": "success", "cliente": cliente}
        else:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    finally:
        db.close()


@app.post("/incluir-contrato")
async def incluir_contrato(cod_hw: str, tipo: str, pagamento: bool, pacote: str, id_cliente: int):
    db = next(get_db(cod_hw))
    try:
        cliente = buscar_cliente(db, id_cliente)
        if cliente is not None:
            sucesso = criar_contrato(db, tipo, pagamento, pacote, 0, None, id_cliente)
            if sucesso:
                cliente = alterar_cliente(db, id_cliente, ativo=True)
                return {"status": "success", "message": "Contrato incluído com sucesso."}
            else:
                raise HTTPException(status_code=500, detail="Erro ao incluir contrato.")
        else:
            return {"retorno": "Por favor informe um cliente válido."}
    finally:
        db.close()


@app.post("/alterar-contrato")
async def alterar_contrato(cod_hw: str, id_contrato: int, tipo: str = None, pagamento: bool = None, pacote: str = None):
    db = next(get_db(cod_hw))
    try:
        if pagamento:
            data_pagamento = datetime.now().date()
        else:
            data_pagamento = None

        contrato = editar_contrato(
            db,
            id_contrato,
            tipo,
            pagamento,
            pacote,
            None,
            data_pagamento
        )
        if contrato:
            return {"status": "success", "message": "Contrato alterado com sucesso."}
        else:
            raise HTTPException(status_code=404, detail="Contrato não encontrado.")
    finally:
        db.close()


@app.post("/excluir-contrato")
async def excluir_contrato(cod_hw: str, id_contrato: int):
    db = next(get_db(cod_hw))
    try:
        sucesso = deletar_contrato(db, id_contrato)
        if sucesso:
            return {"status": "success", "message": "Contrato excluído com sucesso."}
        else:
            raise HTTPException(status_code=404, detail="Erro ao excluir contrato.")
    finally:
        db.close()


@app.post("/visualizar-contratos")
async def visualizar_contratos(cod_hw: str):
    db = next(get_db(cod_hw))
    try:
        contratos = listar_contratos(db)
        lista_contratos = []

        for contrato in contratos:
            if contrato.pagamento:
                status_pagamento = "Pago"
            else:
                status_pagamento = "Não Pago"

            cliente = buscar_cliente(db, contrato.id_cliente)

            dados_formatados = {
                "id": contrato.id,
                "tipo": contrato.tipo,
                "pacote": contrato.pacote,
                "tokens_utilizados": contrato.tokens_utilizados,
                "status_pagamento": status_pagamento,
                "data_ultimo_pagamento": contrato.data_ultimo_pagamento,
                "id_cliente": cliente.id,
                "nome_cliente": cliente.nome
            }

            lista_contratos.append(dados_formatados)

        return {"retorno": lista_contratos}
    finally:
        db.close()


@app.post("/buscar-contrato")
async def buscar_contrato(cod_hw: str, id_contrato: int):
    db = next(get_db(cod_hw))
    try:
        contrato = buscar_contrato_por_id(db, id_contrato)
        if contrato is not None:
            return {"status": "success", "contrato": contrato}
        else:
            raise HTTPException(status_code=404, detail="Contrato não encontrado.")
    finally:
        db.close()


@app.post("/logar-adm")
async def logar(usuario: str, senha: str):
    db = next(get_db('hwadmin'))
    try:
        usuario_dados = buscar_cliente_email(db, usuario)

        if usuario_dados is not None:
            senha_usuario = usuario_dados.senha
            if senha_usuario == senha and (usuario_dados.empresa == 'hareware' or usuario_dados.empresa == 'hwadmin'):
                return {
                    "id": usuario_dados.id,
                    "nome": usuario_dados.nome,
                    "empresa": usuario_dados.empresa
                }
            else:
                return {"status": "Usuário ou senha incorretos"}
        else:
            return {"status": "Usuário ou senha incorretos"}
    finally:
        db.close()