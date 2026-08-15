from time import sleep

import requests
import json

CAMINHO = '../pokemons_1.json'

types = {}


def _limpar_pokemon(table, nomes_tipos):
    return {
        'id': table['id'],
        'name': table['name'],
        'tipos': nomes_tipos,
        'stats': table['stats'],
    }


def _limpar_tipo(dados_tipo):
    return {
        'name': dados_tipo['name'],
        'damage_relations': dados_tipo['damage_relations'],
    }


def baixar_pokemons():
    url_base = 'https://pokeapi.co/api/v2/pokemon/'
    with open(CAMINHO, mode='r', encoding='utf8') as file:
        dados = json.load(file)

    pokemons_1a_geracao = dados['pokemons']
    types.update(dados['tipos'])

    ids_baixados = {pokemon['id'] for pokemon in pokemons_1a_geracao}

    for i in range(1, 152):
        if i in ids_baixados:
            continue
        print(f"Buscando pokemon id {i}")
        data = requests.get(url_base + str(i)).text
        table = json.loads(data)
        nome = table['name']
        print(f"Baixado dados do pokemon {nome}")

        nomes_tipos = []
        for slot in table['types']:
            tipo = slot['type']['name']
            if tipo not in types:
                data_tipo = requests.get(slot['type']['url']).text
                dados_tipo = json.loads(data_tipo)
                types[tipo] = _limpar_tipo(dados_tipo)
            nomes_tipos.append(tipo)

        pokemons_1a_geracao.append(_limpar_pokemon(table, nomes_tipos))
        with open(CAMINHO, mode='w', encoding='utf8') as file:
            file.write(json.dumps({'pokemons': pokemons_1a_geracao, 'tipos': types}))
        sleep(2)


if __name__ == "__main__":
    baixar_pokemons()
