import random
import sys
import argparse
from src.grafo import ler_grafo, floyd_warshall
from src.relogio import Relogio
from src.entidades import Pokemon, Treinador, Mundo, vertices_proibidos_para_npc
from src.interface import loop_comandos

def popular_mundo(mundo, grafo, locais, evolucoes, populacao):
    # Não pode ter item ou pokemon em vértices 'especiais'
    proibidos = vertices_proibidos_para_npc(locais)
    vertices_livres = [v for v in grafo if v not in proibidos]

    #Gera ordem aleatoria de vertices para não ficar muito sequencial
    random.shuffle(vertices_livres)

    #Dicionário para guardar a quantidade de cada entidade colocada
    restantes = {
        "pokemon": populacao.get('POKEMON', 0),
        "item": populacao.get('ITENS', 0),
        "treinador": populacao.get('TREINADORES', 0),
    }

    #Em cada vertice livre, adiciona uma entidade, decrementando sua quantidade
    contador_treinadores = 0
    for vertice in vertices_livres:
        candidatos = [tipo for tipo, qtd in restantes.items() if qtd > 0]
        if not candidatos:
            break  # nada mais a distribuir

        tipo = random.choice(candidatos)
        if tipo == "pokemon":
            cadeia = random.choice(evolucoes)
            mundo.adicionar_pokemon_selvagem(vertice, Pokemon(cadeia[0], cadeia))
        elif tipo == "item":
            mundo.adicionar_item(vertice)
        elif tipo == "treinador":
            contador_treinadores += 1
            npc = Treinador.criar_treinador_npc(f"Treinador {contador_treinadores}", vertice, evolucoes)
            mundo.adicionar_treinador_npc(npc)

        restantes[tipo] -= 1


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
