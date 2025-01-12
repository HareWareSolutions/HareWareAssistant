
def validar_cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * len(cpf):
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10

    return cpf[-2:] == f"{digito1}{digito2}"


def validar_cnpj(cnpj: str) -> bool:
    cnpj = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj) != 14 or cnpj == cnpj[0] * len(cnpj):
        return False

    def calcular_digito(base: str, pesos: list) -> int:
        soma = sum(int(base[i]) * pesos[i] for i in range(len(base)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1

    digito1 = calcular_digito(cnpj[:12], pesos1)
    digito2 = calcular_digito(cnpj[:12] + str(digito1), pesos2)

    return cnpj[-2:] == f"{digito1}{digito2}"


def validar_documento(documento: str) -> bool:
    documento = documento.strip()
    if len(documento) in [11, 14]:
        if len(documento) == 11:
            return validar_cpf(documento)
        elif len(documento) == 14:
            return validar_cnpj(documento)
    return False

