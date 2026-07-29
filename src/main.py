import random
from src.grafo import ler_grafo
from src.relogio import Relogio
from src.entidades import Pokemon, Treinador
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
    grafo, locais, populacao, evolucoes = ler_grafo('mapas/exemplo.txt')
    relogio = Relogio(grafo)

    print(f"Mapa carregado — {len(grafo)} vértices | prazo da Liga: {relogio.prazo()} unidades")

    popular_mundo(grafo, evolucoes, populacao)

    starter = Pokemon(evolucoes[0][0], evolucoes[0])
    treinador = Treinador("Ash", locais['LAB'])
    treinador.time.append(starter)

    loop_comandos(grafo, locais, treinador, relogio)


if __name__ == "__main__":
    main()
