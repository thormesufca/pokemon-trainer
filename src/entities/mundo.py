from __future__ import annotations
import random
from .pokemon import Pokemon
from .treinador import Treinador
from .lider_ginasio import LiderGinasio


def vertices_proibidos_para_npc(locais):
    """Vértices onde NPCs (treinadores, pokémon selvagens) não podem ser colocados/passar: LAB, PMC e ginásios."""
    return {locais.get('LAB')} | set(locais.get('PMC', [])) | set(locais.get('GINASIO', []))


class Mundo:
    """Estado do que está espalhado pela região: itens, Pokémon selvagens e treinadores NPC."""

    def __init__(self):
        self.itens = {}               # {vertice: [tipo, ...]}
        self.pokemons_selvagens = {}  # {vertice: [Pokemon, ...]}
        self.treinadores_npc = []     # [Treinador, ...] (cada um sabe sua própria posição)
        self.ovos = {}                # {vertice: [Pokemon, ...]}
        self.lideres_ginasio = {}     # {ginasio_vertice: LiderGinasio}

    def adicionar_item(self, vertice, tipo="erva"):
        self.itens.setdefault(vertice, []).append(tipo)

    def adicionar_pokemon_selvagem(self, vertice, pokemon):
        self.pokemons_selvagens.setdefault(vertice, []).append(pokemon)

    def adicionar_treinador_npc(self, treinador: Treinador):
        self.treinadores_npc.append(treinador)

    def adicionar_lider_ginasio(self, lider: LiderGinasio):
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
        if tipo == "ovo":
            return sorted(v for v, lst in self.ovos.items() if lst)
        return []

    def retirar_item(self, vertice):
        lst = self.itens.get(vertice)
        if not lst:
            return None 
        return lst.pop()

    def adicionar_ovo(self, vertice, pokemon):
        self.ovos.setdefault(vertice, []).append(pokemon)

    def retirar_ovo(self, vertice):
        lst = self.ovos.get(vertice)
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

    def popular(self, grafo, locais, evolucoes, populacao):
        """Espalha pokémon selvagens, itens, ovos e treinadores NPC pelos vértices livres do grafo."""
        proibidos = vertices_proibidos_para_npc(locais)
        vertices_livres = [v for v in grafo if v not in proibidos]

        # Gera ordem aleatoria de vertices para não ficar muito sequencial
        random.shuffle(vertices_livres)

        # Dicionário para guardar a quantidade de cada entidade colocada
        restantes = {
            "pokemon": populacao.get('POKEMON', 0),
            "item": populacao.get('ITENS', 0),
            "treinador": populacao.get('TREINADORES', 0),
            "ovo": populacao.get('OVOS', 0),
        }

        # Em cada vertice livre, adiciona uma entidade, decrementando sua quantidade
        contador_treinadores = 0
        for vertice in vertices_livres:
            candidatos = [tipo for tipo, qtd in restantes.items() if qtd > 0]
            if not candidatos:
                break  # nada mais a distribuir

            tipo = random.choice(candidatos)
            if tipo == "pokemon":
                cadeia = random.choice(evolucoes)
                self.adicionar_pokemon_selvagem(vertice, Pokemon(cadeia[0], cadeia))
            elif tipo == "item":
                self.adicionar_item(vertice)
            elif tipo == "treinador":
                contador_treinadores += 1
                npc = Treinador.criar_treinador_npc(f"Treinador {contador_treinadores}", vertice, evolucoes)
                self.adicionar_treinador_npc(npc)
            elif tipo == "ovo":
                cadeia = random.choice(evolucoes)
                self.adicionar_ovo(vertice, Pokemon(cadeia[0], cadeia))

            restantes[tipo] -= 1

    def criar_lideres_ginasio(self, locais, evolucoes):
        """Cria um LiderGinasio para cada ginásio do mapa e os registra no mundo."""
        for i, ginasio in enumerate(locais.get('GINASIO', []), start=1):
            lider = LiderGinasio.criar(f"Líder {i}", ginasio, evolucoes)
            self.adicionar_lider_ginasio(lider)