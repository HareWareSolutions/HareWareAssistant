import logging
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import hashlib

# Configuração de log
logging.basicConfig(level=logging.INFO)

# Inicialização da aplicação FastAPI
app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Dicionário para armazenar IDs das mensagens enviadas (em memória, idealmente deve ser um banco de dados ou cache)
sent_messages = {}


# Função para gerar um identificador único para cada mensagem
def generate_message_id(phone_number: str, message: str) -> str:
    # Gerar um hash SHA-256 com base no número de telefone e na mensagem
    return hashlib.sha256(f"{phone_number}{message}".encode('utf-8')).hexdigest()


# Função para enviar a mensagem via API
async def enviar_mensagem(api_url, connection_key, phone_number, message, delay_message, auth_token):
    """
    Função para enviar uma mensagem via API e receber uma resposta com uma mensagem de teste.

    Parâmetros:
    - api_url: URL base da API
    - connection_key: Chave de conexão para autenticação
    - phone_number: Número de telefone (formato internacional, ex: +55...)
    - message: Mensagem a ser enviada
    - delay_message: Atraso em milissegundos antes de enviar a mensagem
    - auth_token: Token de autenticação (se necessário)

    Retorno:
    - Resposta da API (em formato JSON ou mensagem de erro)
    """
    # Gerar um identificador único para a mensagem
    message_id = generate_message_id(phone_number, message)

    # Verificar se a mensagem já foi enviada
    if message_id in sent_messages:
        logging.info(f"Mensagem duplicada detectada: {message_id}")
        return {"status": "error", "message": "Mensagem já enviada anteriormente."}

    url = f"{api_url}/message/sendText?connectionKey={connection_key}"

    # Dados da mensagem
    data = {
        "phoneNumber": phone_number,
        "message": message,
        "delayMessage": str(delay_message)  # Atraso deve ser convertido para string
    }

    # Cabeçalhos para a requisição (com autenticação e tipo de conteúdo)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"  # Usando o token de autenticação
    }

    try:
        # Usando httpx para fazer a requisição de forma assíncrona
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)

        # Verificar a resposta da API
        if response.status_code == 200:
            api_response = response.json()

            # Armazenar o ID da mensagem para evitar duplicação
            sent_messages[message_id] = api_response.get("message", "Sem mensagem de teste")

            return {"status": "success", "message": api_response.get("message", "Sem mensagem de teste")}
        else:
            return {"status": "error", "status_code": response.status_code, "response": response.text}

    except httpx.RequestError as e:
        logging.error(f"Ocorreu um erro durante a requisição: {e}")
        return {"status": "error", "message": str(e)}


# Endpoint que recebe a mensagem e sempre retorna uma resposta com uma mensagem de teste
@app.post("/webhook-zapi")
async def receive_message(request: Request):
    # Receber os dados da requisição
    data = await request.json()

    # Extraindo o número do telefone
    remote_jid = data['body']['key']['remoteJid']
    numero = remote_jid[0:13]  # Ajuste para obter o número corretamente

    # Definindo os parâmetros para o envio
    api_url = "https://host13.serverapi.dev"  # Substitua com o seu host real
    connection_key = "w-api_N3IE7GZOFN"  # Substitua com a chave de conexão real
    phone_number = numero  # Número extraído da requisição
    message = "Bolinã de gorfe"  # Mensagem que você deseja enviar
    delay_message = 1000  # Atraso de 1000 milissegundos
    auth_token = "xT3AcKpnGLC5VPk49fhTlCLwk1VkuU9Up"  # Substitua com seu token de autenticação

    # Chamando a função para enviar a mensagem
    resultado = await enviar_mensagem(api_url, connection_key, phone_number, message, delay_message, auth_token)

    # Retornando a resposta
    return {"status": "success", "message": "Mensagem recebida com sucesso! Este é um teste."}
