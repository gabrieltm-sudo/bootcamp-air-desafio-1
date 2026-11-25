from decimal import Decimal
from datetime import date as Date
from etl.transformacao import (tratar_email, normalizar_estado, converter_data, normalizar_valor, deduplicar_pedidos, calcular_valor_itens, eh_divergente)

"""
Testes para as funções de transformação
"""
def test_email_nulo_retorna_none(): # A1
    assert tratar_email(None) is None

def test_email_informado_retorna_mesmo_email(): # A1
    email = "teste@exemplo.com"
    assert tratar_email(email) == email

def test_estado_minusculo_retorna_maiusculo(): # A2
    assert normalizar_estado("rs") == "RS"

def test_estado_nao_minusculo_retorna_maiusculo(): # A2
    assert normalizar_estado("Rs") == "RS"

def test_data_dd_mm_aaaa_retorna_objeto_date(): # A3
    data = "31/08/2005"
    assert converter_data(data) == Date(2005, 8, 31)

def test_data_aaaa_mm_dd_retorna_objeto_date(): # A3
    data = "2005-08-31"
    assert converter_data(data) == Date(2005, 8, 31)

def test_valor_com_virgula_vira_numero(): # A4
    assert normalizar_valor("1,34") == Decimal("1.34")

def test_valor_numerico_permanece(): # A4
    valor = 93.32
    assert normalizar_valor(valor) == Decimal("93.32")

def test_deduplicacao_pedidos():  # A5
    pedidos_entrada = [
        {
            "id": 1,
            "cliente_id": 101,
            "data_pedido": "2023-01-01",
            "status": "entregue",
            "valor_total": 100.00,
            "itens": [
                {"produto_id": 201, "quantidade": 2, "preco_unitario": 50.00}
            ],
        },
        {
            "id": 1,
            "cliente_id": 101,
            "data_pedido": "2023-01-01",
            "status": "cancelado",
            "valor_total": 100.00,
            "itens": [
                {"produto_id": 201, "quantidade": 2, "preco_unitario": 50.00}
            ],
        },
        {
            "id": 2,
            "cliente_id": 102,
            "data_pedido": "2023-01-02",
            "status": "entregue",
            "valor_total": 50.00,
            "itens": [
                {"produto_id": 201, "quantidade": 1, "preco_unitario": 50.00}
            ],
        },
    ]

    pedidos_esperados = [
        pedidos_entrada[0],
        pedidos_entrada[2],
    ]

    pedidos_unicos, total_duplicados = deduplicar_pedidos(pedidos_entrada)

    assert pedidos_unicos == pedidos_esperados
    assert total_duplicados == 1

def test_deduplicacao_sem_duplicados(): # A5
    pedidos_entrada = [
        {
            "id": 1,
            "cliente_id": 101,
            "data_pedido": "2023-01-01",
            "status": "cancelado",
            "valor_total": 100.00,
            "itens": [
                {"produto_id": 201, "quantidade": 2, "preco_unitario": 50.00}
            ],
        },
        {
            "id": 2,
            "cliente_id": 102,
            "data_pedido": "2023-01-02",
            "status": "entregue",
            "valor_total": 50.00,
            "itens": [
                {"produto_id": 201, "quantidade": 1, "preco_unitario": 50.00}
            ],
        }
    ]

    pedidos_esperados = pedidos_entrada.copy()

    pedidos_unicos, total_duplicados = deduplicar_pedidos(pedidos_entrada)

    assert pedidos_unicos == pedidos_esperados
    assert total_duplicados == 0

def test_calcular_valor_itens():  # A6
    itens = [
        {"produto_id": 201, "quantidade": 2, "preco_unitario": 50.00},
        {"produto_id": 202, "quantidade": 3, "preco_unitario": 10.50},
    ]
    assert calcular_valor_itens(itens) == Decimal("131.50")


def test_valor_total_pedidos_divergente():  # A6
    assert eh_divergente(Decimal("100.00"), Decimal("100.02")) is True


def test_valor_total_pedidos_dentro_da_tolerancia():  # A6
    assert eh_divergente(Decimal("100.00"), Decimal("100.01")) is False


def test_valor_total_pedidos_igual():  # A6
    assert eh_divergente(Decimal("100.00"), Decimal("100.00")) is False