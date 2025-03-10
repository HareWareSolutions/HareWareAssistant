import time
from openai import AzureOpenAI



foundry_endpoint = "https://hareware-openai.openai.azure.com/"
foundry_key = "Tft6fly9yH8Yx6yyXz7vaM6g3iQIXBaQ8b69vFZ4l23ewuBc8W6tJQQJ99AKACYeBjFXJ3w3AAABACOGRcxn"
assistant_id_foundry = {
    "hareware": "asst_z0XpoKoyLqtUmyEW6oNH0hlO",
    "emyconsultorio": "asst_8RLF74DaqKV3qDnDfRoY3T0B"
    }


client = AzureOpenAI(
    azure_endpoint=foundry_endpoint,
    api_key=foundry_key,
    api_version="2024-05-01-preview"
)


def send_message_to_ai(code: str, message_content: str):
    thread = create_thread()

    send_message(thread.id, message_content)

    run = start_run(thread.id, assistant_id_foundry[code])

    run_status = wait_for_run_to_complete(run, thread.id)

    return get_assistant_reply(run_status, thread.id)


def create_thread():
    return client.beta.threads.create()


def send_message(thread_id, message_content):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_content
    )


def start_run(thread_id, assistant_id):
    return client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )


def wait_for_run_to_complete(run, thread_id):
    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
    return run


def get_assistant_reply(run_status, thread_id):
    if run_status.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        for message in messages:
            if message.role == 'assistant':
                return message.content
    elif run_status.status == 'requires_action':
        return "A IA precisa de uma ação adicional."
    elif run_status.status == 'incomplete':
        return "Desculpa, não consegui compreender o que você disse, poderia dizer novamente porém de outra forma?"
    elif run_status.status == 'failed':
        return "Desculpa, mas meu sistema cognitivo falhou, poderia escrever novamente a sua mensagem?"
    else:
        return f"Status do run: {run_status.status}"


