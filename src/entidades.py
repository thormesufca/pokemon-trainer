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
        if self.consciente:
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


class MundoStub:
    def vertices_com(self, tipo):
        return []