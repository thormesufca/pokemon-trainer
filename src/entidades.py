from __future__ import annotations

import random
from collections import Counter
from typing import List

class Pokemon:
    MAX_HP = 100
    XP_EVOLUCAO = 1000
    BONUS_EVOLUCAO = 0.30

    def __init__(self, nome, cadeia_evolutiva, ap_base=None, dp_base=None):
        self.nome = nome
        self.cadeia_evolutiva = cadeia_evolutiva
        self.fase = cadeia_evolutiva.index(nome)  # 0, 1 ou 2
        self.hp = 100
        self.xp = 0
        self.ap_base = ap_base if ap_base is not None else random.randint(10, 30)
        self.dp_base = dp_base if dp_base is not None else random.randint(5, 20)
        self._pontos_ap = 0
        self._pontos_dp = 0
        self._tempo_inconsciente = 0  # unidades restantes até recuperar consciência
        self._dono: Treinador = None

    @property
    def ap(self):
        return int(self.ap_base + 0.1 * self.xp + self._pontos_ap)

    @property
    def dp(self):
        return int(self.dp_base + 0.1 * self.xp + self._pontos_dp)

    @property
    def consciente(self):
        return self.hp >= 20 and self._tempo_inconsciente == 0

    @property
    def muito_machucado(self):
        return self.hp < 5

    @property
    def tem_dono(self):
        return self._dono is not None

    def ganhar_xp(self, n):
        self.xp += n
        if self.xp >= self.XP_EVOLUCAO and self.fase < len(self.cadeia_evolutiva) - 1:
            self._evoluir()

    def _evoluir(self):
        self.fase += 1
        self.nome = self.cadeia_evolutiva[self.fase]
        self.ap_base = int(self.ap_base * (1 + self.BONUS_EVOLUCAO))
        self.dp_base = int(self.dp_base * (1 + self.BONUS_EVOLUCAO))
        self.xp = 0  # zera após evoluir (máximo 3 fases)

    def ganhar_ponto_batalha(self):
        self._pontos_ap += 1
        self._pontos_dp += 1

    def receber_dano(self, dano):
        self.hp = max(0, self.hp - dano)
        if not self.consciente:
            self._tempo_inconsciente = random.randint(10, 50)

    def curar_natural(self, distancia):
        if not self.muito_machucado:
            ganho = distancia // 10
            self.curar(ganho)
        if not self.consciente:
            self._tempo_inconsciente = max(0, self._tempo_inconsciente - distancia)

    def curar_pmc(self):
        self.curar(self.MAX_HP)
        self._tempo_inconsciente = 0

    def curar(self, amount:int):
        self.hp = min(self.MAX_HP, self.hp + amount)

    def capturar(self, treinador: Treinador):
        self._dono = treinador


    def __repr__(self):
        return f"{self.nome} HP:{self.hp} XP:{self.xp} AP:{self.ap} DP:{self.dp}"


