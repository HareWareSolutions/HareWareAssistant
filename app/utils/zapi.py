import os
import re
from dotenv import load_dotenv
import requests

load_dotenv()

#client_token_zapi = os.getenv('ZAPI_CLIENT_TOKEN')
#zapi_instance = os.getenv('ZAPI_INSTANCIA')
#token_zapi = os.getenv('ZAPI_TOKEN')


def get_credentials(env):
    if env == 'hareware':
        client_token_zapi = "F4d0341838a8d4eddad0be7bda51ce724S"
        zapi_instance = "3D8E853051C5D0C0BCB04A0EF4D5AC96"
        token_zapi = "1FB88ED2D493FCC6B436C9B3"
    elif env == 'mmania':
        client_token_zapi = "F4d0341838a8d4eddad0be7bda51ce724S"
        zapi_instance = "3DA117F2FB115098C9701A5D138A61BB"
        token_zapi = "E20500BA1D9262121B984AC7"
    elif env == 'malaman':
        client_token_zapi = "F4d0341838a8d4eddad0be7bda51ce724S"
        zapi_instance = "3DBBCB685FBD10930FDDEEBFCAD96732"
        token_zapi = "B152191B0734E9872587B74E"

    return client_token_zapi, zapi_instance, token_zapi


def send_message_zapi(env, number, message, delay_typing=0):
    client_token_zapi, zapi_instance, token_zapi = get_credentials(env)

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


def send_poll_zapi(env, number, question, options):
    client_token_zapi, zapi_instance, token_zapi = get_credentials(env)

    url = f"https://api.z-api.io/instances/{zapi_instance}/token/{token_zapi}/send-poll"
    headers = {
        'Content-Type': 'application/json',
        'Client-Token': client_token_zapi
    }
    payload = {
        "phone": number,
        "message": question,
        "pollMaxOptions": 1,
        "poll": options,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Enquete enviada com sucesso!")
        else:
            print(f"Falha ao enviar a enquete. Código de status: {response.status_code}")
            print(f"Resposta da API: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar a enquete: {e}")


def send_document_zapi(env, number, document_url, file_name):
    client_token_zapi, zapi_instance, token_zapi = get_credentials(env)

    url = f"https://api.z-api.io/instances/{zapi_instance}/token/{token_zapi}/send-document/pdf"
    headers = {
        'Content-Type': 'application/json',
        'Client-Token': client_token_zapi
    }
    payload = {
        "phone": number,
        "document": document_url,
        "fileName": file_name
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Documento enviado com sucesso!")
        else:
            print(f"Falha ao enviar o documento. Código de status: {response.status_code}")
            print(f"Resposta da API: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar o documento: {e}")


def remove_word(sentence):
    sentence_without_source = re.sub(r'【\d+:\d+†\([^\)]+\)】', '', sentence)
    sentence_without_source = re.sub(r'【\d+:\d+†[^\]]+】', '', sentence_without_source)
    return sentence_without_source