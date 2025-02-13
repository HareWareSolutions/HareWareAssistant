from openai import OpenAI
import requests


client = OpenAI(api_key="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")

assistant_id_openai = {
    "hareware": "asst_pb8dfn9OtyXz4c0s9pZMOXSQ",
    "emyconsultorio": "asst_XnR71BKSAU4dceGOranD7qJb"
    }


def ask_to_openai(code, pergunta):
    try:
        thread = client.beta.threads.create()

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=pergunta
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id_openai[code]
        )

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            return messages.data[0].content[0].text.value
        elif run.status == 'failed':
            return "Desculpa, mas meu sistema cognitivo falhou, poderia escrever novamente a sua mensagem?"
        elif run.status == 'incomplete':
            return "Desculpa, não consegui compreender o que você disse, poderia dizer novamente porém de outra forma?"
        else:
            return f"Erro: {run.status}"
    except requests.exceptions.Timeout:
        return "Erro de conexão: O tempo de espera pela resposta da API excedeu o limite."
    except requests.exceptions.RequestException as e:
        return f"Erro de requisição: {str(e)}"
    except KeyError:
        return "Erro: O código do assistente fornecido é inválido."
    except Exception as e:
        return f"Erro inesperado: {str(e)}"
