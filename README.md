# Desafio Final -> ETL da Verdejar (Bootcamp AIR - AI-DRIVEN DATA ENGINEERING)

Pipeline ETL em Python para extração de dados de API e CSV, tratamento de "erros" (armadilhas A1 a A6), carga idempotente em PostgreSQL e validação via testes automatizados e consultas SQL.

## Autor
- *Gabriel Torres Machado* - [GitHub](https://github.com/gabrieltm-sudo)

## Decisões Técnicas

* **Banco de dados:** Caminho A - PostgreSQL local.
* **Driver de conexão:** `psycopg` (v3), utilizando consultas parametrizadas e `psycopg.sql` (`sql.SQL` / `sql.Identifier`) para identificadores dinâmicos.
* **Precisão monetária:** uso de `decimal.Decimal` em `transformacao.py` para evitar imprecisões de ponto flutuante (`float`) e manter compatibilidade direta com colunas `NUMERIC` no PostgreSQL.

## Estrutura do Projeto

```text
desafio-1-bootcampAIR/
├── COMO_USEI_IA.md           # Registro de uso de IA, decisões aceitas, rejeitadas e retrabalhos
├── CONTRATO_DE_DADOS.md      # Contrato de dados das tabelas de destino
├── Makefile                  # Atalho para criação do ambiente virtual (.venv) e instalação de dependências
├── README.md                 # Documentação principal e evidências do projeto
├── consultas_validacao.sql   # Consultas SQL de validação e reconciliação
├── pytest.ini                # Configuração de pythonpath = src para execução do pytest na raiz
├── requirements.txt          # Dependências do projeto
└── src/
    ├── main.py               # Integração e execução do pipeline ETL
    ├── brutos/               # Dados brutos extraídos da API (ignorado no .gitignore)
    ├── etl/
    │   ├── extracao.py       # Extração paginada da API e leitura do CSV
    │   ├── transformacao.py  # Tratamento das armadilhas A1 a A6
    │   └── carga.py          # Conexão com PostgreSQL e carga idempotente
    ├── insumos/              # Insumos fornecidos pelo desafio (API local, gerador, schemas e dados/)
    └── tests/
        ├── test_transformacao.py  # Testes unitários das armadilhas A1 a A6
        └── test_reconciliacao.py  # Testes de reconciliação origem x destino
```

## Pré-requisitos e Configuração

1. Python 3.12+ e PostgreSQL instalados e em execução.
2. Crie e ative o ambiente virtual e instale as dependências:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
   Ou, se preferir, use o `Makefile`:
   ```bash
    make venv
    source .venv/bin/activate
   ```
3. Crie um .env na raiz do projeto com as variáveis de ambiente necessárias para conexão com o banco:
    ```env
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=nome_do_banco
    DB_USER=usuario
    DB_PASSWORD=senha
    ```
## Como executar
1. Suba a API localmente:
    ```bash
    cd src/insumos
    python3 api_verdejar.py
    ```
2. Crie as tabelas no PostgreSQL, se não existirem:
    ```bash
    psql -h localhost -U usuario -c "CREATE DATABASE verdejar;"
    psql -h localhost -U usuario -d verdejar -f src/insumos/schema.sql
    ```
3. Execute o ETL (Considerando que está na raiz):
    ```bash
    cd src
    python3 main.py
    ```
4. Execute os testes unitários (Na raiz do projeto, com o ambiente virtual ativo):
    ```bash
    pytest
    ```
5. Execute as consultas de validação:
    ```bash
    psql -h localhost -U usuario -d verdejar -f consultas_validacao.sql
    ```

## Idempotência

Para garantir que execuções repetidas do ETL deixem o banco sempre com as mesmas contagens e sem duplicações, a carga utiliza uma estratégia de limpeza prévia:
- Antes da execução, limpa as quatro tabelas de uma vez com `TRUNCATE TABLE`;
- Insere os dados respeitando a ordem das `Foreign Keys` (`produtos` -> `clientes` -> `pedidos` -> `itens_pedido`);
- Como o bloco roda dentro da transação gerenciada pelo `psycopg` (`with obter_conexao() as conexao:`), qualquer falha durante as inserções dispara o `ROLLBACK` automático (inclusive desfazendo o `TRUNCATE`), mantendo o estado anterior do banco íntegro.

### Evidência de Idempotência
- Primeira execução do ETL:
    ```text
    Extração: Clientes páginas = 5; Registros = 1000
    Extração: Pedidos páginas = 26; Registros brutos = 5100
    Transformação: Pedidos únicos = 5000 Pedidos repetidos e descartados = 100
    Transformação: Emails nulos = 81 Estados padronizados = 151 Datas convertidas = 1037 Valores convertidos = 1255
    Carga: Clientes = 1000 Produtos = 12 Pedidos = 5000 Itens = 12455
    Reconciliação: soma_valor_itens_origem = 311228.75 soma_valor_itens_destino = 311228.75 Diferença = 0.00
    Divergentes: 238 pedidos com valor_total diferente da soma dos itens
    ```
- Segunda execução do ETL:
    ```text
    Extração: Clientes páginas = 5; Registros = 1000
    Extração: Pedidos páginas = 26; Registros brutos = 5100
    Transformação: Pedidos únicos = 5000 Pedidos repetidos e descartados = 100
    Transformação: Emails nulos = 81 Estados padronizados = 151 Datas convertidas = 1037 Valores convertidos = 1255
    Carga: Clientes = 1000 Produtos = 12 Pedidos = 5000 Itens = 12455
    Reconciliação: soma_valor_itens_origem = 311228.75 soma_valor_itens_destino = 311228.75 Diferença = 0.00
    Divergentes: 238 pedidos com valor_total diferente da soma dos itens
    ```
- Comprovação das duas execuções juntas:
    ```text
    (.venv) gabriel@gabriel-Vivobook-Go-E1504FA-E1504FA:~/Downloads/Códigos/desafio-1-bootcampAIR/src$ python3 main.py
    Extração: Clientes páginas = 5; Registros = 1000
    Extração: Pedidos páginas = 26; Registros brutos = 5100
    Transformação: Pedidos únicos = 5000 Pedidos repetidos e descartados = 100
    Transformação: Emails nulos = 81 Estados padronizados = 151 Datas convertidas = 1037 Valores convertidos = 1255
    Carga: Clientes = 1000 Produtos = 12 Pedidos = 5000 Itens = 12455
    Reconciliação: soma_valor_itens_origem = 311228.75 soma_valor_itens_destino = 311228.75 Diferença = 0.00
    Divergentes: 238 pedidos com valor_total diferente da soma dos itens
    (.venv) gabriel@gabriel-Vivobook-Go-E1504FA-E1504FA:~/Downloads/Códigos/desafio-1-bootcampAIR/src$ python3 main.py
    Extração: Clientes páginas = 5; Registros = 1000
    Extração: Pedidos páginas = 26; Registros brutos = 5100
    Transformação: Pedidos únicos = 5000 Pedidos repetidos e descartados = 100
    Transformação: Emails nulos = 81 Estados padronizados = 151 Datas convertidas = 1037 Valores convertidos = 1255
    Carga: Clientes = 1000 Produtos = 12 Pedidos = 5000 Itens = 12455
    Reconciliação: soma_valor_itens_origem = 311228.75 soma_valor_itens_destino = 311228.75 Diferença = 0.00
    Divergentes: 238 pedidos com valor_total diferente da soma dos itens
    ```

## Testes Automatizados
* `pytest` é utilizado para execução dos testes unitários e de reconciliação.
Saída do comando `pytest`:
    ```text
    ========================= 16 passed in 1.43s =========================
    ```

## Consultas SQL de Validação
As consultas SQL de validação estão no arquivo `consultas_validacao.sql`. Elas verificam os três casos definidos no desafio:
- (A) Total de vendas por mês (com teste de consulta para verificar se a soma dos meses bate com o total geral da tabela);
- (B) Quantidade de pedidos por estado;
- (C) Pedidos divergentes.

### Resultados obtidos:
**(A) Total de vendas por mês**

| mes | total_mes |
| --- | ---: |
| 2026-01-01 00:00:00-03 | 30449.02 |
| 2026-02-01 00:00:00-03 | 33923.86 |
| 2026-03-01 00:00:00-03 | 30678.70 |
| 2026-04-01 00:00:00-03 | 31253.96 |
| 2026-05-01 00:00:00-03 | 30890.02 |
| 2026-06-01 00:00:00-03 | 31627.73 |
| 2026-07-01 00:00:00-03 | 32796.17 |
| 2026-08-01 00:00:00-03 | 29328.04 |
| 2026-09-01 00:00:00-03 | 29995.71 |
| 2026-10-01 00:00:00-03 | 31104.54 |

*Agrupamento em 10 meses (janeiro a outubro de 2026), confirmando a conversão uniforme das datas (armadilha A3).*

**(A.1) Teste de reconciliação (soma dos meses vs. soma geral da tabela)**

| soma_geral | soma_meses | diferenca |
| ---: | ---: | ---: |
| 312047.75 | 312047.75 | 0.00 |

*A diferença zerada (`0.00`) confirma que o agrupamento mensal não perdeu nem duplicou valores em relação ao total da tabela `pedidos`.*

**(B) Quantidade de pedidos por estado**

| estado | total_pedidos |
| --- | ---: |
| RS | 1543 |
| SC | 1127 |
| PR | 974 |
| SP | 880 |
| MG | 476 |

*A soma dos 5 estados fecha em exatamente 5.000 pedidos únicos e todas as siglas aparecem padronizadas em maiúsculas, comprovando a integridade do `JOIN` e a normalização de estados (armadilha A2).*

**(C) Pedidos divergentes**

Total encontrado: **238 pedidos** (amostra das 5 primeiras linhas retornadas):

| id | status | valor_total | valor_itens | divergente |
| ---: | --- | ---: | ---: | :---: |
| 1 | entregue | 125.84 | 130.84 | t |
| 51 | cancelado | 26.58 | 23.58 | t |
| 71 | cancelado | 144.35 | 134.35 | t |
| 81 | entregue | -1.84 | 3.16 | t |
| 106 | em_transporte | 47.78 | 44.78 | t |

*Todos os 238 pedidos com diferença superior a `0.01` entre `valor_total` e `valor_itens` foram preservados e sinalizados com `divergente = TRUE`.*