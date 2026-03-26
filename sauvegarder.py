import json


class Sauvegarder:
    def __init__(self):
        try:
            # Données utilisateur: niveau atteint, circuits personnalisés
            # Format attendu: {"niveau": int, "circuits_libre": list}
            self.data = read("data.json")
        except FileNotFoundError:
            # Création d'un état par défaut si la sauvegarde n'existe pas
            default = {"niveau": 1, "circuits-libre": []}
            write("data.json", default)
            self.data = default

        # Chargement des niveaux préconstruits (fichier requis)
        #self.__niveaux = read("niveaux.json")

    def niveaux_disponibles(self):
        # Retourne la liste des niveaux disponibles (préconstruits).
        return self.__niveaux["niveaux"]

    def debloque_niveau(self) -> int:
        # Débloque un niveau supplémentaire et met à jour la sauvegarde.
        self.data["niveau"] = self.data["niveau"] + 1
        write("data.json", self.data)
        return self.data["niveau"]

    def circuits_libre(self):
        # Retourne la liste des circuits libres sauvegardés par l'utilisateur.
        return self.data["circuits_libre"]


def write(path: str, data: dict):
    with open(path, "w") as file:
        json.dump(data, file)


def read(path: str):
    with open(path, "r") as file:
        return json.loads(file.read())