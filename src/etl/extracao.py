import requests


def extrair_rota(rota, page_size=200):
    rota_limpa = rota.lstrip("/")
    pagina = 1
    total_pages = 1
    paginas_lidas = 0
    registros = []

    while pagina <= total_pages:
        try:
            resposta = requests.get(
                f"http://127.0.0.1:8000/{rota_limpa}",
                params={"page": pagina, "page_size": page_size},
                timeout=5,
            )
        except requests.exceptions.ConnectionError:
            print(f"[ ERRO ] Não foi possível conectar à API na rota /{rota_limpa}")
            break
        except requests.exceptions.Timeout:
            print(f"[ ERRO ] Tempo limite excedido na rota /{rota_limpa}, pagina {pagina}")
            break
        except requests.exceptions.RequestException as erro:
            print(f"[ ERRO ] Falha na requisição da rota /{rota_limpa}: {erro}")
            break

        match resposta.status_code:
            case 200:
                try:
                    dados = resposta.json()
                except requests.exceptions.JSONDecodeError:
                    print(f"[ ERRO ] Resposta inválida na rota /{rota_limpa}, pagina {pagina}")
                    break

                registros.extend(dados.get("items", []))
                total_pages = dados.get("total_pages", total_pages)
                paginas_lidas+=1
                pagina+=1
            case 404:
                print(f"[ ERRO ] Rota ou página inexistente (/{rota_limpa}, pagina {pagina})")
                break
            case _:
                print(f"[ ERRO ] Status HTTP inesperado {resposta.status_code} na rota /{rota_limpa}")
                break

    return registros, paginas_lidas