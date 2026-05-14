import datetime
import json
from dataclasses import dataclass, asdict
from dacite import from_dict, Config, UnexpectedDataError, WrongTypeError, MissingValueError
import uuid

from niveau.definitions import Sujet


@dataclass
class ComposanteDTO:
    type: int  # enum
    resistance: float
    tension: float


@dataclass
class NoeudDTO:
    pos: list[float]  # [x, y]
    voltage: float
    voisins: list[tuple[int, int]]  # (fil_index, noeud_index)


@dataclass
class FilDTO:
    points: list[list[float]]  # [[x, y], [x, y], ...]
    composantes: list[ComposanteDTO]
    tension: float
    resistance: float
    # indices des noeuds dans le circuit (references temporaires pour la serialisation)
    # une meilleur facon de faire serait d'utiliser des IDs uniques (noeud.id / fil.id / composante.id)
    # pour eviter toute dependance a l'ordre des listes
    noeuds: list[int] | None


@dataclass
class CircuitDTO:
    id: str
    nom: str
    fils: list[FilDTO]
    noeuds: list[NoeudDTO]
    derniere_sauvegarde: int


@dataclass
class NiveauDTO:
    ohm: list[int]
    kirchoff: list[int]
    resistance: list[int]


@dataclass
class SaveDTO:
    circuits: list[CircuitDTO]
    niveau: NiveauDTO


class Sauvegarde:
    def __init__(self):
        try:
            # Dacite valide automatiquement la structure des données (types + clés/valeurs)
            self.data = from_dict(SaveDTO, read("data.json"), config=Config(strict=True, check_types=True))

            # Validation manuelle du nombre de niveaux
            niveau = self.data.niveau
            if len(niveau.ohm) != 5 or len(niveau.kirchoff) != 5 or len(niveau.resistance) != 5:
                raise ValueError("Données invalides: chaque progression doit contenir exactement 5 niveaux")
        except (FileNotFoundError, ValueError, WrongTypeError, MissingValueError, UnexpectedDataError):
            # Création d'un état par défaut si la sauvegarde n'existe pas ou malformé
            self.initialize_defaults()

    def initialize_defaults(self):
        default_data = SaveDTO([], NiveauDTO(
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ))
        write("data.json", asdict(default_data))
        self.data = default_data

    def progression_niveaux(self, sujet: Sujet) -> list[int]:
        return getattr(self.data.niveau, sujet.name.lower())

    def update_niveau(self, sujet: Sujet, niveau: int, point: int):
        progression = getattr(self.data.niveau, sujet.name.lower())
        current_points = progression[niveau - 1]
        if current_points < point:
            progression[niveau - 1] = point
            write("data.json", asdict(self.data))

    def delete_circuit(self, id: str):
        for circuit in self.data.circuits:
            if circuit.id == id:
                self.data.circuits.remove(circuit)
                write("data.json", asdict(self.data))
                break

    def get_circuit(self, id: str) -> CircuitDTO | None:
        for circuit in self.data.circuits:
            if circuit.id == id:
                return circuit
        return None

    def get_circuits(self) -> list[CircuitDTO]:
        return self.data.circuits

    # Retourne l'id générer
    def creation_circuit_libre(self, nom: str) -> str:
        id = str(uuid.uuid4())
        date = int(datetime.datetime.now(datetime.UTC).timestamp())
        nouveau_circuit = CircuitDTO(id, nom, [], [], date)

        self.data.circuits.append(nouveau_circuit)
        write("data.json", asdict(self.data))
        return id

    def modifie_circuit(self, id: str, fils: list[FilDTO], noeuds: list[NoeudDTO]) -> bool:
        for idx, circuit in enumerate(self.data.circuits):
            if circuit.id != id:
                continue

            date = int(datetime.datetime.now(datetime.UTC).timestamp())
            circuit.derniere_sauvegarde = date
            circuit.fils = fils
            circuit.noeuds = noeuds
            write("data.json", asdict(self.data))
            return True

        return False


def write(path: str, data: dict):
    with open(path, "w") as file:
        json.dump(data, file)


def read(path: str):
    with open(path, "r") as file:
        return json.loads(file.read())
