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
    data_atual = horario_atual.strftime('%d/%m/%Y')
    data_atual_dt = datetime.strptime(data_atual, '%d/%m/%Y')

    horarios_disponiveis_finais = []

    if data_agendamento == data_atual_dt:
        for horario_disponivel in horarios_disponiveis[env]:
            hora = list(horario_disponivel.keys())[0]
            hora_dt = datetime.strptime(hora, '%H:%M').replace(year=horario_atual.year, month=horario_atual.month, day=horario_atual.day)
            if hora_dt > horario_atual:
                horarios_disponiveis_finais.append(horario_disponivel)

    elif data_agendamento > data_atual_dt:
        horarios_disponiveis_finais = horarios_disponiveis[env]

    for agendamento in agendamentos:
        horario_agendado = agendamento[:5]
        horarios_disponiveis_finais = [horario for horario in horarios_disponiveis_finais if list(horario.keys())[0] != horario_agendado]

    horarios_livres = [list(horario.keys())[0] for horario in horarios_disponiveis_finais if list(horario.values())[0] == 1]

    return horarios_livres
