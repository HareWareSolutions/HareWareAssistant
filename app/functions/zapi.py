import os
import re
import json
from dotenv import load_dotenv
import requests

load_dotenv()

client_token_zapi = os.getenv('ZAPI_CLIENT_TOKEN')
zapi_instance = os.getenv('ZAPI_INSTANCIA')
token_zapi = os.getenv('ZAPI_TOKEN')


def send_message_zapi(number, message, delay_typing=0):
    if isinstance(message, list):
        message = message[0].text.value

    edited_message = remove_word(message)

    url = f"https://api.z-api.io/instances/{zapi_instance}/token/{token_zapi}/send-text"
    headers = {
        'Content-Type': 'application/json',
        'Client-Token': client_token_zapi
    }
    payload = {
        "phone": number,
        "message": edited_message,
        "delayTyping": delay_typing
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Mensagem enviada com sucesso!")
        else:
            print(f"Falha ao enviar a mensagem. Código de status: {response.status_code}")
            print(f"Resposta da API: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar a mensagem: {e}")


def remove_word(sentence):
    sentence_without_source = re.sub(r'【\d+:\d+†\([^\)]+\)】', '', sentence)
    sentence_without_source = re.sub(r'【\d+:\d+†[^\]]+】', '', sentence_without_source)
    return sentence_without_source