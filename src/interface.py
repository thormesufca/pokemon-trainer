from src.grafo import vizinhos, mais_proximo
from src.entidades import Pokemon, Treinador, vertices_proibidos_para_npc


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


COMANDOS_FIXOS = ["ir <v>", "mapa", "status", "interesse", "sair"]


def _comandos_contextuais(locais, treinador: Treinador, mundo):
    """Comandos extras que só fazem sentido no vértice atual do treinador."""
    extras = []
    if treinador.posicao in mundo.vertices_com("item"):
        extras.append("pegar")
    if treinador.posicao in locais.get("PMC", []):
        if any(p.muito_machucado for p in treinador.time):
            extras.append("deixar <índice>")
        if any(e["notificado"] and e["vertice"] == treinador.posicao for e in treinador.pmc_pendentes):
            extras.append("retirar")
    return extras


def _comandos_disponiveis(locais, treinador: Treinador, mundo):
    return COMANDOS_FIXOS + _comandos_contextuais(locais, treinador, mundo)


def _exibir_comandos(locais, treinador: Treinador, mundo):
    print("Comandos: " + "  |  ".join(_comandos_disponiveis(locais, treinador, mundo)))


def exibir_mapa(grafo, locais, treinador):
    origem = treinador.posicao
    tipo = _tipo_local(origem, locais)
    label = f"[{origem}] {tipo}" if tipo else f"[{origem}]"
    print(f"\n=== VIZINHANÇA DE {label} ===")
    for viz, w in vizinhos(grafo, origem):
        tipo_viz = _tipo_local(viz, locais)
        rotulo_viz = f"[{viz}] {tipo_viz}" if tipo_viz else f"[{viz}]"
        print(f"  → {rotulo_viz} (custo {w})")
    print()


def _descrever_local(mundo, treinador: Treinador):
    itens = mundo.itens.get(treinador.posicao, [])
    selvagens = mundo.pokemons_selvagens.get(treinador.posicao, [])
    npcs_aqui = [t for t in mundo.treinadores_npc if t.posicao == treinador.posicao]
    lideres_aqui = [l for l in mundo.lideres_ginasio.values() if l.posicao == treinador.posicao]
    partes = []
    if itens:
        partes.append("Itens: " + ", ".join(itens))
    if selvagens:
        partes.append("Pokémon selvagem: " + ", ".join(p.nome for p in selvagens))
    if npcs_aqui:
        partes.append("Treinador: " + ", ".join(t.nome for t in npcs_aqui))
    if lideres_aqui:
        partes.append("Líder de Ginásio: " + ", ".join(
            f"{l.nome} (ginásio {l.ginasio})" for l in lideres_aqui
        ))
    print("Aqui: " + (" | ".join(partes) if partes else "nada de especial"))


def exibir_estado(grafo, treinador, relogio, locais, mundo):
    tipo = _tipo_local(treinador.posicao, locais)
    label = f"[{treinador.posicao}]" + (f" {tipo}" if tipo else "")
    time_str = "  ".join(
        f"{p.nome} HP:{p.hp}" + ("" if p.consciente else " (incon.)")
        for p in treinador.time
    ) or "(sem Pokémon)"
    print(f"\n--- {label} | Tempo: {relogio.tempo_atual()} / {relogio.prazo()} ---")
    _descrever_local(mundo, treinador)
    vizs = "  ".join(f"{viz} ({w})" for viz, w in vizinhos(grafo, treinador.posicao))
    print(f"Vizinhos: {vizs}")
    print(f"Time: {time_str}")
    _exibir_comandos(locais, treinador, mundo)


def _exibir_status(treinador: Treinador):
    print(f"\n=== STATUS — {treinador.nome} ===")
    print(f"XP: {treinador.xp} | Insígnias: {len(treinador.insignias)}")
    if treinador.time:
        for i, p in enumerate(treinador.time):
            print(f"  [{i}] {p}  {'[incon.]' if not p.consciente else ''}")
    else:
        print("  (sem Pokémon)")
    if treinador.pmc_pendentes:
        for entrada in treinador.pmc_pendentes:
            if entrada["notificado"]:
                estado = "pronto para retirada"
            else:
                estado = f"{entrada['restante']}/{entrada['total']} unidades restantes"
            print(f"  Em tratamento no PMC [{entrada['vertice']}]: {entrada['pokemon'].nome} ({estado})")
    if treinador.ovos:
        for ovo, dist in treinador.ovos.items():
            print(f"  Ovo {ovo.nome}: {dist} unidades até eclodir")
    itens_disponiveis = {tipo: qtd for tipo, qtd in treinador.itens.items() if qtd > 0}
    if itens_disponiveis:
        for tipo, qtd in itens_disponiveis.items():
            print(f"  Item: {tipo} x {qtd}")
    else:
        print("  (sem itens)")

    print()

def _adicionar_pokemon_escolha(treinador: Treinador, pokemon: Pokemon):
    if not treinador.time_cheio:
        treinador.adicionar_pokemon(pokemon)
        return

    candidatos = treinador.time + [pokemon]
    print("Time cheio! Escolha quem enviar para o laboratório:")
    for i, p in enumerate(candidatos):
        marca = " (recém capturado)" if p is pokemon else ""
        print(f"[{i}] - {p.nome} ({p.hp} HP){marca}")

    while True:
        escolha = input("> ").strip()
        if escolha.isdigit() and 0 <= int(escolha) < len(candidatos):
            break
        print("Escolha inválida")

    treinador.gerenciar_time_cheio(pokemon, int(escolha))

