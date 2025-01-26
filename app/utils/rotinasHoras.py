from datetime import datetime
import pytz


def verificar_horarios(env, agendamentos, data_agendamento):
    horarios_disponiveis = {
        'hareware': [{"08:00": 1}, {"09:00": 1}, {"10:00": 1}, {"11:00": 1}, {"13:00": 1}, {"14:00": 1}, {"15:00": 1}, {"16:00": 1}, {"17:00": 1}, {"18:00": 1}],
        'joice': [{"06:30": 1}, {"09:00": 1}, {"11:30": 1}, {"14:00": 1}, {"16:30": 1}, {"19:00": 1}],
        'malaman': [{"08:00": 1}, {"09:00": 1}, {"10:00": 1}, {"11:00": 1}, {"12:00": 1}, {"13:00": 1}, {"14:00": 1}, {"15:00": 1}, {"16:00": 1}, {"17:00": 1}, {"18:00": 1}],
        'malaman-sabado': [{"07:00": 1}, {"08:00": 1}, {"09:00": 1}, {"10:00": 1}, {"11:00": 1}, {"12:00": 1}, {"13:00": 1}, {"14:00": 1}]
    }

    tz = pytz.timezone('America/Sao_Paulo')
    horario_atual = datetime.now(tz)
    horario_atual_str = horario_atual.strftime('%H:%M')
    data_atual = horario_atual.strftime('%Y-%m-%d')

    if data_agendamento == data_atual:
        for horario_disponivel in horarios_disponiveis[env]:
            hora = list(horario_disponivel.keys())[0]
            if hora <= horario_atual_str:
                horario_disponivel[hora] = 0

    for agendamento in agendamentos:
        horario_agendado = agendamento[:5]
        for horario_disponivel in horarios_disponiveis[env]:
            if horario_agendado in horario_disponivel:
                horario_disponivel[horario_agendado] = 0

    horarios_livres = []
    for horario_disponivel in horarios_disponiveis[env]:
        for hora, disponibilidade in horario_disponivel.items():
            if disponibilidade == 1:
                horarios_livres.append(hora)

    return horarios_livres
