import random
import sys
from src.grafo import ler_grafo, floyd_warshall
from src.relogio import Relogio
from src.entidades import Pokemon, Treinador, MundoStub
from src.interface import loop_comandos


def popular_mundo(grafo, evolucoes, populacao):
    vertices = list(grafo.keys())
    pokemons_soltos = []
    for _ in range(populacao['POKEMON']):
        cadeia = random.choice(evolucoes)
        p = Pokemon(cadeia[0], cadeia)
        p.vertice = random.choice(vertices)
        pokemons_soltos.append(p)
    return pokemons_soltos


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    grafo, locais, populacao, evolucoes = ler_grafo('mapas/exemplo.txt')
    distancias, proximos = floyd_warshall(grafo)
    relogio = Relogio(grafo)
    mundo = MundoStub()

    print(f"Mapa carregado — {len(grafo)} vértices | prazo da Liga: {relogio.prazo()} unidades")

    popular_mundo(grafo, evolucoes, populacao)

    starter = Pokemon(evolucoes[0][0], evolucoes[0])
    treinador = Treinador("Ash", locais['LAB'])
    treinador.adicionar_pokemon(starter)

    loop_comandos(grafo, locais, treinador, relogio, distancias, proximos, mundo)



if __name__ == "__main__":
    main()
