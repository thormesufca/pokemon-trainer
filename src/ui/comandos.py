"""Ações do jogador: comandos do loop principal e o que cada um faz sobre o estado do jogo."""

import random
from src.grafo import vizinhos
from src.entities import Pokemon, Treinador
from src.ui.exibicao import (
    exibir_mapa, exibir_estado, exibir_status,
    descrever_rota, verificar_pokemons_machucados, pontos_de_interesse,
)


def adicionar_pokemon_escolha(treinador: Treinador, pokemon: Pokemon):
    """Adiciona um Pokémon capturado ao time; se estiver cheio, pede ao jogador para escolher quem enviar ao laboratório."""
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


# --- Handlers de comando ---------------------------------------------------
def _cmd_sair(ctx):
    print("Até a próxima!")
    return True


def _cmd_mapa(ctx):
    exibir_mapa(ctx.grafo, ctx.locais, ctx.treinador)
    return False


def _cmd_status(ctx):
    exibir_status(ctx.treinador)
    return False


def _cmd_pegar(ctx):
    tipo = ctx.mundo.retirar_item(ctx.treinador.posicao)
    if tipo is None:
        print("Não há nenhum item para pegar aqui.")
        return False
    ctx.treinador.pegar_item(tipo)
    print(f"Você pegou: {tipo}")
    return False


def _cmd_pegar_ovo(ctx):
    treinador = ctx.treinador
    if len(treinador.time) + len(treinador.ovos) >= treinador.MAX_TOTAL:
        print("Você não pode carregar mais ovos ou Pokémon no momento.")
        return False
    ovo = ctx.mundo.retirar_ovo(treinador.posicao)
    if ovo is None:
        print("Não há ovos aqui.")
        return False
    dist_choca = random.randint(50, 200)
    treinador.ovos[ovo] = dist_choca
    print(f"Você pegou um ovo de {ovo.nome}! Ele choca em {dist_choca} unidades de distância.")
    return False


def _cmd_interesse(ctx):
    pontos_de_interesse(ctx.dist, ctx.prox, ctx.locais, ctx.mundo, ctx.treinador)
    return False


def _cmd_retirar(ctx):
    treinador = ctx.treinador
    if treinador.posicao not in ctx.locais.get("PMC", []):
        print("Você não está em um PMC.")
        return False
    recolhidos = treinador.retirar_do_pmc(ctx.locais)
    if not recolhidos:
        print("Não há Pokémon prontos para retirar aqui.")
    for pokemon in recolhidos:
        destino_pokemon = "seu time" if pokemon in treinador.time else "o laboratório (time cheio)"
        print(f"Você recolheu {pokemon.nome} do PMC — foi para {destino_pokemon}.")
    return False


def _cmd_deixar(ctx, partes):
    if len(partes) != 2 or not partes[1].isdigit():
        print("Uso: deixar <índice do pokémon no time> (veja os índices em 'status')")
        return False
    try:
        pokemon, tempo = ctx.treinador.deixar_no_pmc(int(partes[1]), ctx.locais)
    except ValueError as e:
        print(str(e))
        return False
    print(f"Você deixou {pokemon.nome} em tratamento no PMC. Tempo estimado: {tempo} unidades.")
    return False


def _cmd_ir(ctx, partes):
    if len(partes) != 2 or not partes[1].isdigit():
        print("Uso: ir <número do vértice>")
        return False

    treinador = ctx.treinador
    destino = int(partes[1])
    adj = dict(vizinhos(ctx.grafo, treinador.posicao))
    if destino not in adj:
        vizs = ", ".join(str(v) for v in sorted(adj))
        print(f"Vértice {destino} não é vizinho. Vizinhos: {vizs}")
        return False

    w = adj[destino]
    prontos, chocados = treinador.mover(destino, w, ctx.relogio)
    ctx.mundo.mover_npcs(ctx.grafo, ctx.proibidos_npc)
    ctx.mundo.mover_lideres(ctx.grafo, ctx.prox, ctx.proibidos_npc)
    exibir_estado(ctx.grafo, treinador, ctx.relogio, ctx.locais, ctx.mundo)

    for entrada in prontos:
        rota = descrever_rota(ctx.dist, ctx.prox, treinador.posicao, [entrada["vertice"]])
        print(f"\n✔ {entrada['pokemon'].nome} foi curado no PMC e está te esperando! Vá até {rota}")

    for ovo in chocados:
        destino_ovo = "seu time" if ovo in treinador.time else "o laboratório (time cheio)"
        print(f"\nUm ovo chocou! Bem-vindo, {ovo.nome}! Foi para {destino_ovo}.")

    verificar_pokemons_machucados(ctx.dist, ctx.prox, ctx.locais, treinador)

    if ctx.relogio.acabou():
        print("Tempo esgotado! A Liga fechou as portas.")
        return True
    if treinador.classificado and treinador.posicao == ctx.locais.get("ESTADIO"):
        print("Você se inscreveu na Liga Pokémon com 8 insígnias — VITÓRIA!")
        return True
    return False


# Comandos sem argumento.
COMANDOS_SEM_ARGUMENTO = {
    "sair": _cmd_sair,
    "mapa": _cmd_mapa,
    "status": _cmd_status,
    "pegar": _cmd_pegar,
    "pegar ovo": _cmd_pegar_ovo,
    "interesse": _cmd_interesse,
    "retirar": _cmd_retirar,
}

# Comandos com argumento — a chave é o prefixo (com o espaço) usado no texto digitado.
COMANDOS_COM_ARGUMENTO = {
    "deixar ": _cmd_deixar,
    "ir ": _cmd_ir,
}
