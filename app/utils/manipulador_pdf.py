'''import fitz


async def extrair(arquivo):
    text = ""
    caminho_arquivo = '/home/hwadmin/HareWareAssistant/app/utils/documentos/' + arquivo
    with fitz.open(caminho_arquivo) as pdf:
        for page_num in range(len(pdf)):
            page = pdf.load_page(page_num)
            text += page.get_text()
    return text


async def gerar_processado(textos, nome_arquivo):
    caminho = '/home/hwadmin/HareWareAssistant/app/utils/documentos-processados/' + nome_arquivo
    pdf = fitz.open()

    for texto in textos:
        page = pdf.new_page(width=612, height=792)
        page.insert_text((10, 10), texto)

    pdf.save(caminho)
    pdf.close()


async def extrair_bytea(bytea):
    doc = fitz.open(stream=bytea, filetype="pdf")
    texto_extraido = ""
    for pagina in doc:
        texto_extraido += pagina.get_text()
    return texto_extraido
'''