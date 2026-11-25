# Como Usei IA neste Desafio

## Contexto e Papéis Adotados

* **Modelo de IA:** Google Gemini 4
* **Documentação (`README.md` e `CONTRATO_DE_DADOS.md`):** usei a IA como tutora, pedindo explicações conceituais, sugestões de boas práticas e revisão de sintaxe/ortografia, mas escrevendo o conteúdo por conta própria.
* **Pipeline ETL (`src/etl/`, `src/main.py` e `src/tests/`):** usei a IA como par com escopo limitado (assim como foi definido), pedindo revisões pontuais, explicações de boas práticas e ajuda para depurar erros específicos, mantendo a escrita e a validação sob meu controle.
* **Consultas SQL (`consultas_validacao.sql`):** usei a IA como tutora, escrevendo as queries por conta própria e pedindo apenas apontamento de erros de sintaxe/lógica e explicações conceituais (como para relembrar conceitos de CTEs e `INNER JOIN`), sem solicitar consultas prontas.

---

## Sugestões Aceitas

### 1. Uso de `decimal.Decimal` para valores monetários (`transformacao.py`)
* **O que foi sugerido:** substituir `float` por `decimal.Decimal` em `normalizar_valor` e `calcular_valor_itens`.
* **Por que aceitei:** pesquisei na internet e descobri que `decimal.Decimal` evita erros de arredondamento de ponto flutuante em somas financeiras e mantém compatibilidade direta com colunas `NUMERIC` do PostgreSQL e que é uma boa prática quando estiver lidando com valores financeiros.
* **Como validei:** rodei os testes unitários das armadilhas A4 e A6 em `test_transformacao.py` e validei a soma total de `valor_itens` no banco via `test_reconciliacao.py` (diferença dentro da tolerância de 0.01 (1 centavo)).

### 2. Refatoração do teste da armadilha A5 (`test_deduplicacao_pedidos`)
* **O que foi sugerido:** desempacotar o retorno `(pedidos_unicos, total_duplicados)` antes dos `assert`, adicionar um pedido com `id: 2` e diferenciar o `status` na duplicata de `id: 1`.
* **Por que aceitei:** `assert deduplicar_pedidos(...) == pedidos_transformados, 1` falhava porque a vírgula no `assert` em Python define a mensagem de erro, não uma tupla. Além disso, incluir um segundo ID e alterar o status da duplicata serve para comprovar que a função mantém a primeira ocorrência sem descartar registros únicos.
* **Como validei:** execução do `pytest` confirmando todos os 14 testes unitários (de `test_transformacao.py`) passando.

### 3. Transação única e consultas parametrizadas em `carga.py`
* **O que foi sugerido:** encapsular `TRUNCATE TABLE` e as inserções dentro do mesmo bloco transacional do `psycopg` (`with obter_conexao() as conexao:`), usando parâmetros e `psycopg.sql` (`sql.SQL`/`sql.Identifier`) para evitar SQL injection.
* **Por que aceitei:** garante atomicidade (em caso de erro no meio da carga, o `ROLLBACK` desfaz inclusive o `TRUNCATE`) e segue boas práticas de segurança na construção de queries.
* **Como validei:** executei o pipeline mais de uma vez seguida e confirmei que as contagens no PostgreSQL permaneceram idênticas (5.000 pedidos únicos) sem duplicação.

---

## Sugestões Rejeitadas ou Adaptadas

### 1. Rascunho inicial sugerido para `main.py`
* **O que foi sugerido:** uma estrutura inicial de integração que não refletia a organização real das minhas funções de extração, transformação e carga.
* **Por que rejeitei:** havia assinatura de funções e fluxos de pastas não condizentes com o projeto (talvez por alucinação), então preferi estruturar o `main.py` diretamente a partir dos módulos que já estavam prontos.
* **Como validei**: após estruturar o `main.py` conectado às minhas funções, executei o pipeline completo com a API local e o PostgreSQL ativos e conferi os totais carregados no banco.


