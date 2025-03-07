from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')


async def dia_da_semana(data):
    return data.strftime("%A")


