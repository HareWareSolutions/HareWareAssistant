import pandas as pd
import os


def predicoes_arc(prompt, target):
    arquivo_excel = '/home/hwadmin/HareWareAssistant/app/utils/data/arc.xlsx'

    if os.path.exists(arquivo_excel):
        df = pd.read_excel(arquivo_excel)
    else:
        df = pd.DataFrame(columns=['prompt', 'target'])

    nova_linha = pd.DataFrame({'prompt': [prompt], 'target': [target]})
    df = pd.concat([df, nova_linha], ignore_index=True)

    df.to_excel(arquivo_excel, index=False)


def predicoes_iia(prompt, target):
    arquivo_excel = '/home/hwadmin/HareWareAssistant/app/utils/data/iia.xlsx'

    if os.path.exists(arquivo_excel):
        df = pd.read_excel(arquivo_excel)
    else:
        df = pd.DataFrame(columns=['prompt', 'target'])

    nova_linha = pd.DataFrame({'prompt': [prompt], 'target': [target]})
    df = pd.concat([df, nova_linha], ignore_index=True)

    df.to_excel(arquivo_excel, index=False)
