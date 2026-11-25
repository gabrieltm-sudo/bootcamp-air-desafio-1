import os
import psycopg
from psycopg import sql
from dotenv import load_dotenv

load_dotenv()


def obter_conexao():
    """Abre conexão com o PostgreSQL usando variáveis de ambiente."""
    variaveis = {
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": os.getenv("DB_PORT", "5432"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
    }

    faltando = [nome for nome, valor in variaveis.items() if not valor]
    if faltando:
        raise ValueError(
            f"Variáveis de ambiente obrigatórias não configuradas no .env: {', '.join(faltando)}"
        )
    
    return psycopg.connect(
        host=variaveis["DB_HOST"],
        port=variaveis["DB_PORT"],
        dbname=variaveis["DB_NAME"],
        user=variaveis["DB_USER"],
        password=variaveis["DB_PASSWORD"],
    )


def obter_soma_valor_itens():
    """Retorna a soma de valor_itens carregada na tabela pedidos."""
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT SUM(valor_itens) FROM pedidos")
            resultado = cursor.fetchone()[0]
    return resultado


def carregar_dados(produtos, clientes, pedidos, itens):
    sql_produtos = """
        INSERT INTO produtos (produto_id, nome, categoria, preco_base)
        VALUES (%(produto_id)s, %(nome)s, %(categoria)s, %(preco_base)s)
    """

    sql_clientes = """
        INSERT INTO clientes (id, nome, email, cidade, estado, cadastro_em)
        VALUES (%(id)s, %(nome)s, %(email)s, %(cidade)s, %(estado)s, %(cadastro_em)s)
    """

    sql_pedidos = """
        INSERT INTO pedidos (id, cliente_id, data_pedido, status, valor_total, valor_itens, divergente)
        VALUES (%(id)s, %(cliente_id)s, %(data_pedido)s, %(status)s, %(valor_total)s, %(valor_itens)s, %(divergente)s)
    """

    sql_itens = """
        INSERT INTO itens_pedido (pedido_id, linha, produto_id, quantidade, preco_unitario)
        VALUES (%(pedido_id)s, %(linha)s, %(produto_id)s, %(quantidade)s, %(preco_unitario)s)
    """

    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE itens_pedido, pedidos, clientes, produtos;")

            for produto in produtos:
                cursor.execute(sql_produtos, produto)
            
            for cliente in clientes:
                cursor.execute(sql_clientes, cliente)
            
            for pedido in pedidos:
                cursor.execute(sql_pedidos, pedido)
            
            for item in itens:
                cursor.execute(sql_itens, item)

            contagens = {}

            for tabela in ("produtos", "clientes", "pedidos", "itens_pedido"):
                query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(tabela))
                cursor.execute(query)
                contagens[tabela] = cursor.fetchone()[0]

    return contagens