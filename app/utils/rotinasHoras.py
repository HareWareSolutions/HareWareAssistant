

def verificar_horarios(env, agendamentos):

    horarios_disponiveis = {
        'hareware': [{"08:00": 1}, {"09:00": 1}, {"10:00": 1}, {"11:00": 1}, {"13:00": 1}, {"14:00": 1}, {"15:00": 1},{"16:00": 1}, {"17:00": 1}, {"18:00": 1}],
        'joice': [{"06:30": 1}, {"09:00", 1}, {"11:30", 1}, {"14:00", 1}, {"16:30", 1}, {"19:00", 1}],
        'malaman': [{"08:30": 1}, {"09:30": 1}, {"10:30", 1}, {"11:30": 1}, {"12:30", 1}, {"13:30", 1}, {"14:30": 1}, {"15:30", 1}, {"16:30": 1}, {"17:30", 1}]
                            }

    for agendamento in agendamentos:
        horario = agendamento[:5]

        for horario_disponivel in horarios_disponiveis[env]:
            if horario in horario_disponivel:
                horario_disponivel[horario] = 0

    horarios_livres = [list(horario.keys())[0] for horario in horarios_disponiveis if list(horario.values())[0] == 1]

    return horarios_livres
