from types import SimpleNamespace
from src.ui.exibicao import exibir_estado, comandos_disponiveis
from src.ui.comandos import COMANDOS_SEM_ARGUMENTO, COMANDOS_COM_ARGUMENTO


def loop_comandos(grafo, locais, treinador, relogio, dist, prox, mundo):
    ctx = SimpleNamespace(
        grafo=grafo, locais=locais, treinador=treinador, relogio=relogio,
        dist=dist, prox=prox, mundo=mundo,
    )

    print(f"\nBem-vindo, {treinador.nome}! Você está no laboratório.")
    exibir_estado(grafo, treinador, relogio, locais, mundo)

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            break

        if not cmd:
            continue

        if cmd in COMANDOS_SEM_ARGUMENTO:
            deve_parar = COMANDOS_SEM_ARGUMENTO[cmd](ctx)
        else:
            prefixo = next((p for p in COMANDOS_COM_ARGUMENTO if cmd.startswith(p)), None)
            if prefixo is not None:
                deve_parar = COMANDOS_COM_ARGUMENTO[prefixo](ctx, cmd.split())
            else:
                print("Comando desconhecido. Tente: " + "  |  ".join(comandos_disponiveis(locais, treinador, mundo)))
                deve_parar = False

        if deve_parar:
            break
