TIPOS_POR_POKEMON = {
    'Bulbasaur': ['grass', 'poison'],
    'Ivysaur': ['grass', 'poison'],
    'Venusaur': ['grass', 'poison'],
    'Charmander': ['fire'],
    'Charmeleon': ['fire'],
    'Charizard': ['fire', 'flying'],
    'Squirtle': ['water'],
    'Wartortle': ['water'],
    'Blastoise': ['water'],
    'Pikachu': ['electric'],
    'Raichu': ['electric'],
    'Geodude': ['rock', 'ground'],
    'Graveler': ['rock', 'ground'],
    'Golem': ['rock', 'ground'],
    'Gastly': ['ghost', 'poison'],
    'Haunter': ['ghost', 'poison'],
    'Gengar': ['ghost', 'poison'],
    'Magikarp': ['water'],
    'Gyarados': ['water', 'flying'],
    'Abra': ['psychic'],
    'Kadabra': ['psychic'],
    'Alakazam': ['psychic'],
}


def tipos_de(nome):
    """Lista de tipos elementais de uma espécie"""
    return TIPOS_POR_POKEMON.get(nome, [])

RELACOES_TIPO = {
    'electric': {'forte': ['flying', 'water'], 'fraco': ['electric', 'grass'], 'imune': ['ground']},
    'fire':     {'forte': ['grass'], 'fraco': ['fire', 'rock', 'water'], 'imune': []},
    'flying':   {'forte': ['grass'], 'fraco': ['electric', 'rock'], 'imune': []},
    'ghost':    {'forte': ['ghost', 'psychic'], 'fraco': [], 'imune': []},
    'grass':    {'forte': ['ground', 'rock', 'water'], 'fraco': ['fire', 'flying', 'grass', 'poison'], 'imune': []},
    'ground':   {'forte': ['electric', 'fire', 'poison', 'rock'], 'fraco': ['grass'], 'imune': ['flying']},
    'poison':   {'forte': ['grass'], 'fraco': ['ghost', 'ground', 'poison', 'rock'], 'imune': []},
    'psychic':  {'forte': ['poison'], 'fraco': ['psychic'], 'imune': []},
    'rock':     {'forte': ['fire', 'flying'], 'fraco': ['ground'], 'imune': []},
    'water':    {'forte': ['fire', 'ground', 'rock'], 'fraco': ['grass', 'water'], 'imune': []},
}


def multiplicador_tipo(tipo_atacante, tipos_defensor):
    """Produto do multiplicador de tipo_atacante contra cada tipo em tipos_defensor"""
    relacao = RELACOES_TIPO.get(tipo_atacante, {})
    forte = relacao.get('forte', [])
    fraco = relacao.get('fraco', [])
    imune = relacao.get('imune', [])

    mult = 1.0
    for tipo in tipos_defensor:
        if tipo in imune:
            mult *= 0.0
        elif tipo in forte:
            mult *= 2.0
        elif tipo in fraco:
            mult *= 0.5
    return mult
