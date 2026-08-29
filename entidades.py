from __future__ import annotations

import random
from collections import Counter
from typing import List
#adicionar abaixo:
import interface

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
    #adicionar abaixo:
    #Parte do sistema de batalha, usado na chamada da batalha pelo treinador,
    #em que existe chance de esquiva e de crítico
    def atacar(self, pkmnAdv: Pokemon):
        if (pkmnAdv.dp < self.ap):
            danoF = self.ap - pkmnAdv.dp
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

    #adicionar o "usuario = bool"(false para npc e true para jogador)
    def __init__(self, nome, posicao_inicial, usuario = bool):
        self.nome = nome
        self.posicao = posicao_inicial
        self.xp = 0
        self.time: List[Pokemon] = []
        self.laboratorio: List[Pokemon] = []
        self.itens = Counter()
        self.ovos = {}  # {Pokemon: dist_restante}
        self.insignias = set()
        self._dist_acumulada = 0
        #copiar abaixo
        self.usuario = usuario

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
    #copiar abaixo:
    #Sistema de batalha se iniciando a partir do treinador
    def iniciarBatalha(self, adv: Treinador):
        if adv.usuario == True :
            resp = input(f"{adv.nome} Quer batalhar? (s/n)")
            if(resp.lower() == 'n') :
                print(f"Você negou a batalha!")
                return
        turno = 1
        t1 = self.conscientes[:3]
        t2 = adv.conscientes[:3]
        if(self.pode_batalhar and adv.pode_batalhar):
            pk1 = t1[0]
            pk2 = t2[0]
            while len(t1) > 0 and len(t2) > 0:
                print(f"Turno {turno}")
                if self.usuario == True :
                    resp = input(f"{adv.nome} Quer desistir da batalha? (s/n)")
                    if(resp.lower() == 's') :
                        print(f"Você desistiu da batalha e perdeu por WO!")
                        if self.xp <= adv.xp:
                            self.ganhar_xp(3)
                        else :
                            self.ganhar_xp(1)
                        return
                pk2.atacar(pk1)
                if not pk1.consciente :
                    #caso o pokemon do desafiante seja derrotado pelo golpe
                    pk1.ganhar_xp(3)
                    t1.pop(0)
                    if self.usuario == True :
                        if len(t1) == 2:
                            while(True):
                                escolha = int(input(f'escolha outro pokemon para batalhar'f"(({t1[0].nome})1/({t1[1].nome})2)"))
                                if(escolha == 1) :
                                    pk1 = t1[0]
                                    break
                                elif(escolha == 2) :
                                    pk1 = t1[1]
                                    break
                        elif len(t1) == 1 :
                            pk1 = t1[0]
                    else :
                        pk1 = t1[0]
                    pk2.ganhar_xp(10)
                else:
                    #caso o pokemon do desafiante sobreviva ao golpe
                    pk1.atacar(pk2)
                    if not pk2.consciente :
                        pk2.ganhar_xp(3)
                        t2.pop(0)
                        if adv.usuario == True :
                            if len(t2) == 2:
                                while(True):
                                    escolha = int(input(f'escolha outro pokemon para batalhar'f"(({t2[0].nome})1/({t2[1].nome})2)"))
                                    if(escolha == 1) :
                                        pk2 = t2[0]
                                        break
                                    elif(escolha == 2) :
                                        pk2 = t2[1]
                                        break
                            elif len(t2) == 1 :
                                pk2 = t2[0]
                        else :
                            pk2 = t2[0]
                        pk1.ganhar_xp(10)
                turno+=1   
        else :
            print(f"Não é possível iniciar a batalha")   
        #Casos de vitórias e derrotas(Desafiante/Desafiado)                  
        if len(t1) == 0 and self.xp < adv.xp :
            adv.ganhar_xp(1)
            print(f"{adv.nome} Ganhou!")
        elif len(t1) == 0 and self.xp >= adv.xp :
            adv.ganhar_xp(3)
            print(f"{adv.nome} Ganhou!")
        if len(t2) == 0 and adv.xp < self.xp :
            self.ganhar_xp(1)
            print(f"{self.nome} Ganhou!")
        elif len(t2) == 0 and adv.xp >= self.xp :
            self.ganhar_xp(3)
            print(f"{self.nome} Ganhou!") 

    #copiar abaixo:        
    def iniciarCaptura(self, pkslvg: Pokemon):
        if self.usuario == True:    
            resp = input(f"{self.nome} Quer tentar capturar o Pokemon? (s/n)")
            if(resp.lower() == 'n') :
                print(f"Você deixou fugir!")
                return
            turno = 1
            t1 = self.conscientes[:3]
            backupPkmn: List[Pokemon] = t1[0]
            if(self.pode_batalhar):
                while len(t1) > 0 and pkslvg.consciente:
                    print(f"Turno {turno}")
                    pk1 = t1[0]
                    pkslvg.atacar(pk1)
                    if not pk1.consciente :
                        #caso o pokemon do desafiante seja derrotado pelo golpe
                        pk1.ganhar_xp(3)
                        t1.pop(0)
                        backupPkmn.append(pk1)
                        pkslvg.ganhar_xp(10)
                    else :
                        #caso o pokemon do desafiante sobreviva ao golpe
                        pk1.atacar(pkslvg)
                        if not pkslvg.consciente :
                            pkslvg.ganhar_xp(3)
                            pk1.ganhar_xp(10)
                    if self.usuario == True :
                        resp = input(f"{self.nome} Quer desistir da captura? (s/n)")
                        if(resp.lower() == 's') :
                            print(f"Você desistiu da captura!")
                            return
                    turno+=1
                if not pkslvg.consciente :
                    interface.adicionar_pokemon_escolha(self, pkslvg)
                    pkslvg.ganhar_xp(3)
                    for pk in backupPkmn:
                        pk.ganhar_xp(3)
                    print(f"{self.nome} capturou um {pkslvg.nome} selvagem!")
                else:
                    print(f"Você perdeu...")          



class MundoStub:
    def vertices_com(self, tipo):
        return []