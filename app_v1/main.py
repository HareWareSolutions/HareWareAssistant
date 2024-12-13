import logging
from pydantic import BaseModel
from fastapi import FastAPI, Request
from functions.zapi import send_message_zapi
from functions.foundry import send_message_to_ai
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


@app.post("/webhook-zapi")
async def receive_message(request: Request):
    try:
        data = await request.json()
        logging.info(f"Dados recebidos: {data}")

        number = data.get("phone")
        if not number:
            logging.error("Número de telefone não encontrado.")
            return {"status": "error", "message": "Número de telefone não encontrado."}

        text_message = data.get("text", {}).get("message")
        imagem_url = data.get("image", {}).get("imageUrl")
        captions = data.get("image", {}).get("caption")

        if imagem_url:
            logging.info(f"Imagem recebida: {imagem_url}")
            if captions:
                logging.info(f"captions da imagem: {captions}")
            response = "Infelizmente no momento ainda não consigo analisar imagens..."

            send_message_zapi(
                number=number,
                message=response,
                delay_typing=5
            )

        if text_message:
            logging.info(f"Mensagem de texto recebida: {text_message}")

            response = send_message_to_ai(text_message)
            send_message_zapi(
                number=number,
                message=response,
                delay_typing=5
            )

        return {"status": "success"}

    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {str(e)}")
        return {"status": "error", "message": str(e)}
