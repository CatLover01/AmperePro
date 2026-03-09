import json

#bd de base
bd = {
    "Circuits": [
        {"Nom": "JM L\n'électricité", "Données": ["A", "B", "C"], "dernière sauvegarde" : "19 avril 1962"}
        ],}

# en JSON
with open("bd.json", "w", encoding = "UTF-8") as f:
    json.dump(bd, f, indent = 4)
