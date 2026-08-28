import random
import sys
import argparse
from src.grafo import ler_grafo, floyd_warshall
from src.relogio import Relogio
from src.entidades import Pokemon, Treinador, Mundo
from src.interface import loop_comandos


def popular_mundo(mundo, grafo, locais, evolucoes, populacao):
    vertices = list(grafo.keys())
    # batalhas são proibidas no PMC e no laboratório: nenhum pokémon selvagem pode surgir lá
    proibidos_para_batalha = {locais.get('LAB')} | set(locais.get('PMC', []))
    vertices_para_pokemon = [v for v in vertices if v not in proibidos_para_batalha] or vertices
    for _ in range(populacao.get('POKEMON', 0)):
        cadeia = random.choice(evolucoes)
        p = Pokemon(cadeia[0], cadeia)
        mundo.adicionar_pokemon_selvagem(random.choice(vertices_para_pokemon), p)
    for _ in range(populacao.get('ITENS', 0)):
        mundo.adicionar_item(random.choice(vertices))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapa", default='exemplo.txt')
    args = parser.parse_args()
    grafo, locais, populacao, evolucoes = ler_grafo(f'mapas/{args.mapa}')
    distancias, proximos = floyd_warshall(grafo)
    relogio = Relogio(grafo)
    mundo = Mundo()

    print(f"Mapa carregado — {len(grafo)} vértices | prazo da Liga: {relogio.prazo()} unidades")

    popular_mundo(mundo, grafo, locais, evolucoes, populacao)

    starter = Pokemon(evolucoes[0][0], evolucoes[0])
    treinador = Treinador("Ash", locais['LAB'])
    treinador.adicionar_pokemon(starter)

    loop_comandos(grafo, locais, treinador, relogio, distancias, proximos, mundo)



if __name__ == "__main__":
    main()
