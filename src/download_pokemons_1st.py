from time import sleep

import requests
import json

url_base = 'https://pokeapi.co/api/v2/pokemon-species/'

with open('../pokemons_1.json', mode='r', encoding='utf8') as file:
    pokemons_1a_geracao = json.load(file)

for i in range(1, 152):
    if str(i) in pokemons_1a_geracao:
        continue
    print(f"Buscando pokemon id {i}")
    data = requests.get(url_base + str(i)).text
    table = json.loads(data)
    names = table['names']
    for name in names:
        if name['language']['name'] == 'en':
            nome = name['name']
            print(f"Baixado dados do pokemon {nome}")
            break

    pokemons_1a_geracao[i] = data
    with open('../pokemons_1.json', mode='w', encoding='utf8') as file:
        file.write(json.dumps(pokemons_1a_geracao))
    sleep(2)
