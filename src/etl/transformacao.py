from datetime import datetime
from decimal import Decimal


# --- Funções auxiliares (regras A3, A4, A5 e A6) ---

def tratar_email(email):
    """
    A1: mantém None se o e-mail vier ausente/nulo, ou retorna o próprio e-mail.
    """
    # Se email for None (ou vazio, se quiser cobrir ""), retornar None
    # Caso contrário, retornar email
    if email is None:
        return None
    else:
        return email


def normalizar_estado(estado):
    """
    A2: recebe a sigla do estado (ex.: 'mg') e retorna em maiúsculas ('MG').
    """
    return estado.upper()

def converter_data(texto_data):
    """
    A3: recebe string em 'AAAA-MM-DD' ou 'DD/MM/AAAA'
    e retorna um objeto datetime.date.
    """

    if "/" in texto_data:
        data = datetime.strptime(texto_data, "%d/%m/%Y")
    else:
        data = datetime.strptime(texto_data, "%Y-%m-%d")

    return data.date()


def normalizar_valor(valor):
    """
    A4: recebe número (int/float) ou string com vírgula (ex.: '125,84')
    e retorna valor numérico com 2 casas decimais.
    """

    if(type(valor) == str):
        valor = Decimal(valor.replace(",", ".")).quantize(Decimal("0.01"))
    else:
        valor = Decimal(str(valor).replace(",", ".")).quantize(Decimal("0.01"))
           
    return valor

def deduplicar_pedidos(pedidos_brutos):
    """
    A5: remove pedidos com 'id' repetido, mantendo a primeira ocorrência.
    Retorna: (pedidos_unicos, total_duplicados)
    """
    ids_vistos = set()
    pedidos_unicos = []
    total_duplicados = 0

    for i in pedidos_brutos:
        if i["id"] in ids_vistos:
            total_duplicados += 1
        else:
            pedidos_unicos.append(i) 
            ids_vistos.add(i["id"])

    return pedidos_unicos, total_duplicados

def calcular_valor_itens(itens):
    """
    A6: soma (quantidade * preco_unitario) de todos os itens de um pedido.
    Retorna: valor total calculado dos itens com 2 casas decimais.
    """

    total = Decimal("0.00")

    for item in itens:
        preco = normalizar_valor(item["preco_unitario"])
        total += item["quantidade"] * preco

    return total

def eh_divergente(valor_total, valor_itens):
    """
    A6: retorna True se a diferença absoluta entre valor_total (vindo do dataset) e valor_itens (calculado em calcular_valor_itens)
    for maior que um centavo (0.01), ou False caso contrário.
    """

    if abs(valor_total-valor_itens) > Decimal("0.01"):
        return True
    else:
        return False

def transf_clientes(clientes_brutos):
    """
    Aplica armadilhas A1 e A2.
    Conta quantidade de e-mails nulos e estados corrigidos
    Retorna duas listas: clientes_limpos e contadores_clientes
    """
    contadores = {"emails_nulos": 0, "estados_corrigidos": 0}
    clientes_limpos = []
    
    for i in clientes_brutos:
        email = tratar_email(i["email"])
        if email is None:
            contadores["emails_nulos"]+=1

        estado = normalizar_estado(i["estado"])
        if estado != i["estado"]:
            contadores["estados_corrigidos"]+=1

        dados_transformados = {"id": i["id"], "nome": i["nome"], "email": email, "cidade": i["cidade"], "estado": estado, "cadastro_em": i["cadastro_em"]}
        clientes_limpos.append(dados_transformados)

    return clientes_limpos, contadores

def transf_pedidos(pedidos_brutos):
    """
    Aplica armadilhas A3, A4, A5 e A6.
    Conta duplicados, datas convertidas, valores convertidos e divergentes.
    Retorna: pedidos_limpos, itens_limpos e contadores
    """
    pedidos_unicos, total_duplicados = deduplicar_pedidos(pedidos_brutos)

    contadores = {
        "duplicados": total_duplicados,
        "datas_convertidas": 0,
        "valores_convertidos": 0,
        "divergentes": 0
    }
    pedidos_limpos = []
    itens_limpos = []

    for i in pedidos_unicos:
        if "/" in i["data_pedido"]:
            contadores["datas_convertidas"] += 1
        data_pedido = converter_data(i["data_pedido"])

        if type(i["valor_total"]) == str:
            contadores["valores_convertidos"] += 1
        valor_total = normalizar_valor(i["valor_total"])

        valor_itens = calcular_valor_itens(i["itens"])
        divergente = eh_divergente(valor_total, valor_itens)
        if divergente:
            contadores["divergentes"] += 1

        dados_pedido = {
            "id": i["id"],
            "cliente_id": i["cliente_id"],
            "data_pedido": data_pedido,
            "status": i["status"],
            "valor_total": valor_total,
            "valor_itens": valor_itens,
            "divergente": divergente
        }
        pedidos_limpos.append(dados_pedido)

        linha = 1
        for item in i["itens"]:
            dados_item = {
                "pedido_id": i["id"],
                "linha": linha,
                "produto_id": item["produto_id"],
                "quantidade": item["quantidade"],
                "preco_unitario": normalizar_valor(item["preco_unitario"])
            }
            itens_limpos.append(dados_item)
            linha += 1

    return pedidos_limpos, itens_limpos, contadores