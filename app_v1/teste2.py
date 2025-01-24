import requests
import json

# URL da API (Substitua com a URL real conforme instruções do Postman)
url = "https://host13.serverapi.dev/message/sendText?connectionKey=w-api_N3IE7GZOFN"

# Dados da mensagem
data = {
    "phoneNumber": "5519997581672",  # Substitua pelo número real
    "message": "oi, teste",
    "delayMessage": "1000"  # Atraso de 1000 ms
}

# Headers (caso necessário, adicione cabeçalhos como Content-Type ou Auth)
headers = {
    "Content-Type": "application/json",
    # Adicione outros cabeçalhos se necessário, como:
    "Authorization": "Bearer xT3AcKpnGLC5VPk49fhTlCLwk1VkuU9Up"
}

# Enviar a requisição POST
response = requests.post(url, json=data, headers=headers)

# Verificar a resposta da API
if response.status_code == 200:
    print("Mensagem enviada com sucesso!")
    print("Resposta:", response.json())  # Mostra o retorno em formato JSON
else:
    print(f"Erro ao enviar a mensagem. Status: {response.status_code}")
    print("Resposta:", response.text)