class Treinador:
    MAX_ATIVOS = 6
    MAX_TOTAL = 7  # ativos + ovos
    XP_POR_DISTANCIA = 100  # 1 XP a cada 100 unidades

    def _efeito_erva(self):
        for p in self.time:
            if p.consciente:
                p.curar(10)
    EFEITOS = {
        "erva": _efeito_erva
    }


    def __init__(self, nome, posicao_inicial):
        self.nome = nome
        self.posicao = posicao_inicial
        self.xp = 0
        self.time: List[Pokemon] = []
        self.laboratorio: List[Pokemon] = []
        self.itens = Counter()
        self.ovos = {}  # {Pokemon: dist_restante}
        self.insignias = set()
        self._dist_acumulada = 0
        self.pmc_pendentes = []  # [{"pokemon", "vertice", "restante", "total", "notificado"}, ...]

    @property
    def conscientes(self):
        return [p for p in self.time if p.consciente]


    @property
    def pode_batalhar(self):
        return len(self.conscientes) >= 3

    @property
    def time_cheio(self):
        return len(self.time) >= self.MAX_ATIVOS

    def mover(self, destino, peso, relogio):
        relogio.avancar(peso)
        self.posicao = destino
        self._dist_acumulada += peso
        self._processar_distancia(peso)
        return self._processar_pmc(peso)

    def deixar_no_pmc(self, indice, locais):
        """Deixa um Pokémon muito machucado (HP < 5) em tratamento no PMC atual."""
        if self.posicao not in locais.get("PMC", []):
            raise ValueError("Você não está em um PMC.")
        if not (0 <= indice < len(self.time)):
            raise ValueError("Índice de Pokémon inválido.")
        pokemon = self.time[indice]
        if not pokemon.muito_machucado:
            raise ValueError(f"{pokemon.nome} não precisa de tratamento no PMC (HP >= 5).")

        self.time.pop(indice)
        tempo = random.randint(10, 50)  # tempo necessário parado no PMC, em unidades de distância/tempo
        self.pmc_pendentes.append({
            "pokemon": pokemon,
            "vertice": self.posicao,
            "restante": tempo,
            "total": tempo,
            "notificado": False,
        })
        return pokemon, tempo

    def _processar_pmc(self, unidades):
        """Avança o tempo de tratamento dos Pokémon deixados no PMC; retorna os recém-curados."""
        prontos = []
        for entrada in self.pmc_pendentes:
            if entrada["notificado"]:
                continue
            entrada["restante"] = max(0, entrada["restante"] - unidades)
            if entrada["restante"] == 0:
                entrada["pokemon"].curar_pmc()
                entrada["notificado"] = True
                prontos.append(entrada)
        return prontos

    def retirar_do_pmc(self, locais):
        """Recolhe, automaticamente, os Pokémon já curados que aguardam no PMC atual."""
        if self.posicao not in locais.get("PMC", []):
            return []

        prontos_aqui = [e for e in self.pmc_pendentes
                        if e["notificado"] and e["vertice"] == self.posicao]
        retirados = []
        for entrada in prontos_aqui:
            self.pmc_pendentes.remove(entrada)
            pokemon = entrada["pokemon"]
            if self.time_cheio:
                self.laboratorio.append(pokemon)
            else:
                self.time.append(pokemon)
            retirados.append(pokemon)
        return retirados

    def pegar_item(self, tipo: str):
        self.itens[tipo] += 1

    def usar_item(self, tipo: str):
        if self.itens[tipo] <= 0:
            print("Você não tem esse item")
            return
        self.EFEITOS[tipo](self)
        self.itens[tipo] -= 1

    def adicionar_pokemon(self, pokemon: Pokemon):
        if pokemon.tem_dono:
            raise ValueError("Pokemon já tem dono")

        if self.time_cheio:
            raise RuntimeError("Time cheio")

        pokemon.capturar(self)
        self.time.append(pokemon)

    def gerenciar_time_cheio(self, novo_pokemon:Pokemon, indice):
        novo_pokemon.capturar(self)
        candidatos = self.time + [novo_pokemon]
        enviado = candidatos.pop(indice)
        self.laboratorio.append(enviado)
        self.time = candidatos


    def _processar_distancia(self, distancia):
        # XP por distância para cada Pokémon do time
        for p in self.time:
            p.curar_natural(distancia)
            ganho_xp = self._dist_acumulada // self.XP_POR_DISTANCIA
            if ganho_xp > 0:
                p.ganhar_xp(ganho_xp)

        # chocação de ovos
        for ovo in list(self.ovos):
            self.ovos[ovo] -= distancia
            if self.ovos[ovo] <= 0:
                del self.ovos[ovo]
                if len(self.time) < self.MAX_ATIVOS:
                    self.time.append(ovo)

        if self._dist_acumulada >= self.XP_POR_DISTANCIA:
            self._dist_acumulada %= self.XP_POR_DISTANCIA

    def ganhar_xp(self, n):
        self.xp += n

    def coletar_insignia(self, ginasio_id):
        self.insignias.add(ginasio_id)

    @property
    def classificado(self):
        return len(self.insignias) >= 8

    def __repr__(self):
        return f"{self.nome} pos:{self.posicao} XP:{self.xp} insígnias:{len(self.insignias)}"

    @staticmethod
    def criar_treinador_npc(nome, posicao_inicial, evolucoes) -> Treinador:
        """Cria um treinador NPC com um time aleatório (3 a MAX_ATIVOS pokémon)"""
        npc = Treinador(nome, posicao_inicial)
        for _ in range(random.randint(3, Treinador.MAX_ATIVOS)):
            cadeia = random.choice(evolucoes)
            npc.adicionar_pokemon(Pokemon(cadeia[0], cadeia))
        return npc


