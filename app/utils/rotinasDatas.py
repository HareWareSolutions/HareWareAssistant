from datetime import datetime, timedelta
import pytz

fuso_brasil = pytz.timezone("America/Sao_Paulo")


def normalizar_data(data):
    return data.strftime("%d/%m/%Y") if data else None


def extrair_data(frase):
    meses = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
        "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
        "marco": 3
    }
    numeros_por_extenso = {
        "um": 1, "dois": 2, "três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9,
        "dez": 10, "onze": 11, "doze": 12, "treze": 13, "quatorze": 14, "quinze": 15, "dezesseis": 16,
        "dezessete": 17, "dezoito": 18, "dezenove": 19, "vinte": 20, "vinte e um": 21, "vinte e dois": 22,
        "vinte e três": 23, "vinte e quatro": 24, "vinte e cinco": 25, "vinte e seis": 26, "vinte e sete": 27,
        "vinte e oito": 28, "vinte e nove": 29, "trinta": 30, "trinta e um": 31, "tres": 3, "vinte e tres": 23
    }
    dias_semana = {
        "segunda": 0, "terça": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sábado": 5, "domingo": 6,
        "segunda-feira": 0, "terça-feira": 1, "quarta-feira": 2, "quinta-feira": 3, "sexta-feira": 4,
        "terca": 1, "terca-feira": 1, "sabado": 5
    }

    palavras = frase.lower().split()
    agora = datetime.now(fuso_brasil)
    dia, mes, ano = None, agora.month, agora.year

    for i, palavra in enumerate(palavras):
        if palavra.isdigit() and 1 <= int(palavra) <= 31:
            dia = int(palavra)
        elif palavra in numeros_por_extenso:
            dia = numeros_por_extenso[palavra]
        elif palavra in meses:
            mes = meses[palavra]
        elif palavra.isdigit() and len(palavra) == 4:
            ano = int(palavra)
        elif "/" in palavra:
            partes = palavra.split("/")
            if len(partes) >= 2:
                dia, mes = int(partes[0]), int(partes[1])
            if len(partes) == 3:
                ano = int(partes[2])

    if dia:
        return datetime(ano, mes, dia, tzinfo=fuso_brasil).date()

    if "hoje" in palavras:
        return agora.date()
    elif "amanhã" in palavras:
        return (agora + timedelta(days=1)).date()
    elif "amanha" in palavras:
        return (agora + timedelta(days=1)).date()

    for dia_semana, indice in dias_semana.items():
        if dia_semana in palavras:
            dia_atual = agora.weekday()
            delta = (indice - dia_atual) % 7
            if delta == 0:
                delta = 7
            return (agora + timedelta(days=delta)).date()

    return None


def transformar_data_e_hora(data_hora_str: str):
    data_hora = datetime.strptime(data_hora_str, "%d/%m/%Y %H:%M")
    data_hora = fuso_brasil.localize(data_hora)
    data = data_hora.date()
    hora = data_hora.time()
    return data, hora
