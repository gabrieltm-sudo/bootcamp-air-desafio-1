import json
from decimal import Decimal
from etl.transformacao import transf_pedidos
from etl.extracao import (DIR_BRUTOS)
from etl.carga import obter_conexao

def le_arquivo_json():
    caminho_pedidos = DIR_BRUTOS / "pedidos.json"

    with open(caminho_pedidos, "r", encoding="utf-8") as arq:
        pedidos_brutos = json.load(arq)

    pedidos_limpos, _, _ = transf_pedidos(pedidos_brutos)
    return pedidos_limpos
    
def test_rec_cont_pedidos_unicos():
    pedidos_origem = le_arquivo_json()
    cont_origem = len(pedidos_origem)

    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            assert cursor.fetchone()[0] == cont_origem

def test_rec_soma_valor_itens():
    pedidos_origem = le_arquivo_json()
    soma_origem = Decimal("0.00")

    for i in pedidos_origem:
        soma_origem += i["valor_itens"]
    
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT SUM(valor_itens) FROM pedidos")
            soma_dest = cursor.fetchone()[0]

    
    assert soma_dest is not None
    assert abs(soma_origem - soma_dest) <= Decimal("0.01")