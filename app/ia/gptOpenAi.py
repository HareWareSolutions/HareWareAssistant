from openai import OpenAI

client = OpenAI(api_key="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")

assistant_id_openai = {
    "hareware": "asst_pb8dfn9OtyXz4c0s9pZMOXSQ",
    "emyconsultorio": ""
    }


def ask_to_openai(code, pergunta):
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
    else:
        return f"Erro: {run.status}"


if __name__ == "__main__":
    resposta = ask_to_openai('hareware', "Onde está o endereço da empresa?")
    print(resposta)
