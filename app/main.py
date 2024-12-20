import logging
from datetime import datetime
from app.db.db import get_db
from app.models.contato import buscar_contato_id, criar_contato
from app.models.agendamento import buscar_agendamentos_por_data, buscar_agendamentos_por_data_api, gravar_agendamento, buscar_agendamentos_por_contato_id_formatado, buscar_agendamentos_por_contato_id, deletar_agendamento
from app.flow import fluxo_conversa, fluxo_conversa_poll, fluxo_conversa_poll_foa, fluxo_conversa_foa
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException
from app.utils.zapi import send_message_zapi, send_poll_zapi, send_document_zapi
from app.utils.rotinasHoras import verificar_horarios
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


class WebhookData(BaseModel):
    message: str


@app.post("/webhook-zapi-foa")
async def receber_mensagem_foa(request: Request):
    try:
        data = await request.json()
        logging.info(f"Dados recebidos: {data}")

        numero_celular = data.get("phone")
        if not numero_celular:
            logging.info(f"Número de telefone não encontrado.")
            return {"status": "error", "message": "Número de telefone não encontrado"}

        if numero_celular != 5519997581672:
            return {"status": "error", "message": "Telefone não autorizado"}

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
                opcoes = [{'name': opcao} for opcao in resposta['CED']]

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
async def receive_message(request: Request):
    try:
        data = await request.json()
        logging.info(f"Dados recebidos: {data}")

        numero_celular = data.get("phone")
        if not numero_celular:
            logging.error("Número de telefone não encontrado.")
            return {"status": "error", "message": "Número de telefone não encontrado."}

        if data.get("type") == "ReceivedCallback" and data.get("pollVote"):

            poll_data = data["pollVote"]
            poll_message_id = poll_data.get("pollMessageId")
            opcao_votada = poll_data.get("options", [])
            opcao_votada = opcao_votada[0].get("name", "")

            resposta = fluxo_conversa_poll(opcao_votada, numero_celular)

            if 'IHR' in resposta and isinstance(resposta['IHR'], list):
                pergunta = 'Escolha um dos horários disponíveis:'
                opcoes = [{'name': opcao} for opcao in resposta['IHR']]
                opcoes.append({'name': 'Nenhum desses horários é compatível comigo.'})
            elif 'IHR2' in resposta and isinstance(resposta['IHR2'], list):
                desculpa = 'Desculpe, acabamos de registrar um agendamento para esse horário. Poderia, por gentileza, escolher outro horário disponível?'

                send_message_zapi(
                    env='hareware',
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
                    env='hareware',
                    number=numero_celular,
                    message=resposta,
                    delay_typing=1
                )

                return {"status": "success"}

            send_poll_zapi(
                env='hareware',
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
                env='hareware',
                number=numero_celular,
                message=resposta,
                delay_typing=1
            )

        prompt = data.get("text", {}).get("message")
        if prompt:
            logging.info(f"Mensagem de texto recebida: {prompt}")

            resposta = fluxo_conversa(prompt, numero_celular)

            if 'CDT' in resposta:
                pergunta = f'Você deseja realizar um agendamento na data de {resposta["CDT"]}?'
                opcoes = [{'name': 'Sim'}, {'name': 'Não'}]

                send_poll_zapi(
                    env='hareware',
                    number=numero_celular,
                    question=pergunta,
                    options=opcoes
                )

                return {"status": "success"}

            elif 'CAG' in resposta and isinstance(resposta['CAG'], list):
                pergunta = 'Escolha um dos agendamentos para cancelar:'
                opcoes = [{'name': opcao} for opcao in resposta['CAG']]

                send_poll_zapi(
                    env='hareware',
                    number=numero_celular,
                    question=pergunta,
                    options=opcoes
                )

                return {"status": "success"}

            elif 'CNM' in resposta:
                pergunta = resposta['CNM']
                opcoes = [{'name': 'Sim'}, {'name': 'Não'}]

                send_poll_zapi(
                    env='hareware',
                    number=numero_celular,
                    question=pergunta,
                    options=opcoes
                )

                return {"status": "success"}

            send_message_zapi(
                env='hareware',
                number=numero_celular,
                message=resposta,
                delay_typing=1
            )

        return {"status": "success"}

    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/incluir-agendamento")
async def incluir_agendamento(data: str, hora: str, contato: int):
    try:
        data_convertida = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de 'data' inválido. Use 'DD/MM/YYYY'.")

    try:
        datetime.strptime(hora, "%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de 'hora' inválido. Use 'HH:MM'.")

    db = next(get_db('hareware'))
    try:
        data_agendamento = datetime.strptime(data, "%y-%m-%d").date()
        agendamentos = buscar_agendamentos_por_data(db, data_agendamento)
        horarios_disponiveis = verificar_horarios(agendamentos)

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
async def cancelarAgendamento(id_agendamento: int):
    db = next(get_db('hareware'))
    try:
        sucesso = deletar_agendamento(db, id_agendamento)
        if sucesso:
            return {"status": "success", "message": "Agendamento cancelado com sucesso."}
        else:
            raise HTTPException(status_code=500, detail="Erro ao deletar o agendamento.")
    finally:
        db.close()


@app.post("/pesquisar-agenda-dia")
async def pesquisarAgendaDia(data: str):
    db = next(get_db('hareware'))
    try:
        agendamentos = buscar_agendamentos_por_data_api(db, data)

        if agendamentos is not None:
            agendamentos_dia = []
            for agendamento in agendamentos:
                id_agendamento = agendamento.get("id_agendamento")
                data = agendamento.get("data")
                hora = agendamento.get("hora")
                id_contato = agendamento.get("id_contato")

                contato = buscar_contato_id(db, id_contato)

                reserva = {
                    "id_agendamento": id_agendamento,
                    "data": data,
                    "hora": hora,
                    "id_contato": id_contato,
                    "telefone": contato.numero_celular,
                    "nome": contato.nome
                }

                agendamentos_dia.append(reserva)

            return {"retorno": agendamentos_dia}
        else:
            return {"retorno": "Não há agendamentos para esta data."}
    finally:
        db.close()


@app.post("/logar")
async def logar(usuario: str, senha: str):

    if usuario == "HareWareAdmin" and senha == "123456":
        return {"id": 1, "nome": "HareWare", "webhook": "https://fe5f-177-128-10-78.ngrok-free.app/"}
    else:
        return {"status": "Usuário ou senha incorretos"}
