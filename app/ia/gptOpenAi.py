from openai import OpenAI
import requests


assistant_id_openai = {
    "hareware": [
        "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",
        "asst_pb8dfn9OtyXz4c0s9pZMOXSQ"
    ],
    "emyconsultorio": [
        "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",
        "asst_H5Bhwe8cXpeCLfINj3ilZury"
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
