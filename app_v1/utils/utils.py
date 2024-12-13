

words_scheduling = [
    "agendar", "marcar", "reservar", "agendamento", "disponibilidade", "data", "hora", "agenda",
    "reunião", "demonstração", "marcação", "confirmar", "marcar uma reunião", "agendar horário",
    "marcar demonstração", "agendar uma sessão", "proposta de data", "disponível para",
    "confirmar presença", "sugestão de horário", "marcar encontro", "dia e hora", "planejar",
    "reservar horário", "solicitar agendamento", "iniciar reunião", "agendar visita", "programar",
    "horário disponível", "ajustar horário"
]

request_words = [
    "pedido", "solicitar", "gostaria de", "quero", "preciso", "desejo", "por favor", "favor",
    "poderia", "gostaria", "necessito", "posso", "ajuda", "preciso de", "seria possível", "agende", "reserve",
    "marque"
]


def check_request(prompt):
    prompt = prompt.lower()

    for word in request_words:
        if word.lower() in prompt:
            return True
    return False


def check_schedule(prompt):
    prompt = prompt.lower()

    for word in words_scheduling:
        if word.lower() in prompt:
            return True
    return False