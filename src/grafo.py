def ler_grafo(caminho):
    """
    Lê o arquivo de entrada e devolve:
      - grafo: dict {vertice: [(vizinho, peso), ...]}
      - locais: dict com LAB, ESTADIO, PMC (lista), GINASIO (lista)
      - populacao: dict com TREINADORES, POKEMON, ITENS
      - evolucoes: lista de listas [[fase1, fase2, ...], ...]
    """
    grafo = {}
    locais = {"PMC": [], "GINASIO": []}
    populacao = {}
    evolucoes = []

    with open(caminho) as f:
        secao = None
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue

            if linha in ("GRAFO", "LOCAIS", "POPULACAO", "EVOLUCOES"):
                secao = linha
                cabecalho_grafo_lido = False
                continue

            if secao == "GRAFO":
                partes = linha.split()
                if not cabecalho_grafo_lido:
                    # primeira linha da seção: V E (só usamos pra inicializar os vértices)
                    n_vertices = int(partes[0])
                    for v in range(n_vertices):
                        grafo[v] = []
                    cabecalho_grafo_lido = True
                else:
                    u, v, w = int(partes[0]), int(partes[1]), int(partes[2])
                    grafo[u].append((v, w))
                    grafo[v].append((u, w))  # não-direcionado: aresta nos dois sentidos

            elif secao == "LOCAIS":
                partes = linha.split()
                tipo = partes[0]
                vertices = list(map(int, partes[1:]))
                if tipo in ("PMC", "GINASIO"):
                    locais[tipo] = vertices
                else:
                    locais[tipo] = vertices[0]  # LAB e ESTADIO têm um único vértice

            elif secao == "POPULACAO":
                chave, valor = linha.split()
                populacao[chave] = int(valor)

            elif secao == "EVOLUCOES":
                evolucoes.append(linha.split())

    _validar_conexo(grafo)
    return grafo, locais, populacao, evolucoes


def floyd_warshall(grafo: dict):
    """
    Executa floyd-warshall no grafo e retorna duas matrizes.
    A primeira matriz tem a distância entre cada par de vértices do grafo
    A segunda matriz é composta do primeiro passo do menor caminho entre qualquer par de vértices
    """

    n = len(grafo)
    INF = float('inf')

    dist = [[INF] * n for _ in range(n)]
    prox = [[None] * n for _ in range(n)]

    for v in range(n):
        dist[v][v] = 0 # Zerar distâncias para si mesmo
        prox[v][v] = v # Proximo para si mesmo é ele mesmo

    for u in grafo:
        for v, w in grafo[u]:
            if w < dist[u][v]:
                dist[u][v] = w
                prox[u][v] = v

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    prox[i][j] = prox[i][k]

    return dist, prox

def _validar_conexo(grafo):
    """
    Faz uma BFS a partir do vértice 0 e verifica se todos os vértices são alcançáveis.
    Se não forem, o mapa está desconexo e o jogo é impossível.
    """
    visitados = set()
    fila = [0]
    while fila:
        v = fila.pop(0)
        if v in visitados:
            continue
        visitados.add(v)
        for vizinho, _ in grafo[v]:
            if vizinho not in visitados:
                fila.append(vizinho)

    if visitados != set(grafo.keys()):
        raise ValueError("O grafo não é conexo — há vértices inacessíveis.")

def mais_proximo(dist, prox, origem, candidatos: list[int]):
    alcancaveis = [(dist[origem][v], v) for v in candidatos if dist[origem][v] < float('inf')]
    if not alcancaveis:
        return None
    distancia, vertice = min(alcancaveis)
    return vertice, distancia, prox[origem][vertice]

def vizinhos(grafo, v):
    return grafo[v]


def peso(grafo, u, v):
    for vizinho, w in grafo[u]:
        if vizinho == v:
            return w
    return None
