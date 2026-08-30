# Rumo à Liga Pokémon

Simulação de uma jornada Pokémon sobre um grafo: o treinador viaja entre vértices desafiando líderes de ginásio, capturando pokémon selvagens e treinadores NPC, até reunir insígnias suficientes e se inscrever na Liga a tempo.

## Requisitos

- Python 3.9 ou superior
- Nenhuma dependência externa é necessária para jogar (só biblioteca padrão)

> O `requirements.txt` (`requests`, `certifi`, etc.) só é usado pelo script opcional `src/download_pokemons_1st.py`, que baixa dados da PokéAPI. Não é preciso instalá-lo para rodar o jogo.

## Instalação

1. Clone o repositório e entre na pasta do projeto:
   ```bash
   git clone https://github.com/thormesufca/pokemon-trainer
   cd pokemon-trainer
   ```

2. (Opcional, mas recomendado) Crie e ative um ambiente virtual:

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **Linux/macOS:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Só é necessário instalar dependências se for usar o script de download de dados da PokéAPI:
   ```bash
   pip install -r requirements.txt
   ```

## Como executar o jogo

O jogo é executado como módulo, a partir da **raiz do projeto** (é onde ficam as pastas `src/` e `mapas/`):

```bash
python -m src.main
```

Por padrão, carrega o mapa `mapas/exemplo.txt` (9 vértices). Para usar outro mapa (deve estar dentro da pasta `mapas/`):

```bash
python -m src.main --mapa gerado.txt
```

## Gerando um mapa novo

O gerador cria um grafo aleatório e conexo, já populado com laboratório, estádio, PMCs, 8 ginásios, pokémon selvagens, itens, treinadores NPC e ovos:

```bash
python -m src.gerador <n_vertices> <n_arestas> [opções]
```

Exemplo (60 vértices, 300 arestas):
```bash
python -m src.gerador 60 300
```

Opções disponíveis:

| Opção | Padrão | Descrição |
|---|---|---|
| `--peso-min N` | 1 | Peso mínimo de uma aresta |
| `--peso-max N` | 20 | Peso máximo de uma aresta |
| `--seed N` | aleatório | Semente para reprodutibilidade |
| `--saida ARQUIVO` | `mapas/gerado.txt` | Onde salvar o mapa gerado |

Restrições: `n_vertices >= 11` (laboratório + estádio + pelo menos 1 PMC + 8 ginásios) e `n_arestas >= n_vertices - 1`.

Depois de gerado, jogue com:
```bash
python -m src.main --mapa gerado.txt
```

## Como jogar

Ao iniciar, você informa seu nome e escolhe um dos três pokémon iniciais oferecidos (ou digita `n` para recusar os três e receber um aleatório do laboratório).

A cada turno, o jogo mostra sua posição atual, os vizinhos alcançáveis, seu time e os comandos disponíveis naquele momento. Comandos entre `< >` esperam um argumento.

| Comando | O que faz |
|---|---|
| `ir <vértice>` | Move para um vértice vizinho (gasta tempo igual ao peso da aresta) |
| `mapa` | Mostra os vizinhos do vértice atual e o custo até eles |
| `status` | Mostra seu time, XP, insígnias, itens, ovos e pokémon em tratamento no PMC |
| `poi` | Mostra o ponto mais próximo de cada tipo (ginásio, PMC, estádio, pokémon selvagem, item, treinador, líder, ovo) e a rota até lá |
| `pegar` | Pega um item (erva) no vértice atual, se houver |
| `pegar ovo` | Pega um ovo no vértice atual, se houver (a espécie só é revelada quando ele chocar) |
| `usar <item>` | Usa um item do inventário (ex.: `usar erva`) |
| `desafiar` | Desafia um treinador NPC ou líder de ginásio presente no vértice atual para uma batalha |
| `capturar` | Tenta capturar um pokémon selvagem presente no vértice atual |
| `deixar <índice_pokemon>` | Deixa um pokémon muito machucado (HP < 5) em tratamento no PMC atual (índice visto em `status`) |
| `retirar` | Recolhe do PMC atual os pokémon já tratados |
| `sair` | Encerra o jogo |

Observações importantes:

- **Batalhas contra outro treinador** exigem pelo menos 3 pokémon conscientes; **capturar pokémon selvagem** exige só 1. Nenhuma das duas é permitida no laboratório nem em um PMC.
- Ao **derrotar um líder de ginásio**, você ganha a insígnia daquele ginásio. É preciso 8 insígnias distintas (ou todas as existentes na região, se ela tiver 8 ginásios ou menos) para se inscrever na Liga.
- **Vencer** exige chegar ao estádio já classificado, dentro do prazo mostrado no início da partida (o relógio avança conforme você se move e batalha).
- Treinadores NPC podem, por conta própria, desafiar você ao acaso quando vocês se encontram no mesmo vértice.
- Você pode carregar no máximo 6 pokémon ativos (mais ovos ainda não chocados, até 7 no total); pokémon excedentes vão para o laboratório.

## Estrutura do projeto

```
src/
  main.py            # ponto de entrada do jogo
  gerador.py          # gerador de mapas aleatórios
  grafo.py             # leitura do grafo, BFS, Floyd-Warshall
  relogio.py            # relógio/prazo da jornada
  entities/              # Pokemon, Treinador, LiderGinasio, Mundo, tipos
  ui/                      # exibição (texto na tela) e comandos do jogador
  interface.py               # laço principal de comandos
mapas/
  exemplo.txt          # mapa pequeno de exemplo (9 vértices)
  gerado.txt            # mapa gerado (60 vértices)
```

## Formato do arquivo de mapa

Um mapa é um arquivo de texto com 4 seções:

```
GRAFO
<n_vertices> <n_arestas>
<u> <v> <peso>
...

LOCAIS
LAB <vértice>
ESTADIO <vértice>
PMC <vértice> <vértice> ...
GINASIO <vértice> <vértice> ...

POPULACAO
TREINADORES <quantidade>
POKEMON <quantidade>
ITENS <quantidade>
OVOS <quantidade>

EVOLUCOES
<fase1> <fase2> <fase3>
...
```

O prazo de inscrição na Liga é sorteado automaticamente entre 10× e 15× a soma dos pesos de todas as arestas — não precisa (nem deve) ser informado no arquivo.