class LiderGinasio(Treinador):
    """Líder de um ginásio: fixo ou móvel em relação ao seu vértice de origem."""

    #Tempo fora deve ser aproximadamente metade do tempo em casa, porque presume vagando e retornando
    TEMPO_MIN_FORA = 10
    TEMPO_MAX_FORA = 30
    TEMPO_MIN_CASA = 10
    TEMPO_MAX_CASA = 50

    def __init__(self, nome, ginasio, movel):
        super().__init__(nome, ginasio)
        self.ginasio = ginasio  # vértice de origem; também serve de id da insígnia concedida
        self.movel = movel
        self.estado = "EM_CASA"  # EM_CASA | VAGANDO | RETORNANDO
        self.contador = random.randint(self.TEMPO_MIN_CASA, self.TEMPO_MAX_CASA) if movel else None #Inicia contador com tempo em casa, se móvel

    @property
    def presente(self):
        return self.posicao == self.ginasio

    def passo(self, grafo, prox, vertices_proibidos):
        """Avança um passo no ciclo de movimentação (um vértice por chamada)."""
        if not self.movel:
            return  # fixo: nunca sai do ginásio

        if self.estado == "EM_CASA":
            self.contador -= 1
            if self.contador <= 0:
                self.estado = "VAGANDO"
                self.contador = random.randint(self.TEMPO_MIN_FORA, self.TEMPO_MAX_FORA) #Reseta o contador para tempo fora
                self._passo_vagando(grafo, vertices_proibidos)  # já sai andando neste turno

        elif self.estado == "VAGANDO":
            self._passo_vagando(grafo, vertices_proibidos)
            if self.contador <= 0:
                self.estado = "RETORNANDO"

        elif self.estado == "RETORNANDO":
            if self.posicao == self.ginasio:
                self.estado = "EM_CASA"
                self.contador = random.randint(self.TEMPO_MIN_CASA, self.TEMPO_MAX_CASA) #Reseta contador para tempo em casa
            else:
                self.posicao = prox[self.posicao][self.ginasio] #Dá um passo pelo menor caminho

    def _passo_vagando(self, grafo, vertices_proibidos):
        candidatos = [v for v, _ in grafo[self.posicao] if v not in vertices_proibidos] #Dá um passo para um vértice aleatório
        if candidatos:
            self.posicao = random.choice(candidatos)
        self.contador -= 1

    @staticmethod
    def criar(nome, ginasio, evolucoes) -> "LiderGinasio":
        """Cria um Líder de ginásio com time cheio de pokemons"""
        lider = LiderGinasio(nome, ginasio, movel=random.choice([True, False]))
        for _ in range(Treinador.MAX_ATIVOS):
            cadeia = random.choice(evolucoes)
            lider.adicionar_pokemon(Pokemon(cadeia[0], cadeia))
        return lider


def vertices_proibidos_para_npc(locais):
    return {locais.get('LAB')} | set(locais.get('PMC', [])) | set(locais.get('GINASIO', []))


class Mundo:
    """Estado do que está espalhado pela região: itens, Pokémon selvagens e treinadores NPC."""

    def __init__(self):
        self.itens = {}               # {vertice: [tipo, ...]}
        self.pokemons_selvagens = {}  # {vertice: [Pokemon, ...]}
        self.treinadores_npc = []     # [Treinador, ...] (cada um sabe sua própria posição)
        self.lideres_ginasio = {}     # {ginasio_vertice: LiderGinasio}

    def adicionar_item(self, vertice, tipo="erva"):
        self.itens.setdefault(vertice, []).append(tipo)

    def adicionar_pokemon_selvagem(self, vertice, pokemon):
        self.pokemons_selvagens.setdefault(vertice, []).append(pokemon)

    def adicionar_treinador_npc(self, treinador: "Treinador"):
        self.treinadores_npc.append(treinador)

    def adicionar_lider_ginasio(self, lider: "LiderGinasio"):
        self.lideres_ginasio[lider.ginasio] = lider

    def vertices_com(self, tipo):
        if tipo == "item":
            return sorted(v for v, lst in self.itens.items() if lst)
        if tipo == "pokemon_selvagem":
            return sorted(v for v, lst in self.pokemons_selvagens.items() if lst)
        if tipo == "treinador":
            return sorted({t.posicao for t in self.treinadores_npc})
        if tipo == "lider":
            return sorted({l.posicao for l in self.lideres_ginasio.values()})
        return []  # TODO "ovo" e outras categorias

    def retirar_item(self, vertice):
        lst = self.itens.get(vertice)
        if not lst:
            return None
        return lst.pop()

    def mover_npcs(self, grafo, vertices_proibidos):
        def passo_aleatorio(origem):
            candidatos = [v for v, _ in grafo[origem] if v not in vertices_proibidos]
            return random.choice(candidatos) if candidatos else origem

        novos_pokemons = {}
        for vertice, lista in self.pokemons_selvagens.items():
            for p in lista:
                destino = passo_aleatorio(vertice)
                novos_pokemons.setdefault(destino, []).append(p)
        self.pokemons_selvagens = novos_pokemons

        for treinador in self.treinadores_npc:
            treinador.posicao = passo_aleatorio(treinador.posicao)

    def mover_lideres(self, grafo, prox, vertices_proibidos):
        for lider in self.lideres_ginasio.values():
            lider.passo(grafo, prox, vertices_proibidos)