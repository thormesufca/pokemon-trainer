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
