

def verificar_horarios(agendamentos):

    horarios_disponiveis = [{"08:00": 1}, {"09:00": 1}, {"10:00": 1}, {"11:00": 1}, {"13:00": 1}, {"14:00": 1}, {"15:00": 1},
                            {"16:00": 1}, {"17:00": 1}, {"18:00": 1}]

    for agendamento in agendamentos:
        horario = agendamento[:5]

        for horario_disponivel in horarios_disponiveis:
            if horario in horario_disponivel:
                horario_disponivel[horario] = 0

    horarios_livres = [list(horario.keys())[0] for horario in horarios_disponiveis if list(horario.values())[0] == 1]

    return horarios_livres
