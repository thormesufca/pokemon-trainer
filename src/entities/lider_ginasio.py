import random
from .treinador import Treinador
from .pokemon import Pokemon

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
        self.usuario = False

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
