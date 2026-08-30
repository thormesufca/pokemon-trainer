from __future__ import annotations
import random

from .tipos import tipos_de


class Pokemon:
    MAX_HP = 100
    XP_EVOLUCAO = 1000
    BONUS_EVOLUCAO = 0.30

    def __init__(self, nome, cadeia_evolutiva, ap_base=None, dp_base=None):
        self.nome = nome
        self.cadeia_evolutiva = cadeia_evolutiva
        self.fase = cadeia_evolutiva.index(nome)  # 0, 1 ou 2
        self.tipos = tipos_de(nome)
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
        self.tipos = tipos_de(self.nome)  # a nova fase pode ganhar/perder tipos (ex.: Charizard vira fire+flying)
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

    @staticmethod
    def aleatorio(cadeia_evolutiva) -> "Pokemon":
        """Pokémon de fase inicial já com XP e HP aleatórios."""
        pokemon = Pokemon(cadeia_evolutiva[0], cadeia_evolutiva)
        pokemon.xp = random.randint(0, Pokemon.XP_EVOLUCAO - 1)
        pokemon.hp = random.randint(20, Pokemon.MAX_HP)
        return pokemon

    #Parte do sistema de batalha, usado na chamada da batalha pelo treinador, em que existe chance de esquiva e de crítico
    def atacar(self, pkmnAdv: Pokemon, bonus_ap=0, bonus_dp_adv=0):
        ap_efetivo = self.ap + bonus_ap
        dp_efetivo_adv = pkmnAdv.dp + bonus_dp_adv
        if (dp_efetivo_adv < ap_efetivo):
            danoF = ap_efetivo - dp_efetivo_adv
            ModuloDifXP = abs(self.xp - pkmnAdv.xp)
            chance = min(1.0, ModuloDifXP / 1000)
            #chance de esquiva
            if random.random() < chance :
                return print(f"{pkmnAdv.nome} esquivou!")
            #chance de crítico
            if random.random() < chance:    
                return pkmnAdv.receber_dano(danoF*2)
            return pkmnAdv.receber_dano(danoF)  
        else :
            return print(f"{pkmnAdv.nome} não recebeu dano")        

    def __repr__(self):
        tipos = "/".join(self.tipos) if self.tipos else "?"
        return f"{self.nome} ({tipos}) HP:{self.hp} XP:{self.xp} AP:{self.ap} DP:{self.dp}"