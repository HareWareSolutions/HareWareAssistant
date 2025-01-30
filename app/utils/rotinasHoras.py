from datetime import datetime
import pytz

def verificar_horarios(env, agendamentos, data_agendamento):
    horarios_disponiveis = {
        'hareware': {"08:00": 1, "09:00": 1, "10:00": 1, "11:00": 1, "13:00": 1, "14:00": 1, "15:00": 1, "16:00": 1, "17:00": 1, "18:00": 1},
        'joice': {"06:30": 1, "09:00": 1, "11:30": 1, "14:00": 1, "16:30": 1, "19:00": 1},
        'malaman': {"08:00": 1, "09:00": 1, "10:00": 1, "11:00": 1, "12:00": 1, "13:00": 1, "14:00": 1, "15:00": 1, "16:00": 1, "17:00": 1, "18:00": 1},
        'malaman-sabado': {"07:00": 1, "08:00": 1, "09:00": 1, "10:00": 1, "11:00": 1, "12:00": 1, "13:00": 1, "14:00": 1}
    }

    tz = pytz.timezone('America/Sao_Paulo')
    horario_atual = datetime.now(tz)
    horario_atual_str = horario_atual.strftime('%H:%M')
    data_atual = horario_atual.strftime('%d/%m/%Y')

    data_agendamento_dt = datetime.strptime(data_agendamento, "%d/%m/%Y").date()
    data_atual_dt = datetime.strptime(data_atual, "%d/%m/%Y").date()

    if env not in horarios_disponiveis:
        return []

    horarios_disponiveis_finais = {}

    if data_agendamento_dt == data_atual_dt:
        for hora, disponivel in horarios_disponiveis[env].items():
            if datetime.strptime(hora, "%H:%M").time() > horario_atual.time():
                horarios_disponiveis_finais[hora] = disponivel
    elif data_agendamento_dt > data_atual_dt:
        horarios_disponiveis_finais = horarios_disponiveis[env].copy()

    for agendamento in agendamentos:
        horario_agendado = agendamento[:5]
        if horario_agendado in horarios_disponiveis_finais:
            del horarios_disponiveis_finais[horario_agendado]

    horarios_livres = [hora for hora, disponivel in horarios_disponiveis_finais.items() if disponivel == 1]

    return horarios_livres