### 2. Troca de `executemany` por laços `for` em `carga.py`
* **O que foi sugerido:** uso de `executemany` para inserção em lote nas tabelas do PostgreSQL.
* **Por que adaptei:** optei por usar laços `for` explícitos para manter o fluxo de inserção mais legível (para mim) e fácil de depurar no volume atual de dados (uma vez que o volume é relativamente pequeno), priorizando clareza no código que eu precisava dominar.
* **Como validei:** executei o pipeline duas vezes seguidas e rodei `pytest` para confirmar a carga completa e sem duplicação.

### 3. Adaptação do `test_reconciliacao.py`
* **O que foi sugerido:** calcular a soma de origem em uma única linha com `sum((p["valor_itens"] for p in pedidos_origem), Decimal("0.00"))`.
* **Por que adaptei:** reescrevi a soma com um laço `for` tradicional e nomeei a função auxiliar como `le_arquivo_json()` para manter o teste legível e alinhado ao meu padrão de escrita.
* **Como validei:** rodei `pytest` na raiz do projeto, confirmando que a soma calculada pelo laço de repetição bate com o `SUM(valor_itens)` do banco dentro da tolerância de 0.01.

### 4. Tratamento de falhas no `main.py`
- **O que foi sugerido:** na revisão final do `main.py` com o assistente (para ajustar a saída acessível e evitar carga parcial), foi sugerido encerrar os blocos de erro com um `return` simples.
- **Por que adaptei:** mantive a validação da extração e o formato de saída acessível, mas substituí os `return` nos caminhos de erro por `sys.exit(1)`. Um `return` simples faz o script Python encerrar com código de saída `0` (sucesso), o que mascararia falhas para o terminal ou automações como o `Makefile`. Com `sys.exit(1)`, o processo sinaliza erro explicitamente ao sistema operacional.
- **Como validei:** executei `python src/main.py` duas vezes seguidas com a API e o banco ativos (confirmando execução normal e contagens idênticas) e rodei `pytest` para garantir que todos os 16 testes continuam passando.

---

## Falhas, Erros e Retrabalhos

### 1. Cópia prematura em `carga.py` e revisão forçada de entendimento
* **O que aconteceu:** em um primeiro momento, apliquei o código sugerido para `carga.py` antes de dominar todos os detalhes de transação, `rollback` automático do `psycopg` e uso de `sql.Identifier`.
* **Como corrigi:** parei o avanço do projeto para revisar o módulo linha por linha e responder perguntas técnicas sobre o funcionamento de cada bloco, garantindo entendimento real do código antes de seguir para os testes.

### 2. Erros sucessivos no `test_reconciliacao.py`
* **O que aconteceu:** inicialmente comparei `COUNT(*)` do banco com o número fixo `5000` (o que não validava contra a origem). Ao reescrever para ler `brutos/pedidos.json` e somar `valor_itens` em um laço `for`, escrevi `soma_origem += i["valor_itens"], Decimal("0.00")`, criando acidentalmente uma tupla e gerando `TypeError`.
* **Como corrigi:** inicializei `soma_origem = Decimal("0.00")` antes do laço e somei apenas `i["valor_itens"]`. Validei rodando `pytest` até todos os 16 testes passarem.

### 3. Sintaxe de CTEs encadeadas em `consultas_validacao.sql`
* **O que aconteceu:** ao montar o teste de reconciliação da soma mensal contra o total geral da tabela, errei a sintaxe de CTEs (repetindo `WITH`, fechando a primeira CTE com `;`, deixando um parêntese aberto em `SUM(valor_total)` e mantendo linhas em branco que o SQL Script do DBeaver interpretou como separador de instruções).
* **Como corrigi:** corrigi cada erro iterativamente com orientação em modo tutor e validei executando o arquivo completo via `psql -h localhost -U postgres -d verdejar -f consultas_validacao.sql`, obtendo `diferenca = 0.00`.