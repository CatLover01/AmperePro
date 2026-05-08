import datetime
import json
from json import JSONDecodeError
from dataclasses import dataclass, asdict
from dacite import from_dict
import uuid

from niveau.definitions import Sujet


@dataclass
class CircuitLibre:
    id: str
    nom: str
    matrix: list
    derniere_sauvegarde: int


class Sauvegarde:
    def __init__(self):
        try:
            # Données utilisateur: niveau atteint, circuits personnalisés
            self.data = read("data.json")
        except (FileNotFoundError, JSONDecodeError):
            # Création d'un état par défaut si la sauvegarde n'existe pas ou malformé
            self.initialize_defaults()

    def initialize_defaults(self):
        default_data = {"circuits-libre": [], "niveau": {
            Sujet.Ohm.value: [0, 0, 0, 0, 0],
            Sujet.Kirchoff.value: [0, 0, 0, 0, 0],
            Sujet.Resistance.value: [0, 0, 0, 0, 0]
        }}
        write("data.json", default_data)
        self.data = default_data

    def progression_niveaux(self, sujet: Sujet) -> list[int]:
        try:
            return self.data["niveau"][sujet.value]
        except:
            # Data malformé
            self.initialize_defaults()
            return [0, 0, 0, 0, 0]

    def update_niveau(self, sujet: Sujet, niveau: int, point: int):
        current_points = self.data["niveau"][sujet.value][niveau - 1]
        if current_points < point:
            self.data["niveau"][sujet.value][niveau - 1] = point
            write("data.json", self.data)

    def delete_circuit(self, id: str):
        for circuit in self.data["circuits-libre"]:
            if circuit["id"] == id:
                self.data["circuits-libre"].remove(circuit)
                write("data.json", self.data)
                break

    def circuits_libre(self) -> list[CircuitLibre]:
        # Retourne la liste des circuits libres sauvegardés par l'utilisateur.
        try:
            circuits = []
            for circuit in self.data["circuits-libre"]:
                circuits.append(from_dict(CircuitLibre, circuit))
            return circuits
        except:
            # Data malformé
            self.initialize_defaults()
            return []

    # Retourne l'id générer
    def creation_circuit_libre(self, nom: str) -> str:
        id = str(uuid.uuid4())
        date = int(datetime.datetime.now(datetime.UTC).timestamp())
        nouveau_circuit = CircuitLibre(id, nom, [], date)

        self.data["circuits-libre"].append(asdict(nouveau_circuit))
        write("data.json", self.data)
        return id

    def modifie_circuit(self, id: str, mat: list) -> bool:
        for idx, circuit in enumerate(self.data["circuits-libre"]):
            if circuit["id"] != id: continue

            date = int(datetime.datetime.now(datetime.UTC).timestamp())
            circuit["date"] = date
            circuit["matrix"] = mat
            write("data.json", self.data)
            return True

        return False


def write(path: str, data: dict):
    with open(path, "w") as file:
        json.dump(data, file)


def read(path: str):
    with open(path, "r") as file:
        return json.loads(file.read())
