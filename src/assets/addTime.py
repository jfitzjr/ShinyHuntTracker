import json

pokemonDictionary = {}

with open('CountSave.json', 'r', encoding="utf-8") as getSave:
    pokemonDictionary = json.loads(getSave.read())

newDictionary = {}

for pokemon in pokemonDictionary:
    newDictionary[pokemon] = [pokemonDictionary[pokemon], 0]

with open('CountSaveNew.json', 'w', encoding='utf-8') as f:
    json.dump(newDictionary, f, indent=4, ensure_ascii=False)