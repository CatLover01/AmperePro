import json
from json import JSONDecodeError
from dataclasses import dataclass, asdict


@dataclass
class CircuitLibre:
    id: str
    nom: str
    matrix: list
    derniere_sauvegarde: int

class Sauvegarder:
    def __init__(self):
        try:
            # Données utilisateur: niveau atteint, circuits personnalisés
            # Format attendu: {"niveau": int, "circuits_libre": list}
            self.data = read("data.json")
        except FileNotFoundError | JSONDecodeError:
            # Création d'un état par défaut si la sauvegarde n'existe pas ou malformé
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

    def ajout_circuit_libre(self, nouveau_circuit: CircuitLibre):
        circuit_dict = {nouveau_circuit.id: asdict(nouveau_circuit)}
        self.data["circuits-libre"].append(circuit_dict)
        write("data.json" , self.data)

    # Retourne faux si le circuit modifier n'existe pas
    def modifie_circuit(self, circuit_modifier: CircuitLibre) -> bool:
        for idx, circuit in enumerate(self.data["circuits-libre"]):
            if circuit.id != circuit_modifier.id: continue

            self.data["circuits-libre"][idx] = asdict(circuit_modifier)
            write("data.json" , self.data)
            return True

        return False


def write(path: str, data: dict):
    with open(path, "w") as file:
        json.dump(data, file)


def read(path: str):
    with open(path, "r") as file:
        return json.loads(file.read())