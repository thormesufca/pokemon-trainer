from __future__ import annotations
from .pokemon import Pokemon

import random
from collections import Counter
from typing import List

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
        self.usuario = True
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
        chocados = self._processar_distancia(peso)
        pmc_prontos = self._processar_pmc(peso)
        return pmc_prontos, chocados
    
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
        for p in self.time:
            p.curar_natural(distancia)
            ganho_xp = self._dist_acumulada // self.XP_POR_DISTANCIA
            if ganho_xp > 0:
                p.ganhar_xp(ganho_xp)

        chocados = []
        for ovo in list(self.ovos):
            self.ovos[ovo] -= distancia
            if self.ovos[ovo] <= 0:
                del self.ovos[ovo]
                ovo.capturar(self)
                if len(self.time) < self.MAX_ATIVOS:
                    self.time.append(ovo)
                else:
                    self.laboratorio.append(ovo)
                chocados.append(ovo)

        if self._dist_acumulada >= self.XP_POR_DISTANCIA:
            self._dist_acumulada %= self.XP_POR_DISTANCIA

        return chocados

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
        npc.usuario = False
        return npc
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
        if (self.pode_batalhar and adv.pode_batalhar):
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
        
    def iniciarCaptura(self, pkslvg: Pokemon):
        from src.ui.comandos import adicionar_pokemon_escolha  # import tardio: evita ciclo entities <-> ui

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
                    adicionar_pokemon_escolha(self, pkslvg)
                    pkslvg.ganhar_xp(3)
                    for pk in backupPkmn:
                        pk.ganhar_xp(3)
                    print(f"{self.nome} capturou um {pkslvg.nome} selvagem!")
                else:
                    print(f"Você perdeu...") 
