from etl.extracao import (
    CAMINHO_PRODUTOS_CSV,
    DIR_BRUTOS,
    extrair_rota,
    ler_produtos_csv,
    salvar_json,
)
from etl.transformacao import transf_clientes, transf_pedidos


def main():
    clientes_brutos, pag_clientes = extrair_rota("clientes")
    pedidos_brutos, pag_pedidos = extrair_rota("pedidos")
    produtos_brutos = ler_produtos_csv(CAMINHO_PRODUTOS_CSV)

    if not clientes_brutos or not pedidos_brutos:
        print("[ ERRO ] Extração incompleta. Verifique se a API está rodando.")
        return

    salvar_json(clientes_brutos, DIR_BRUTOS / "clientes.json")
    salvar_json(pedidos_brutos, DIR_BRUTOS / "pedidos.json")

    print("=== Resumo da Extração ===")
    print(f"Clientes extraídos: {len(clientes_brutos)} ({pag_clientes} páginas)")
    print(f"Pedidos extraídos: {len(pedidos_brutos)} ({pag_pedidos} páginas)")
    print(f"Produtos lidos do CSV: {len(produtos_brutos)}")

    clientes_limpos, cont_clientes = transf_clientes(clientes_brutos)
    pedidos_limpos, itens_limpos, cont_pedidos = transf_pedidos(pedidos_brutos)

    print("\n=== Resumo da Transformação ===")
    print(f"E-mails nulos: {cont_clientes['emails_nulos']}")
    print(f"Estados corrigidos: {cont_clientes['estados_corrigidos']}")
    print(f"Datas convertidas (DD/MM/AAAA): {cont_pedidos['datas_convertidas']}")
    print(f"Valores convertidos (texto -> número): {cont_pedidos['valores_convertidos']}")
    print(f"Pedidos repetidos descartados: {cont_pedidos['duplicados']}")
    print(f"Pedidos divergentes: {cont_pedidos['divergentes']}")
    print("===============================")
    print(
        f"Prontos para carga -> "
        f"Clientes: {len(clientes_limpos)} | "
        f"Produtos: {len(produtos_brutos)} | "
        f"Pedidos: {len(pedidos_limpos)} | "
        f"Itens: {len(itens_limpos)}"
    )

if __name__ == "__main__":
    main()