def _descrever_rota(dist, prox, origem, candidatos):
    """Descreve, a partir de origem, o candidato mais próximo (menor caminho de Floyd-Warshall)
    e qual o próximo vértice a seguir para chegar até ele."""
    resultado = mais_proximo(dist, prox, origem, candidatos)
    if resultado is None:
        return None
    vertice, distancia, passo = resultado
    if vertice == origem:
        return f"vértice {vertice} — você já está lá"
    if vertice == passo:
        return f"vértice {vertice} (custo {distancia}) — vizinho a você!"
    return f"vértice {vertice} (custo {distancia}) — vá para o vértice {passo} em seguida"


def _verificar_pokemons_machucados(dist, prox, locais, treinador: Treinador):
    machucados = [p for p in treinador.time if p.muito_machucado]
    if not machucados:
        return
    nomes = ", ".join(p.nome for p in machucados)
    rota = _descrever_rota(dist, prox, treinador.posicao, locais.get("PMC", []))
    rota = rota or "nenhum PMC acessível"
    print(f"\n{nomes} com HP < 5 — leve ao PMC para tratamento! PMC mais próximo: {rota}")


def _pontos_de_interesse(dist, prox, locais, mundo, treinador: Treinador):
    origem = treinador.posicao
    categorias = {
        "Ginásio" : locais.get("GINASIO", []),
        "Hospital (PMC)" : locais.get("PMC", []),
        "Estádio": [locais.get("ESTADIO")] if locais.get("ESTADIO") is not None else [],
        "Pokemon Selvagem": mundo.vertices_com("pokemon_selvagem"),
        "Item": mundo.vertices_com("item"),
        "Treinador": mundo.vertices_com("treinador"),
        "Líder de Ginásio": mundo.vertices_com("lider"),
        "Ovo": mundo.vertices_com("ovo")
    }
    print("\n=== PONTOS DE INTERESSE PRÓXIMOS ===")
    for nome, candidatos in categorias.items():
        resultado = mais_proximo(dist, prox, origem, candidatos)
        if resultado is None:
            print(f"{nome}: nenhum encontrado")
            continue
        vertice, distancia, passo = resultado
        if vertice == origem:
            print(f"{nome}: você já está aqui")
        elif vertice == passo:
            print(f"{nome}: Vértice {vertice} (custo {distancia}) - Vizinho a você!")
        else:
            print(f"{nome}: Vértice {vertice} (custo {distancia}) - via vértice {passo}")



def loop_comandos(grafo, locais, treinador, relogio, dist, prox, mundo):
    proibidos_npc = vertices_proibidos_para_npc(locais)

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

        if cmd == "sair":
            print("Até a próxima!")
            break

        elif cmd == "mapa":
            exibir_mapa(grafo, locais, treinador)

        elif cmd == "status":
            _exibir_status(treinador)

        elif cmd == "pegar":
            tipo = mundo.retirar_item(treinador.posicao)
            if tipo is None:
                print("Não há nenhum item para pegar aqui.")
                continue
            treinador.pegar_item(tipo)
            print(f"Você pegou: {tipo}")

        elif cmd == "interesse":
            _pontos_de_interesse(dist, prox, locais, mundo, treinador)

        elif cmd.startswith("deixar "):
            partes = cmd.split()
            if len(partes) != 2 or not partes[1].isdigit():
                print("Uso: deixar <índice do pokémon no time> (veja os índices em 'status')")
                continue
            try:
                pokemon, tempo = treinador.deixar_no_pmc(int(partes[1]), locais)
            except ValueError as e:
                print(str(e))
                continue
            print(f"Você deixou {pokemon.nome} em tratamento no PMC. Tempo estimado: {tempo} unidades.")

        elif cmd == "retirar":
            if treinador.posicao not in locais.get("PMC", []):
                print("Você não está em um PMC.")
                continue
            recolhidos = treinador.retirar_do_pmc(locais)
            if not recolhidos:
                print("Não há Pokémon prontos para retirar aqui.")
            for pokemon in recolhidos:
                destino_pokemon = "seu time" if pokemon in treinador.time else "o laboratório (time cheio)"
                print(f"Você recolheu {pokemon.nome} do PMC — foi para {destino_pokemon}.")

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
            prontos = treinador.mover(destino, w, relogio)
            mundo.mover_npcs(grafo, proibidos_npc)
            mundo.mover_lideres(grafo, prox, proibidos_npc)
            exibir_estado(grafo, treinador, relogio, locais, mundo)

            for entrada in prontos:
                rota = _descrever_rota(dist, prox, treinador.posicao, [entrada["vertice"]])
                print(f"\n✔ {entrada['pokemon'].nome} foi curado no PMC e está te esperando! Vá até {rota}")

            _verificar_pokemons_machucados(dist, prox, locais, treinador)

            if relogio.acabou():
                print("Tempo esgotado! A Liga fechou as portas.")
                break
            if treinador.classificado and treinador.posicao == locais.get("ESTADIO"):
                print("Você se inscreveu na Liga Pokémon com 8 insígnias — VITÓRIA!")
                break

        else:
            print("Comando desconhecido. Tente: " + "  |  ".join(_comandos_disponiveis(locais, treinador, mundo)))
