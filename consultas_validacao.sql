-- Query de validação de vendas totais do mês

SELECT 
    DATE_TRUNC('month', data_pedido) AS mes,
    SUM(valor_total) AS total_mes 
FROM pedidos
GROUP BY mes
ORDER BY mes;

-- Teste de validação -> Se diferença == 0, então as somas das vendas batem
WITH vendas_mes AS (
    SELECT DATE_TRUNC('month', data_pedido) AS mes, SUM(valor_total) AS total_mes 
    FROM pedidos
    GROUP BY mes
),
somas AS (
    SELECT SUM(total_mes) as soma_meses, (select SUM(valor_total) from pedidos) as soma_geral
    FROM vendas_mes
)
SELECT soma_geral, soma_meses, soma_geral-soma_meses as diferenca
FROM somas;

-- Query de validação de pedidos (qntd por estado)
SELECT c.estado, COUNT(*) as total_pedidos
FROM pedidos p
INNER JOIN clientes c
    ON p.cliente_id = c.id
GROUP BY c.estado
ORDER BY total_pedidos desc;

-- Query de validação de pedidos divergentes
SELECT id, status, valor_total, valor_itens, divergente
FROM pedidos
WHERE divergente = true;