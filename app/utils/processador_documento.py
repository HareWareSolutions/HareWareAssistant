'''from app.ia.bmhw01 import ScoreBM25
import nltk
from nltk.stem import RSLPStemmer
from app.models.documento import ler_documentos
from app.db.db import get_db
nltk.download('rslp')


def processar_documento(conteudo_pdf):
    conteudo_formatado = remover_pontuacao(conteudo_pdf)
    conteudo_formatado = remover_stopwords(conteudo_formatado)
    conteudo_formatado = radicalizar(conteudo_formatado)

    return conteudo_formatado


async def formatacoes(env, texto):
    db = next(get_db(env))
    try:
        formatacao_pergunta = remover_pontuacao(texto)
        formatacao_pergunta = remover_stopwords(formatacao_pergunta)
        formatacao_pergunta = radicalizar(formatacao_pergunta)

        titulos_formatados = {}
        registros = ler_documentos()
        for registro in registros:
            titulo = registro.titulo
            titulo = remover_pontuacao(titulo)
            titulo = remover_stopwords(titulo)
            titulo = radicalizar(titulo)
            titulos_formatados[registro.id] = (titulo)

        return formatacao_pergunta, titulos_formatados, len(registros)
    finally:
        db.close()


async def calcular_tokens_titulos(titulos_formatados):
    total_tokens = 0
    tokens_por_titulo = {}
    for id in titulos_formatados:
        total_tokens += len(titulos_formatados[id])
        tokens_por_titulo[id] = len(titulos_formatados[id])
    return total_tokens, tokens_por_titulo


async def calcular_repeticao_geral(termos_perguntas, termos_textos):
    repeticao_termos_perguntas = {}

    for termo_pergunta in termos_perguntas:
        repeticao_termo = 0

        for id in termos_textos:
            for termo_chave in termos_textos[id]:
                if termo_pergunta == termo_chave:
                    repeticao_termo += 1

        repeticao_termos_perguntas[termo_pergunta] = repeticao_termo

    return repeticao_termos_perguntas


async def calcular_repeticao_por_documento(termos_perguntas, termos_textos):
    tokens_por_documentos = {}

    for termo_pergunta in termos_perguntas:

        qtd_por_documentos = {}
        for id in termos_textos:
            repeticao_termo = 0
            for termo_chave in termos_textos[id]:
                if termo_pergunta == termo_chave:
                    repeticao_termo += 1
            qtd_por_documentos[id] = repeticao_termo
        tokens_por_documentos[termo_pergunta] = qtd_por_documentos

    return tokens_por_documentos


async def calcular_score(total_documentos, repeticoes_termos_perguntas, total_tokens_documentos, tokens_por_documento):
    idf = {}
    for termo in repeticoes_termos_perguntas:
        if repeticoes_termos_perguntas[termo] > 0:
            idf_termo = ScoreBM25(total_documentos=total_documentos, total_documento_termo=repeticoes_termos_perguntas[termo]).inverse_term_frequency()
            idf[termo] = idf_termo

    tf = {}
    for termo_pesquisa, documento_termos in tokens_por_documento.items():
        term_frequency = {}
        for id, termos_documento in documento_termos.items():
            if termos_documento > 0:
                tf_documento = ScoreBM25(total_termos_documento=termos_documento, total_documentos=total_documentos, total_tokens_documento=total_tokens_documentos).term_frequency()
                term_frequency[id] = tf_documento

        if term_frequency:
            tf[termo_pesquisa] = term_frequency

    pontuacoes_doc = {}
    anterior = 0

    for termo_tf, tf_doc in tf.items():
        tf_doc_ordenado = dict(sorted(tf_doc.items()))

        for id_doc, term_f in tf_doc_ordenado.items():
            score_doc = ScoreBM25(idf=idf[termo_tf], tf=term_f).score()

            if id_doc in pontuacoes_doc:
                soma = pontuacoes_doc[id_doc] + score_doc
                pontuacoes_doc[id_doc] = soma
            else:
                pontuacoes_doc[id_doc] = score_doc

            anterior = id_doc

    pontuacoes_ordenadas = sorted(pontuacoes_doc.items(), key=lambda x: x[1], reverse=True)

    maiores_pontuacoes = pontuacoes_ordenadas[:3]

    return maiores_pontuacoes


async def radicalizar(texto):
    stemmer = RSLPStemmer()
    texto_formatado = [stemmer.stem(palavra) for palavra in texto]

    return texto_formatado


async def remover_stopwords(texto):
    stopwords = ("a à aí agora ainda alguém algum alguma algumas alguns ali ano "
                 "anos antes até bem cada com como contra da daquele daqueles das"
                 " de dela delas deles depois desde desta destas deste deste dia "
                 "dias disse disso disto dólar dois dos é ela elas eles em entre "
                 "então era essa essas esse esses esta está estas estava estavam "
                 "este esteve estive estivemos estiveram estiverem estivermos eu "
                 "foi for foram fosse fossem fui fôssemos geral grandes há até "
                 "depois dentro fora iam isso isto já lugar mais mas meu minha "
                 "minhas meus mês meses muito na nada não nome no nos nós nada "
                 "nem nenhum nenhuma nenhumas nenhuns nunca nuns o onde os ou "
                 "outra outras outro outros para pela pelo pelas pelos pessoa pode "
                 "podem por porém qual quando quem quero seu sua suas seus sempre ser"
                 " será serão seu seus sobre somos tal tem tempo tenho teu tua tuas teus"
                 " tudo um uma umas uns vontade vez vezes você vocês")

    texto_separado = texto.split()
    texto_formatado = []

    for palavra in texto_separado:
        if palavra not in stopwords:
            texto_formatado.append(palavra)

    return texto_formatado


async def remover_pontuacao(texto):
    pontuacao = ".,;:!?()[]{}--\/*&=+-"
    texto_minusculo = texto.lower()
    texto_formatado = ''

    for char in texto_minusculo:
        if char not in pontuacao:
            texto_formatado += char

    return texto_formatado

'''