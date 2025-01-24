import logging
import requests
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

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


# Definição do modelo Pydantic
class WebhookData(BaseModel):
    message: str


# Função para enviar a mensagem via API
def enviar_mensagem(api_url, connection_key, phone_number, message, delay_message, auth_token):
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
    # URL da API (construída com a chave de conexão)
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

    # Enviar a requisição POST
    response = requests.post(url, json=data, headers=headers)

    # Verificar a resposta da API
    if response.status_code == 200:
        # Supondo que a API retornará uma mensagem de teste no corpo da resposta
        api_response = response.json()
        # Exibindo a resposta com a mensagem de teste
        return {"status": "success", "message": api_response.get("message", "Sem mensagem de teste")}
    else:
        return {"status": "error", "status_code": response.status_code, "response": response.text}


# Endpoint que recebe a mensagem e sempre retorna uma resposta com uma mensagem de teste
@app.post("/webhook-zapi")
async def receive_message(request: Request, data: WebhookData):
    """
    Endpoint que recebe uma mensagem e sempre retorna uma resposta com uma mensagem de teste.
    """
    logging.info(f"Mensagem recebida: {data.message}")

    # Mensagem de teste a ser retornada
    return {"status": "success", "message": "Mensagem recebida com sucesso! Este é um teste."}


# Exemplo de como chamar a função de envio de mensagem
if __name__ == "__main__":
    # Parâmetros para a função de envio
    api_url = "https://host13.serverapi.dev"  # Substitua com o seu host real
    connection_key = "w-api_N3IE7GZOFN"  # Substitua com a chave de conexão real
    phone_number = "5519997581672"  # Substitua com o número de telefone real
    message = "oi, teste"  # A mensagem que você deseja enviar
    delay_message = 1000  # Atraso de 1000 milissegundos
    auth_token = "xT3AcKpnGLC5VPk49fhTlCLwk1VkuU9Up"  # Substitua com seu token de autenticação

    # Chamando a função para enviar a mensagem
    resultado = enviar_mensagem(api_url, connection_key, phone_number, message, delay_message, auth_token)

    # Exibindo o resultado
    if resultado["status"] == "success":
        print("Mensagem enviada com sucesso!")
        print("Resposta da API:", resultado["message"])
    else:
        print(f"Erro ao enviar a mensagem. Código de status: {resultado['status_code']}")
        print("Resposta de erro:", resultado["response"])
