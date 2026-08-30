import random
import sys
import argparse
from src.grafo import ler_grafo, floyd_warshall
from src.relogio import Relogio
from src.entities import Pokemon, Treinador, Mundo
from src.interface import loop_comandos


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapa", default='exemplo.txt')
    args = parser.parse_args()
    grafo, locais, populacao, evolucoes = ler_grafo(f'mapas/{args.mapa}')
    distancias, proximos = floyd_warshall(grafo)
    relogio = Relogio(grafo)
    mundo = Mundo()

    mundo.popular(grafo, evolucoes, populacao)
    mundo.criar_lideres_ginasio(locais, evolucoes)

    print(f"Mapa carregado — {len(grafo)} vértices | prazo da Liga: {relogio.prazo()} unidades")

    nome_jogador = input("Qual é o seu nome, treinador? ").strip() or "Ash"

    starters = evolucoes[:3]
    print("\nEscolha o seu Pokémon inicial (ou 'n' para recusar os três e receber um aleatório):")
    for i, cadeia in enumerate(starters):
        print(f"  [{i}] {cadeia[0]}")

    while True:
        escolha = input("> ").strip().lower()
        if escolha.isdigit() and 0 <= int(escolha) < len(starters):
            cadeia_escolhida = starters[int(escolha)]
            break
        if escolha == "n":
            cadeia_escolhida = random.choice(evolucoes)
            print(f"Você recusou os três iniciais. O professor Carvalho te deu um {cadeia_escolhida[0]} aleatório!")
            break
        print("Escolha inválida.")

    starter = Pokemon(cadeia_escolhida[0], cadeia_escolhida)
    treinador = Treinador(nome_jogador, locais['LAB'])
    treinador.adicionar_pokemon(starter)

    loop_comandos(grafo, locais, treinador, relogio, distancias, proximos, mundo)


if __name__ == "__main__":
    main()
