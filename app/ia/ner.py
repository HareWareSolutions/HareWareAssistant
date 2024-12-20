from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://hareware-language-ai.cognitiveservices.azure.com/"
api_key = "ETSMkUTHDIMitWWiBaJruFnZIaMwQQFoOgaOdikWpuA0Xfblwg0TJQQJ99ALACZoyfiXJ3w3AAAaACOGHXta"

text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))


def reconhecer_entidades(texto):
    try:
        response = text_analytics_client.recognize_entities(documents=[texto])
        resposta = response[0].entities

        entidades = []
        for entidade in resposta:
            entidades.append({entidade.category: entidade.text})

        print(entidades)
        return entidades
    except Exception as e:
        return f"Ocorreu um erro: {str(e)}"


reconhecer_entidades("eu quero um bolo de cenoura vulcão, um bolo de chocolate e um de morango")