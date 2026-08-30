from __future__ import annotations
from .pokemon import Pokemon

import random
from collections import Counter
from typing import List

class Treinador:
    MAX_ATIVOS = 6
    MAX_TOTAL = 7  # ativos + ovos
    XP_POR_DISTANCIA = 100  # 1 XP a cada 100 unidades
    DIST_CHOCAGEM = 100  # distância percorrida para um ovo chocar

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
        """Batalha contra outro treinador exige 3 pokémon conscientes (regra exclusiva disso)."""
        return len(self.conscientes) >= 3

    @property
    def pode_capturar(self):
        """Tem que ter pelo menos 1 pokemon consciente."""
        return len(self.conscientes) >= 1

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

    def trocar_com_laboratorio(self, indice_time, indice_laboratorio, locais):
        """Troca um Pokémon do time por um do laboratório; só é permitido no laboratório."""
        if self.posicao != locais.get("LAB"):
            raise ValueError("Você não está no laboratório.")
        if not (0 <= indice_time < len(self.time)):
            raise ValueError("Índice de Pokémon do time inválido.")
        if not (0 <= indice_laboratorio < len(self.laboratorio)):
            raise ValueError("Índice de Pokémon do laboratório inválido.")

        do_time = self.time[indice_time]
        do_laboratorio = self.laboratorio[indice_laboratorio]
        self.time[indice_time] = do_laboratorio
        self.laboratorio[indice_laboratorio] = do_time
        return do_time, do_laboratorio

    def trocar_posicoes_time(self, indice_a, indice_b):
        """Troca a posição de dois Pokémon dentro do time."""
        if not (0 <= indice_a < len(self.time)):
            raise ValueError("Índice de Pokémon inválido.")
        if not (0 <= indice_b < len(self.time)):
            raise ValueError("Índice de Pokémon inválido.")

        self.time[indice_a], self.time[indice_b] = self.time[indice_b], self.time[indice_a]

    def _processar_distancia(self, distancia):
        for p in self.time:
            p.curar_natural(distancia)
            ganho_xp = self._dist_acumulada // self.XP_POR_DISTANCIA
            if ganho_xp > 0:
                p.ganhar_xp(ganho_xp)

        chocados = []
        restante = distancia
        for ovo in list(self.ovos):
            if restante <= 0:
                break
            self.ovos[ovo] -= restante
            if self.ovos[ovo] <= 0:
                restante = -self.ovos[ovo]
                del self.ovos[ovo]
                ovo.capturar(self)
                if len(self.time) < self.MAX_ATIVOS:
                    self.time.append(ovo)
                else:
                    self.laboratorio.append(ovo)
                chocados.append(ovo)
            else:
                restante = 0

        if self._dist_acumulada >= self.XP_POR_DISTANCIA:
            self._dist_acumulada %= self.XP_POR_DISTANCIA

        return chocados

    def ganhar_xp(self, n):
        self.xp += n

    def coletar_insignia(self, ginasio_id):
        self.insignias.add(ginasio_id)

    def classificado(self, total_ginasios):
        """Precisa de 8 insígnias distintas — ou de todas as existentes na região, se ela tiver 8 ginásios ou menos.
        """
        necessarias = min(8, total_ginasios)
        return len(self.insignias) >= necessarias

    def __repr__(self):
        return f"{self.nome} pos:{self.posicao} XP:{self.xp} insígnias:{len(self.insignias)}"

    @staticmethod
    def criar_treinador_npc(nome, posicao_inicial, evolucoes) -> Treinador:
        """Cria um treinador NPC com um time aleatório (3 a MAX_ATIVOS pokémon)"""
        npc = Treinador(nome, posicao_inicial)
        npc.xp = random.randint(0, 20)  # já espalhado na região: XP aleatório (requisito 4)
        for _ in range(random.randint(3, Treinador.MAX_ATIVOS)):
            cadeia = random.choice(evolucoes)
            npc.adicionar_pokemon(Pokemon.aleatorio(cadeia))
        npc.usuario = False
        return npc

    
    #Sistema de batalha se iniciando a partir do treinador
    def iniciarBatalha(self, adv: Treinador, relogio):
        from .lider_ginasio import LiderGinasio  # import tardio: evita ciclo treinador <-> lider_ginasio

        if adv.usuario == True :
            resp = input(f"{adv.nome} Quer batalhar? (s/n)")
            if(resp.lower() == 'n') :
                print(f"Você negou a batalha!")
                return
        turno = 1
        t1 = self.conscientes[:3]
        t2 = adv.conscientes[:3]
        if (self.pode_batalhar and adv.pode_batalhar):
            relogio.avancar(1)  # cada batalha dura o equivalente a uma unidade de tempo
            pk1 = t1[0]
            pk2 = t2[0]
            while len(t1) > 0 and len(t2) > 0:
                print(f"{('='*20)}Turno {turno}{('=' * 20)}")
                if adv.usuario == True :  # só o desafiado pode desistir — o desafiante (self) não pode
                    resp = input(f"{adv.nome} Quer desistir da batalha? (s/n)")
                    if(resp.lower() == 's') :
                        print(f"{adv.nome} desistiu da batalha e perdeu por WO!")
                        if self.xp < adv.xp:
                            self.ganhar_xp(1)
                        else :
                            self.ganhar_xp(3)
                        return
                pk2.atacar(pk1, bonus_ap=adv.xp, bonus_dp_adv=self.xp)
                if not pk1.consciente :
                    #caso o pokemon do desafiante seja derrotado pelo golpe
                    if pk2.xp >= pk1.xp:
                        pk2.ganhar_ponto_batalha()
                    pk1.ganhar_xp(3)
                    t1.pop(0)
                    if self.usuario == True :
                        if len(t1) == 2:
                            while True:
                                escolha = input(f'escolha outro pokemon para batalhar'f"(({t1[0].nome})1/({t1[1].nome})2)")
                                if escolha == "1":
                                    pk1 = t1[0]
                                    break
                                elif escolha == "2":
                                    pk1 = t1[1]
                                    break
                        elif len(t1) == 1 :
                            pk1 = t1[0]
                        # len(t1) == 0: time do desafiante inteiro derrotado, loop termina na próxima checagem do while
                    elif t1:
                        pk1 = t1[0]
                    pk2.ganhar_xp(10)
                else:
                    #caso o pokemon do desafiante sobreviva ao golpe
                    pk1.atacar(pk2, bonus_ap=self.xp, bonus_dp_adv=adv.xp)
                    if not pk2.consciente :
                        if pk1.xp >= pk2.xp:
                            pk1.ganhar_ponto_batalha()
                        pk2.ganhar_xp(3)
                        t2.pop(0)
                        if adv.usuario == True :
                            if len(t2) == 2:
                                while True:
                                    escolha = input(f'escolha outro pokemon para batalhar'f"(({t2[0].nome})1/({t2[1].nome})2)")
                                    if escolha == "1":
                                        pk2 = t2[0]
                                        break
                                    elif escolha == "2":
                                        pk2 = t2[1]
                                        break
                            elif len(t2) == 1 :
                                pk2 = t2[0]
                            # len(t2) == 0: time do desafiado inteiro derrotado, loop termina na próxima checagem do while
                        elif t2:
                            pk2 = t2[0]
                        pk1.ganhar_xp(10)
                turno+=1

            #Casos de vitórias e derrotas(Desafiante/Desafiado)
            vencedor, perdedor = (adv, self) if len(t1) == 0 else (self, adv)
            if vencedor.xp < perdedor.xp:
                vencedor.ganhar_xp(1)
            else:
                vencedor.ganhar_xp(3)
            if isinstance(perdedor, LiderGinasio):
                vencedor.coletar_insignia(perdedor.ginasio)
                print(f"{vencedor.nome} ganhou a insígnia do ginásio {perdedor.ginasio}!")
            print(f"{vencedor.nome} Ganhou!")
        else:
            print("Não é possível iniciar a batalha")

    def iniciarCaptura(self, pkslvg: Pokemon, relogio):
        from src.ui.comandos import adicionar_pokemon_escolha  # import tardio para evita import circular

        if self.usuario == True:
            resp = input(f"{self.nome} Quer tentar capturar o Pokemon? (s/n)")
            if(resp.lower() == 'n') :
                print(f"Você deixou fugir!")
                return "recusou"
            turno = 1
            t1 = self.conscientes[:3]
            backupPkmn: List[Pokemon] = []
            if(self.pode_capturar):
                relogio.avancar(1)  # anda o relógio em 1 (tempo de batalha)
                while len(t1) > 0 and pkslvg.consciente:
                    print(f"{('=' * 20)}Turno {turno}{('=' * 20)}")
                    pk1 = t1[0]
                    pkslvg.atacar(pk1)
                    if not pk1.consciente :
                        #caso o pokemon do desafiante seja derrotado pelo golpe
                        if pkslvg.xp >= pk1.xp:
                            pkslvg.ganhar_ponto_batalha()
                        pk1.ganhar_xp(3)
                        t1.pop(0)
                        backupPkmn.append(pk1)
                        pkslvg.ganhar_xp(10)
                    else :
                        #caso o pokemon do desafiante sobreviva ao golpe
                        pk1.atacar(pkslvg)
                        if not pkslvg.consciente :
                            if pk1.xp >= pkslvg.xp:
                                pk1.ganhar_ponto_batalha()
                            pkslvg.ganhar_xp(3)
                            pk1.ganhar_xp(10)
                    if t1 and pkslvg.consciente and self.usuario == True :  # só pergunta se a captura ainda está em andamento
                        resp = input(f"{self.nome} Quer desistir da captura? (s/n)")
                        if(resp.lower() == 's') :
                            print(f"Você desistiu da captura!")
                            return "desistiu"
                    turno+=1
                if not pkslvg.consciente :
                    adicionar_pokemon_escolha(self, pkslvg)
                    self.ganhar_xp(3)
                    pkslvg.ganhar_xp(3)
                    for pk in backupPkmn:
                        pk.ganhar_xp(3)
                    print(f"{self.nome} capturou um {pkslvg.nome} selvagem!")
                    return "capturado"
                else:
                    print(f"Você perdeu...")
                    return "perdeu"
