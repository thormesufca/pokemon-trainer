from src.grafo import vizinhos


def _tipo_local(v, locais):
    if v == locais.get('LAB'):
        return 'LAB'
    if v == locais.get('ESTADIO'):
        return 'ESTADIO'
    if v in locais.get('PMC', []):
        return 'PMC'
    if v in locais.get('GINASIO', []):
        return 'GINASIO'
    return ''


def exibir_mapa(grafo, locais, treinador):
    print("\n=== MAPA ===")
    for v in sorted(grafo):
        tipo = _tipo_local(v, locais)
        marca = " ← você" if v == treinador.posicao else ""
        label = f"[{v}] {tipo}" if tipo else f"[{v}]"
        vizs = "  ".join(f"→ {viz} ({w})" for viz, w in vizinhos(grafo, v))
        print(f"  {label}{marca}")
        print(f"      {vizs}")
    print()


def exibir_estado(grafo, treinador, relogio, locais):
    tipo = _tipo_local(treinador.posicao, locais)
    label = f"[{treinador.posicao}]" + (f" {tipo}" if tipo else "")
    time_str = "  ".join(
        f"{p.nome} HP:{p.hp}" + ("" if p.consciente else " (incon.)")
        for p in treinador.time
    ) or "(sem Pokémon)"
    print(f"\n--- {label} | Tempo: {relogio.tempo_atual()} / {relogio.prazo()} ---")
    vizs = "  ".join(f"{viz} ({w})" for viz, w in vizinhos(grafo, treinador.posicao))
    print(f"Vizinhos: {vizs}")
    print(f"Time: {time_str}")


def _exibir_status(treinador):
    print(f"\n=== STATUS — {treinador.nome} ===")
    print(f"XP: {treinador.xp} | Insígnias: {len(treinador.insignias)}")
    if treinador.time:
        for p in treinador.time:
            print(f"  {p}  {'[incon.]' if not p.consciente else ''}")
    else:
        print("  (sem Pokémon)")
    if treinador.ovos:
        for ovo, dist in treinador.ovos.items():
            print(f"  Ovo {ovo.nome}: {dist} unidades até eclodir")
    print()


def loop_comandos(grafo, locais, treinador, relogio):
    print(f"\nBem-vindo, {treinador.nome}! Você está no laboratório.")
    print("Comandos: ir <v>  |  mapa  |  status  |  sair\n")
    exibir_estado(grafo, treinador, relogio, locais)

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            break

        if not cmd:
            continue

        if cmd == "sair":
            print("Até a próxima!")
            break

        elif cmd == "mapa":
            exibir_mapa(grafo, locais, treinador)

        elif cmd == "status":
            _exibir_status(treinador)

        elif cmd.startswith("ir "):
            partes = cmd.split()
            if len(partes) != 2 or not partes[1].isdigit():
                print("Uso: ir <número do vértice>")
                continue
            destino = int(partes[1])
            adj = dict(vizinhos(grafo, treinador.posicao))
            if destino not in adj:
                vizs = ", ".join(str(v) for v in sorted(adj))
                print(f"Vértice {destino} não é vizinho. Vizinhos: {vizs}")
                continue
            w = adj[destino]
            treinador.mover(destino, w, relogio)
            exibir_estado(grafo, treinador, relogio, locais)

            if relogio.acabou():
                print("Tempo esgotado! A Liga fechou as portas.")
                break
            if treinador.classificado:
                print("Você coletou 8 insígnias — rumo ao Estádio!")
                break

        else:
            print("Comando desconhecido. Tente: ir <v>  |  mapa  |  status  |  sair")
