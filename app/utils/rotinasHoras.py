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

    horarios_disponiveis_convertidos = [
        {datetime.strptime(hora, '%H:%M'): disponibilidade for hora, disponibilidade in horario.items()}
        for horario in horarios_disponiveis[env]
    ]

    if data_agendamento == data_atual:
        horarios_disponiveis_convertidos = [
            horario for horario in horarios_disponiveis_convertidos if list(horario.keys())[0] > horario_atual
        ]
    elif data_agendamento > data_atual:
        pass

    for agendamento in agendamentos:
        horario_agendado = datetime.strptime(agendamento[:5], '%H:%M')
        for horario_disponivel in horarios_disponiveis_convertidos:
            if horario_agendado in horario_disponivel:
                horario_disponivel[horario_agendado] = 0

    horarios_livres = []
    for horario_disponivel in horarios_disponiveis_convertidos:
        for hora, disponibilidade in horario_disponivel.items():
            if disponibilidade == 1 and (data_agendamento > data_atual or hora > horario_atual_str):
                horarios_livres.append(hora.strftime('%H:%M'))

    return horarios_livres
