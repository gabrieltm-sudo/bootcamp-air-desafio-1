# CONTRATO DE DADOS - VERDEJAR


### Tabela `clientes`
- **Origem:** API `GET /clientes` (JSON bruto em `src/brutos/clientes.json`)
- **Chave primária:** `id`

| Coluna | Tipo | Nulo? | Regra / Restrição |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Não | Chave primária (`PRIMARY KEY`) |
| `nome` | `TEXT` | Não | Nome completo do cliente |
| `email` | `TEXT` | Sim | Aceitar `NULL` e contabilizar no ETL |
| `cidade` | `TEXT` | Não | Cidade de cadastro |
| `estado` | `CHAR(2)` | Não | Normalizar para 2 letras maiúsculas (ex.: `mg` -> `MG`) |
| `cadastro_em` | `DATE` | Não | Data no formato ISO `AAAA-MM-DD` |

### Tabela `pedidos`
- **Origem:** API `GET /pedidos` (JSON bruto em `src/brutos/pedidos.json`)
- **Chave primária:** `id`
- **Chave estrangeira:** `cliente_id`

| Coluna | Tipo | Nulo? | Regra / Restrição |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Não | Chave primária (`PRIMARY KEY`); deduplicar pedidos repetidos mantendo uma ocorrência por `id` |
| `cliente_id` | `INTEGER` | Não | Chave estrangeira (`FOREIGN KEY`) referenciando a coluna id da tabela `clientes` |
| `data_pedido` | `DATE` | Não | Converter datas no formato `DD/MM/AAAA` ou `AAAA-MM-DD` (ex.: `06/06/2026` ou `2026-06-06`) para o tipo DATE |
| `status` | `TEXT` | Não | Status do pedido |
| `valor_total` | `NUMERIC(12, 2)` | Não | Valor total do pedido - Chega como número ou texto com vírgula (ex.: `"125,84"`); normalizar para número com duas casas decimais |
| `valor_itens` | `NUMERIC(12, 2)` | Não | Valor total de itens do pedido - Calculado no ETL pela soma de `quantidade * preco_unitario` dos itens; pode divergir do `valor_total` |
| `divergente` | `BOOLEAN` | Não | Padrão `FALSE` (`DEFAULT FALSE`); indica se houve divergência entre `valor_total` e `valor_itens` (`true` se diferentes, `false` caso contrário) |

### Tabela `itens_pedido`
- **Origem:** API `GET /pedidos` (JSON bruto em `src/brutos/pedidos.json`)
- **Chave primária:** `pedido_id` e `linha`
- **Chave estrangeira:** `pedido_id` e `produto_id`

| Coluna | Tipo | Nulo? | Regra / Restrição |
| :--- | :--- | :--- | :--- |
| `pedido_id` | `INTEGER` | Não | Chave primária (`PRIMARY KEY`) e chave estrangeira (`FOREIGN KEY`) referenciando a coluna id da tabela `pedidos` |
| `linha` | `INTEGER` | Não | Chave primária (`PRIMARY KEY`); número sequencial gerado pelo ETL para cada item dentro da lista `itens` do pedido |
| `produto_id` | `INTEGER` | Não | Chave estrangeira (`FOREIGN KEY`) referenciando a coluna produto_id da tabela `produtos` |
| `quantidade` | `INTEGER` | Não | Quantidade do produto |
| `preco_unitario` | `NUMERIC(10, 2)` | Não | Preço de uma unidade do produto - Número de até 10 dígitos com 2 casas decimais |

### Tabela `produtos`
- **Origem:** CSV `src/insumos/dados/produtos.csv`
- **Chave primária:** `produto_id`

| Coluna | Tipo | Nulo? | Regra / Restrição |
| :--- | :--- | :--- | :--- |
| `produto_id` | `INTEGER` | Não | Chave primária (`PRIMARY KEY`) |
| `nome` | `TEXT` | Não | Nome do produto |
| `categoria` | `TEXT` | Não | Categoria do produto |
| `preco_base` | `NUMERIC(10, 2)` | Não | Preço base do produto - Número de até 10 dígitos com 2 casas decimais |