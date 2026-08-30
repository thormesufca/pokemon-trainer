import random
import argparse

CADEIAS_EVOLUTIVAS = [
    ["Bulbasaur", "Ivysaur", "Venusaur"],
    ["Charmander", "Charmeleon", "Charizard"],
    ["Squirtle", "Wartortle", "Blastoise"],
    ["Pikachu", "Raichu"],
    ["Geodude", "Graveler", "Golem"],
    ["Gastly", "Haunter", "Gengar"],
    ["Magikarp", "Gyarados"],
    ["Abra", "Kadabra", "Alakazam"],
]

N_GINASIOS = 8  # o jogador precisa de 8 insígnias


def gerar_mapa(n_vertices, n_arestas, peso_min=1, peso_max=20, seed=None, caminho_saida=None):
    """
    Gera um mapa aleatório e conexo no formato do projeto.

    Parâmetros
    ----------
    n_vertices  : número de vértices do grafo
    n_arestas   : número de arestas (>= n_vertices - 1)
    peso_min/max: intervalo dos pesos das arestas
    seed        : semente para reprodutibilidade (None = aleatório)
    caminho_saida: se informado, salva o arquivo no caminho; sempre retorna o conteúdo

    Restrições
    ----------
    n_vertices >= 11  (LAB + ESTADIO + 1 PMC mínimo + 8 GINASIOS)
    n_arestas  >= n_vertices - 1  (árvore geradora mínima)
    n_arestas  <= n_vertices * (n_vertices - 1) // 2  (grafo simples máximo)
    """
    if seed is not None:
        random.seed(seed)

    # PMC sorteado entre 1 e 3, limitado pelos vértices disponíveis
    # 10 fixos: LAB + ESTADIO + 8 GINASIOS; o resto vai para PMC e vértices livres
    n_pmc_max = min(3, n_vertices - 10)
    if n_pmc_max < 1:
        raise ValueError(f"n_vertices deve ser >= 11 (LAB+ESTADIO+8 ginásios+1 PMC mínimo); recebido: {n_vertices}")

    max_arestas = n_vertices * (n_vertices - 1) // 2
    if n_arestas < n_vertices - 1:
        raise ValueError(f"n_arestas deve ser >= {n_vertices - 1} (árvore geradora mínima)")
    if n_arestas > max_arestas:
        raise ValueError(f"n_arestas deve ser <= {max_arestas} para um grafo simples com {n_vertices} vértices")

    n_pmc = random.randint(1, n_pmc_max)

    arestas = _gerar_grafo(n_vertices, n_arestas, peso_min, peso_max)
    locais = _sortear_locais(n_vertices, n_pmc)
    conteudo = _formatar(n_vertices, arestas, locais)

    if caminho_saida:
        with open(caminho_saida, "w") as f:
            f.write(conteudo)

    return conteudo


def _gerar_grafo(n_vertices, n_arestas, peso_min, peso_max):
    """
    Gera arestas de um grafo conexo.

    Estratégia: constrói uma árvore geradora aleatória (n_vertices-1 arestas,
    sempre conexa) e acrescenta arestas extras até atingir n_arestas.
    """
    ordem = list(range(n_vertices))
    random.shuffle(ordem)

    arestas = []
    existentes = set()

    # Árvore geradora: cada vértice i se conecta a um vértice já inserido (0..i-1)
    for i in range(1, n_vertices):
        u = ordem[i]
        v = ordem[random.randint(0, i - 1)]
        w = random.randint(peso_min, peso_max)
        existentes.add((min(u, v), max(u, v)))
        arestas.append((u, v, w))

    # Arestas extras — tenta até 10× o número de arestas desejadas antes de desistir
    tentativas = 0
    limite = (n_arestas - len(arestas)) * 10
    while len(arestas) < n_arestas and tentativas < limite:
        u = random.randint(0, n_vertices - 1)
        v = random.randint(0, n_vertices - 1)
        chave = (min(u, v), max(u, v))
        if u != v and chave not in existentes:
            w = random.randint(peso_min, peso_max)
            existentes.add(chave)
            arestas.append((u, v, w))
        tentativas += 1

    return arestas


def _sortear_locais(n_vertices, n_pmc):
    """Atribui locais obrigatórios a vértices distintos."""
    pool = list(range(n_vertices))
    random.shuffle(pool)

    lab = pool.pop()
    estadio = pool.pop()
    pmc = [pool.pop() for _ in range(n_pmc)]
    ginasios = [pool.pop() for _ in range(N_GINASIOS)]

    return {"LAB": lab, "ESTADIO": estadio, "PMC": pmc, "GINASIO": ginasios}


def _formatar(n_vertices, arestas, locais):
    """Serializa o mapa no formato de texto do projeto."""
    linhas = []

    linhas.append("GRAFO")
    linhas.append(f"{n_vertices} {len(arestas)}")
    for u, v, w in arestas:
        linhas.append(f"{u} {v} {w}")

    linhas.append("")
    linhas.append("LOCAIS")
    linhas.append(f"LAB {locais['LAB']}")
    linhas.append(f"ESTADIO {locais['ESTADIO']}")
    linhas.append(f"PMC {' '.join(str(v) for v in locais['PMC'])}")
    linhas.append(f"GINASIO {' '.join(str(v) for v in locais['GINASIO'])}")

    linhas.append("")
    linhas.append("POPULACAO")
    linhas.append(f"TREINADORES {random.randint(3, 8)}")
    linhas.append(f"POKEMON {random.randint(10, 25)}")
    linhas.append(f"ITENS {random.randint(5, 15)}")
    linhas.append(f"OVOS {random.randint(1, 5)}")

    linhas.append("")
    linhas.append("EVOLUCOES")
    for cadeia in CADEIAS_EVOLUTIVAS:
        linhas.append(" ".join(cadeia))

    return "\n".join(linhas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador de mapa — Rumo à Liga Pokémon")
    parser.add_argument("n_vertices", type=int, help="Número de vértices")
    parser.add_argument("n_arestas", type=int, help="Número de arestas")
    parser.add_argument("--peso-min", type=int, default=1, metavar="N")
    parser.add_argument("--peso-max", type=int, default=20, metavar="N")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--saida", default="mapas/gerado.txt", metavar="ARQUIVO")
    args = parser.parse_args()

    resultado = gerar_mapa(
        args.n_vertices, args.n_arestas,
        args.peso_min, args.peso_max,
        args.seed, args.saida,
    )
    print(resultado)
    if args.saida:
        print(f"\n→ Salvo em {args.saida}")
