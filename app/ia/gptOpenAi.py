from openai import OpenAI
import requests
from app.db.db import get_db
from app.models.clientes import buscar_cliente_nome
from app.models.contrato import buscar_contrato_por_id


async def get_credentials(code):
    async with get_db('hwadmin') as db:
        try:
            contrato = await buscar_contrato_por_id(db, code)
            return contrato.api_key_ia, contrato.assistant_id
        except Exception as e:
            return f"Erro ao buscar contrato: {str(e)}"


async def ask_to_openai(id_contrato, pergunta):
    try:
        api_key, assistant_id = await get_credentials(id_contrato)

        client = OpenAI(api_key=api_key)

        thread = client.beta.threads.create()

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=pergunta
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            return messages.data[0].content[0].text.value
        elif run.status == "failed":
            return "Desculpa, mas meu sistema cognitivo falhou. Poderia escrever novamente sua mensagem?"
        elif run.status == "incomplete":
            return "Desculpa, não consegui compreender. Poderia reformular sua pergunta?"
        else:
            return f"Erro: {run.status}"

    except requests.exceptions.Timeout:
        return "Erro de conexão: O tempo de espera pela resposta da API excedeu o limite."
    except requests.exceptions.RequestException as e:
        return f"Erro de requisição: {str(e)}"
    except KeyError:
        return "Erro: Código do assistente inválido."
    except Exception as e:
        return f"Erro inesperado: {str(e)}"
