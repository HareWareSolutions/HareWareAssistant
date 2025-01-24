import logging
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

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

# Conjunto para armazenar os IDs das mensagens processadas
# Usaremos um dicionário para armazenar o ID da mensagem com o timestamp da última vez que foi processada.
processed_message_ids = {}


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

    # Extraindo o ID da mensagem
    message_id = data['body']['key']['id']

    # Verificando se a mensagem já foi processada com base no ID
    current_time = time.time()  # Timestamp atual
    if message_id in processed_message_ids:
        last_processed_time = processed_message_ids[message_id]
        if current_time - last_processed_time < 5:  # Exemplo de janela de 5 segundos (ajustar conforme necessário)
            logging.info(f"Mensagem duplicada detectada (ID: {message_id}). Ignorando envio.")
            return {"status": "ignored", "message": "Mensagem duplicada detectada, não processada."}

    # Armazenando o ID da mensagem com o timestamp atual
    processed_message_ids[message_id] = current_time

    # Printando os dados recebidos na requisição
    remote_jid = data['body']['key']['remoteJid']
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
