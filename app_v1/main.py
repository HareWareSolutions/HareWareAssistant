import logging
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
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

# Conjunto para armazenar os hashes das mensagens processadas (chave: hash da mensagem)
processed_hashes = {}

# Função para enviar a mensagem via API
async def enviar_mensagem(api_url, connection_key, phone_number, message, delay_message, auth_token):
    """
    Função para enviar uma mensagem via API e receber uma resposta com uma mensagem de teste.
    """
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
            return {"status": "success", "message": api_response.get("message", "Sem mensagem de teste")}
        else:
            return {"status": "error", "status_code": response.status_code, "response": response.text}

    except httpx.RequestError as e:
        logging.error(f"Ocorreu um erro durante a requisição: {e}")
        return {"status": "error", "message": str(e)}


# Endpoint que recebe a mensagem e sempre retorna uma resposta com uma mensagem de teste
@app.post("/webhook-zapi")
async def receive_message(request: Request):
    data = await request.json()

    # Extraindo o ID da mensagem e o conteúdo
    message_id = data['body']['key']['id']
    remote_jid = data['body']['key']['remoteJid']
    message_text = data['body']['message']['extendedTextMessage']['text']

    # Gerando um hash único para a mensagem (com ID e conteúdo)
    message_hash = hashlib.sha256(f"{message_id}-{remote_jid}-{message_text}".encode('utf-8')).hexdigest()

    # Verificando duplicidade usando o hash
    current_time = time.time()  # Timestamp atual
    if message_hash in processed_hashes:
        last_processed_time = processed_hashes[message_hash]
        if current_time - last_processed_time < 5:  # Exemplo de janela de 5 segundos (ajustar conforme necessário)
            logging.info(f"Mensagem duplicada detectada (ID: {message_id}). Ignorando envio.")
            return {"status": "ignored", "message": "Mensagem duplicada detectada, não processada."}

    # Armazenando o hash da mensagem com o timestamp atual
    processed_hashes[message_hash] = current_time

    # Printando os dados recebidos na requisição
    numero = remote_jid[0:13]  # Pegando o número

    api_url = "https://host13.serverapi.dev"  # Substitua com o seu host real
    connection_key = "w-api_N3IE7GZOFN"  # Substitua com a chave de conexão real
    phone_number = numero  # Substitua com o número de telefone real
    message = "Bolinã de gorfe"  # A mensagem que você deseja enviar
    delay_message = 1000  # Atraso de 1000 milissegundos
    auth_token = "xT3AcKpnGLC5VPk49fhTlCLwk1VkuU9Up"  # Substitua com seu token de autenticação

    # Chamando a função para enviar a mensagem
    resultado = await enviar_mensagem(api_url, connection_key, phone_number, message, delay_message, auth_token)

    return {"status": "success", "message": "Mensagem recebida com sucesso! Este é um teste."}
