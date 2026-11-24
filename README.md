## Idempotência:
Para garantir que execuções repetidas do ETL deixem o banco sempre com as mesmas contagens e sem duplicações, a carga utiliza uma estratégia de limpeza prévia:
- Antes da execução, limpa as quatro tabelas de uma vez com `TRUNCATE TABLE`;
- Insere os dados respeitando a ordem das `Foreign Keys` (`produtos` -> `clientes` -> `pedidos` -> `itens_pedido`);
- Como o bloco roda dentro da transação gerenciada pelo `psycopg` (`with obter_conexao() as conexao:`), qualquer falha durante as inserções dispara o `ROLLBACK` automático (inclusive desfazendo o `TRUNCATE`), mantendo o estado anterior do banco íntegro.