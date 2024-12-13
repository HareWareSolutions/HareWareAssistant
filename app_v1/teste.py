import calendar

# Dicionário para armazenar compromissos com horário
compromissos = {}

def mostrar_calendario(ano, mes):
    # Gera o calendário do mês
    cal = calendar.month(ano, mes)
    return cal

def adicionar_compromisso(data, hora, compromisso):
    # Adiciona um compromisso com hora ao dicionário, permitindo múltiplos compromissos por data
    if data not in compromissos:
        compromissos[data] = []
    compromissos[data].append({'hora': hora, 'compromisso': compromisso})

def mostrar_compromissos():
    # Exibe todos os compromissos armazenados
    for data, compromisso_lista in compromissos.items():
        for compromisso_info in compromisso_lista:
            hora = compromisso_info['hora']
            compromisso = compromisso_info['compromisso']
            print(f"Data: {data} - Hora: {hora} - Compromisso: {compromisso}")

# Solicita ano e mês ao usuário
ano = int(input("Digite o ano: "))
mes = int(input("Digite o mês: "))

# Exibe o calendário do mês
calendario_mensal = mostrar_calendario(ano, mes)
print(calendario_mensal)

# Permite ao usuário adicionar compromissos
while True:
    data = input("Digite a data para adicionar um compromisso (dd/mm/aaaa) ou 'sair' para encerrar: ")
    if data.lower() == 'sair':
        break
    hora = input("Digite o horário do compromisso (hh:mm): ")
    compromisso = input("Digite o compromisso: ")
    adicionar_compromisso(data, hora, compromisso)

# Exibe todos os compromissos após o usuário adicionar
print("\nCompromissos agendados:")
mostrar_compromissos()
