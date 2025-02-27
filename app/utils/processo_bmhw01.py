'''from app.utils.processador_documento import formatacoes, calcular_repeticao_geral, calcular_repeticao_por_documento, calcular_tokens_titulos, calcular_score
from app.models.documento import ler_documento, somar_quantidade_tokens
from app.utils.manipulador_pdf import extrair_bytea
from app.db.db import get_db


async def processo_bmhw01(env, prompt):
    db = next(get_db(env))
    try:
        prompt_formatado, titulos_formatados, total_documentos = await formatacoes(env, prompt.pergunta)

        repeticao_termos_pergunta = await calcular_repeticao_geral(prompt_formatado, titulos_formatados)

        tokens_por_documento = await calcular_repeticao_por_documento(prompt_formatado, titulos_formatados)

        total_tokens_titulos, tokens_por_titulo = await calcular_tokens_titulos(titulos_formatados)

        score_titulos = await calcular_score(total_documentos, repeticao_termos_pergunta, total_tokens_titulos,tokens_por_documento)

        conteudos_docs = {}
        quantidade_tokens_pdf = {}
        for chave, valor in score_titulos:
            registro = ler_documento(db, chave)
            valor_bytea = registro.pdf_processado
            conteudo_chave = await extrair_bytea(valor_bytea)
            conteudo_chave = conteudo_chave.split()
            conteudos_docs[chave] = conteudo_chave
            quantidade_tokens_pdf[chave] = registro.quantidade_tokens

        repeticao_termos_prompt = await calcular_repeticao_geral(prompt_formatado, conteudos_docs)
        tokens_por_pdf = await calcular_repeticao_por_documento(prompt_formatado, conteudos_docs)
        total_tokens_pdf = await somar_quantidade_tokens(db)
        score = await calcular_score(total_documentos, repeticao_termos_prompt, total_tokens_pdf, tokens_por_pdf)

        melhor_documento = next(iter(score))
        registro_md = ler_documento(db, melhor_documento[0])
        bytea_md = registro_md.pdf_original
        conteudo_md = await extrair_bytea(bytea_md)
        #prompt_gpt = montar_prompt_gpt(prompt.pergunta, conteudo_md)
        #resposta = GPT(prompt_gpt).gerar_resposta()
        #return {"resposta": resposta}
    finally:
        db.close()
'''