"""Ações do jogador: comandos do loop principal e o que cada um faz sobre o estado do jogo."""

import random
from src.grafo import vizinhos
from src.entities import Pokemon, Treinador
from src.ui.exibicao import (
    exibir_mapa, exibir_estado, exibir_status,
    descrever_rota, verificar_pokemons_machucados, pontos_de_interesse,
    pode_batalhar_aqui,
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
    verificar_pokemons_machucados(ctx.dist, ctx.prox, ctx.locais, ctx.treinador)
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
    treinador.ovos[ovo] = Treinador.DIST_CHOCAGEM
    print(f"Você pegou um ovo! Ele choca em {Treinador.DIST_CHOCAGEM} unidades de distância.")
    return False


def _cmd_interesse(ctx):
    pontos_de_interesse(ctx.dist, ctx.prox, ctx.locais, ctx.mundo, ctx.treinador)
    verificar_pokemons_machucados(ctx.dist, ctx.prox, ctx.locais, ctx.treinador)
    return False


def _escolher(candidatos, pergunta):
    """Pede ao jogador para escolher um índice entre os candidatos, se houver mais de um."""
    if len(candidatos) == 1:
        return candidatos[0]
    print(pergunta)
    for i, c in enumerate(candidatos):
        print(f"[{i}] {c.nome}")
    while True:
        escolha = input("> ").strip()
        if escolha.isdigit() and 0 <= int(escolha) < len(candidatos):
            return candidatos[int(escolha)]
        print("Escolha inválida")


def _cmd_desafiar(ctx):
    treinador = ctx.treinador
    if not pode_batalhar_aqui(ctx.locais, treinador.posicao):
        print("Batalhas não são permitidas aqui (laboratório/PMC).")
        return False
    candidatos = [t for t in ctx.mundo.treinadores_npc if t.posicao == treinador.posicao]
    candidatos += [l for l in ctx.mundo.lideres_ginasio.values() if l.posicao == treinador.posicao]
    if not candidatos:
        print("Não há ninguém para desafiar aqui.")
        return False
    if not treinador.pode_batalhar:
        print("Você precisa de ao menos três pokémon conscientes para batalhar.")
        return False

    oponente = _escolher(candidatos, "Quem você quer desafiar?")
    treinador.iniciarBatalha(oponente, ctx.relogio)
    return False


PROB_DESAFIO_NPC = 0.5  # chance de um treinador NPC presente no vértice desafiar o jogador ao chegar


def desafio_npc(ctx):
    """Ao chegar num vértice com treinador NPC, ele pode desafiar o jogador"""
    treinador = ctx.treinador
    if not pode_batalhar_aqui(ctx.locais, treinador.posicao):
        return
    if not treinador.pode_batalhar:
        return
    candidatos = [t for t in ctx.mundo.treinadores_npc
                  if t.posicao == treinador.posicao and t.pode_batalhar]
    if not candidatos:
        return
    if random.random() >= PROB_DESAFIO_NPC:
        return

    npc = random.choice(candidatos)
    print(f"\n{npc.nome} apareceu e quer batalhar!")
    npc.iniciarBatalha(treinador, ctx.relogio)


def _cmd_capturar(ctx):
    treinador = ctx.treinador
    if not pode_batalhar_aqui(ctx.locais, treinador.posicao):
        print("Batalhas não são permitidas aqui (laboratório/PMC).")
        return False
    candidatos = ctx.mundo.pokemons_selvagens.get(treinador.posicao, [])
    if not candidatos:
        print("Não há pokémon selvagem aqui.")
        return False
    if not treinador.pode_capturar:
        print("Você precisa de ao menos um pokémon consciente para capturar.")
        return False

    alvo = _escolher(candidatos, "Qual pokémon selvagem você quer desafiar?")
    resultado = treinador.iniciarCaptura(alvo, ctx.relogio)
    if resultado in ("capturado", "desistiu"):
        ctx.mundo.retirar_pokemon_selvagem(treinador.posicao, alvo)
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


def _cmd_usar(ctx, partes):
    if len(partes) != 2:
        print("Uso: usar <item> (veja os itens em 'status')")
        return False
    tipo = partes[1]
    treinador = ctx.treinador
    if treinador.itens[tipo] <= 0:
        print(f"Você não tem {tipo}.")
        return False
    treinador.usar_item(tipo)
    print(f"Você usou {tipo}!")
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
    ctx.mundo.mover_npcs(ctx.grafo)
    ctx.mundo.mover_lideres(ctx.grafo, ctx.prox)
    exibir_estado(ctx.grafo, treinador, ctx.relogio, ctx.locais, ctx.mundo)

    for entrada in prontos:
        rota = descrever_rota(ctx.dist, ctx.prox, treinador.posicao, [entrada["vertice"]])
        print(f"\n✔ {entrada['pokemon'].nome} foi curado no PMC e está te esperando! Vá até {rota}")

    for ovo in chocados:
        destino_ovo = "seu time" if ovo in treinador.time else "o laboratório (time cheio)"
        print(f"\nUm ovo chocou! Bem-vindo, {ovo.nome}! Foi para {destino_ovo}.")

    desafio_npc(ctx)

    verificar_pokemons_machucados(ctx.dist, ctx.prox, ctx.locais, treinador)

    if ctx.relogio.acabou():
        print("Tempo esgotado! A Liga fechou as portas.")
        return True
    total_ginasios = len(ctx.locais.get("GINASIO", []))
    if treinador.classificado(total_ginasios) and treinador.posicao == ctx.locais.get("ESTADIO"):
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
    "poi": _cmd_interesse,
    "retirar": _cmd_retirar,
    "desafiar": _cmd_desafiar,
    "capturar": _cmd_capturar,
}

# Comandos com argumento — a chave é o prefixo (com o espaço) usado no texto digitado.
COMANDOS_COM_ARGUMENTO = {
    "deixar": _cmd_deixar,
    "usar": _cmd_usar,
    "ir": _cmd_ir,
}
