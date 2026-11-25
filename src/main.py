from decimal import Decimal
import sys
import psycopg
import requests
from etl.extracao import (
    CAMINHO_PRODUTOS_CSV,
    DIR_BRUTOS,
    extrair_rota,
    ler_produtos_csv,
    salvar_json,
)
from etl.transformacao import transf_clientes, transf_pedidos
from etl.carga import carregar_dados, obter_soma_valor_itens


def main():
    # Parte 1 - Extração
    try:
        clientes_brutos, pag_clientes = extrair_rota("clientes")
        pedidos_brutos, pag_pedidos = extrair_rota("pedidos")
    except requests.exceptions.RequestException:
        sys.exit(1)

    produtos_brutos = ler_produtos_csv(CAMINHO_PRODUTOS_CSV)

    if not clientes_brutos or not pedidos_brutos or not produtos_brutos:
        print("ERRO: Extração incompleta; Verifique a API e o arquivo produtos.csv")
        sys.exit(1)

    salvou_clientes = salvar_json(clientes_brutos, DIR_BRUTOS / "clientes.json")
    salvou_pedidos = salvar_json(pedidos_brutos, DIR_BRUTOS / "pedidos.json")
    if not salvou_clientes or not salvou_pedidos:
        print("ERRO: Falha ao salvar os arquivos brutos em disco")
        sys.exit(1)

    print(f"Extração: Clientes páginas = {pag_clientes}; Registros = {len(clientes_brutos)}")
    print(f"Extração: Pedidos páginas = {pag_pedidos}; Registros brutos = {len(pedidos_brutos)}")

    # Parte 2 - Transformação
    clientes_limpos, cont_clientes = transf_clientes(clientes_brutos)
    pedidos_limpos, itens_limpos, cont_pedidos = transf_pedidos(pedidos_brutos)

    soma_origem = Decimal("0.00")
    for pedido in pedidos_limpos:
        soma_origem += pedido["valor_itens"]

    print(
        f"Transformação: Pedidos únicos = {len(pedidos_limpos)} "
        f"Pedidos repetidos e descartados = {cont_pedidos['duplicados']}"
    )
    print(
        f"Transformação: Emails nulos = {cont_clientes['emails_nulos']} "
        f"Estados padronizados = {cont_clientes['estados_corrigidos']} "
        f"Datas convertidas = {cont_pedidos['datas_convertidas']} "
        f"Valores convertidos = {cont_pedidos['valores_convertidos']}"
    )

    # Parte 3 - Carga no banco e reconciliação
    try:
        contagens_banco = carregar_dados(
            produtos_brutos,
            clientes_limpos,
            pedidos_limpos,
            itens_limpos,
        )
        soma_destino = obter_soma_valor_itens() or Decimal("0.00")
    except (psycopg.Error, ValueError) as erro:
        print(f"ERRO: Falha na carga no PostgreSQL: {erro}")
        sys.exit(1)

    diferenca = abs(soma_origem - soma_destino)


    print(
        f"Carga: Clientes = {contagens_banco['clientes']} "
        f"Produtos = {contagens_banco['produtos']} "
        f"Pedidos = {contagens_banco['pedidos']} "
        f"Itens = {contagens_banco['itens_pedido']}"
    )
    print(
        f"Reconciliação: soma_valor_itens_origem = {soma_origem:.2f} "
        f"soma_valor_itens_destino = {soma_destino:.2f} "
        f"Diferença = {diferenca:.2f}"
    )
    print(
        f"Divergentes: {cont_pedidos['divergentes']} pedidos com valor_total diferente da soma dos itens"
    )


if __name__ == "__main__":
    main()