

async def caracteres_numericos(conteudo_mensagem):
    return any(char.isdigit() for char in conteudo_mensagem)


async def caracteres_invalidos(conteudo_mensagem):
    caracteres_invalidos = [caractere for caractere in conteudo_mensagem if not (caractere.isalnum() or caractere.isspace())]
    return caracteres_invalidos