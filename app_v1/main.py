import logging
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


# Definindo um modelo para validar o corpo da requisição
class WebhookMessage(BaseModel):
    phoneNumber: str
    message: str


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
async def receive_message(request: Request, payload: WebhookMessage):
    # Extraindo o número do telefone e a mensagem do corpo da requisição
    user_phone_number = payload.phoneNumber
    user_message = payload.message

    # Aqui você pode personalizar a mensagem que será enviada de volta
    response_message = f"Oi! Recebemos sua mensagem: '{user_message}'. O número de telefone enviado foi: {user_phone_number}"

    # Parâmetros da API de envio de mensagem
    api_url = "https://host13.serverapi.dev"  # Substitua com o seu host real
    connection_key = "w-api_N3IE7GZOFN"  # Substitua com a chave de conexão real
    phone_number = "5519997581672"  # Substitua com o número de telefone real
    delay_message = 1000  # Atraso de 1000 milissegundos
    auth_token = "xT3AcKpnGLC5VPk49fhTlCLwk1VkuU9Up"  # Substitua com seu token de autenticação

    # Chamando a função para enviar a mensagem
    resultado = await enviar_mensagem(api_url, connection_key, phone_number, response_message, delay_message,
                                      auth_token)

    return {"status": "success",
            "message": f"Mensagem recebida com sucesso! Número de telefone: {user_phone_number}. Este é um teste."}
