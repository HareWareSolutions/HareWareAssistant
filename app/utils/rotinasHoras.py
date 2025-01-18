def verificar_horarios(env, agendamentos):

    horarios_disponiveis = {
        'hareware': [{"08:00": 1}, {"09:00": 1}, {"10:00": 1}, {"11:00": 1}, {"13:00": 1}, {"14:00": 1}, {"15:00": 1}, {"16:00": 1}, {"17:00": 1}, {"18:00": 1}],
        'joice': [{"06:30": 1}, {"09:00": 1}, {"11:30": 1}, {"14:00": 1}, {"16:30": 1}, {"19:00": 1}],
        'malaman': [{"08:30": 1}, {"09:30": 1}, {"10:30": 1}, {"11:30": 1}, {"12:30": 1}, {"13:30": 1}, {"14:30": 1}, {"15:30": 1}, {"16:30": 1}, {"17:30": 1}],
        'malaman-sabado': [{"7:00": 1}, {"08:00": 1}, {"09:00": 1}, {"10:00": 1}, {"11:00": 1}, {"12:00": 1}, {"13:00": 1}, {"14:00": 1}]
    }

    for agendamento in agendamentos:
        horario = agendamento[:5]

        for horario_disponivel in horarios_disponiveis[env]:
            if horario in horario_disponivel:
                horario_disponivel[horario] = 0

    horarios_livres = []
    for horario_disponivel in horarios_disponiveis[env]:
        for hora, disponibilidade in horario_disponivel.items():
            if disponibilidade == 1:
                horarios_livres.append(hora)

    return horarios_livres
