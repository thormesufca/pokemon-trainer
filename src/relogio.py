import random


class Relogio:
    def __init__(self, grafo):
        self._tempo = 0
        self._prazo = self._calcular_prazo(grafo)

    def _calcular_prazo(self, grafo):
        # cada aresta está duplicada na lista (não-direcionado), então dividimos por 2
        soma = sum(w for vizinhos in grafo.values() for _, w in vizinhos) // 2
        return random.randint(10, 15) * soma

    def avancar(self, unidades):
        self._tempo += unidades

    def tempo_atual(self):
        return self._tempo

    def prazo(self):
        return self._prazo

    def acabou(self):
        return self._tempo >= self._prazo
