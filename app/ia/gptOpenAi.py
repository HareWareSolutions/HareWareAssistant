from openai import OpenAI
import requests


assistant_id_openai = {
    "hareware": [
        "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",
        "asst_pb8dfn9OtyXz4c0s9pZMOXSQ"
    ],
    "emyconsultorio": [
        "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",
        "asst_I7AwY6tfrzdqIPQ2xsImgKk3"
    ]
}


def ask_to_openai(code, pergunta):
    try:
        if code not in assistant_id_openai:
            return "Erro: Código do assistente inválido."

        api_key, assistant_id = assistant_id_openai[code]

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
