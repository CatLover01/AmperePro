from collections.abc import Callable
from enum import Enum

from PySide6.QtGui import QPixmap, Qt, QTransform
from PySide6.QtWidgets import QGraphicsPixmapItem
from abc import ABC


class Cote(Enum):
    Gauche = 1
    Droite = 2
    Haut = 3
    Bas = 4


# Type de composante dont nous supportons
class Type(Enum):
    Batterie = 1
    LED = 2
    Resistor = 3
    Diode = 4
    Interrupteur = 5
    Voltmetre = 6
    Amperemetre = 7


# Description will be used for the documentation within the app
class ComposanteBase(ABC):
    def __init__(self, type: Type, nom: str, image_toolbar: str, image_circuit: str, scale: int,
                 description: str):
        self.type = type
        self.nom = nom
        self.description = description
        self.image_toolbar = image_toolbar
        self.image_circuit = image_circuit
        self.scale = scale


class Batterie(ComposanteBase):
    def __init__(self):
        super().__init__(Type.Batterie, "Batterie", "images/toolbar/batterie.jpg",
                         "images/circuit/batterie.png", 40, "A faire...")


class LED(ComposanteBase):
    def __init__(self):
        super().__init__(Type.LED, "LED", "images/toolbar/LED.webp", "images/circuit/LED.png", 68,
                         "- Diode qui émet de la lumière quand le courant passe dans le bon sens"
                         "- Elle a une polarité : anode (+) et cathode (-). \n"
                         "- On met souvent une résistance en série une LED pour évitr trop de courant"
                         )


class Resistor(ComposanteBase):
    def __init__(self):
        super().__init__(Type.Resistor, "Résisteur", "images/toolbar/resistor.jpg",
                         "images/circuit/resistor.png", 56,
                         "- Composante qui limite le courant. \n"
                         "- Unité : Ohms (Ω) \n"
                         "- Loi d'Ohm : V = R · I \n"
                         "- Baisse l'intensité du courant. \n"
                         "- V en Volts, R en Ohms, I en Ampères"
                         )


class Diode(ComposanteBase):
    def __init__(self):
        super().__init__(Type.Diode, "Diode", "images/toolbar/diode.jpg", "images/circuit/diode.png", 30,
                         "- Laisse passer le courant dans un seul sens ( en résumé ). \n"
                         "- Polarité importante. \n"
                         "- Utile pour boquer le retour de courant ou redresser un signal "
                         )


class Interrupteur(ComposanteBase):
    def __init__(self):
        super().__init__(Type.Interrupteur, "Interrupteur", "images/toolbar/interrupteur.jpg",
                         "images/circuit/interrupteur_ouvert.png", 45,
                         "- Sert à ouvrir ou fermer un circuit. \n"
                         "- Ouvert : le courant ne passe pas. \n"
                         "- Fermé : le courant peut passer ( si le circuit est complet )."
                         )


class Voltmetre(ComposanteBase):
    def __init__(self):
        super().__init__(Type.Voltmetre, "Voltmètre", "images/toolbar/voltmetre.jpg",
                         "images/circuit/voltmetre.png", 40,
                         "- Sert à mesurer la tension (différence de potentiel) entre deux points. \n "
                         "- Unité : Volt (V). \n "
                         "- Se branche en parallèle aux bornes de la composante dont on veut mesurer la tension. \n"
                         "- Idéalement, la résistance dans le voltmètre est très grande pour ne pas déranger le circuit."
                         )


class Amperemetre(ComposanteBase):
    def __init__(self):
        super().__init__(Type.Amperemetre, "Ampèremètre", "images/toolbar/amperemetre.jpg",
                         "images/circuit/amperemetre.png", 40,
                         "- Sert à mesurer le courant électrique qui traverse une branche. \n"
                         "- Unité : Ampères (A). \n "
                         "- Se branche en série dans la branche où on veut mesurer le courant \n"
                         "- Idéalement, la résistance dans l'ampèremètre est très faible."
                         )


# Classe des item_instance des composantes
class Item(QGraphicsPixmapItem):
    def __init__(self, pixmap, callback: Callable):
        super().__init__(pixmap)
        self.callback = callback

    # appel la fonction clicked de sa composante parente
    def mousePressEvent(self, event):
        self.callback()


class Composante:
    def __init__(self, composante: Type):
        self.base = toolbar_composantes[composante]
        self.item_instance = None
        self.cote: Cote | None = None

        match composante:
            case Type.Interrupteur:
                self.ouvert = True
                self.image_ferme = "images/circuit/interrupteur_ferme.png"

    def ajouter_pixmap(self) -> QGraphicsPixmapItem:
        pixmap = QPixmap(self.base.image_circuit)
        pixmap_scaled = pixmap.scaled(self.base.scale, self.base.scale, Qt.AspectRatioMode.KeepAspectRatio)
        pixmap_item = Item(pixmap_scaled, self.clicked)

        pixmap_item.setZValue(1)
        self.item_instance = pixmap_item

        # Retourner pour l'ajouter à la scène
        return pixmap_item

    def clicked(self):
        if self.item_instance is None:
            return

        match self.base.type:
            case Type.LED | Type.Diode:
                transform = QTransform()
                transform.scale(-1, 1)
                pixmap_flipped = self.item_instance.pixmap().transformed(transform)
                self.item_instance.setPixmap(pixmap_flipped)

            case Type.Interrupteur:
                if self.ouvert:
                    image = self.image_ferme
                else:
                    # Image circuit est ouvert par défault dans la classe de base
                    image = self.base.image_circuit

                self.ouvert = not self.ouvert

                pixmap = QPixmap(image)
                pixmap_scaled = pixmap.scaled(self.base.scale, self.base.scale, Qt.AspectRatioMode.KeepAspectRatio)
                self.item_instance.setPixmap(pixmap_scaled)


toolbar_composantes = {
    Type.Batterie: Batterie(),
    Type.LED: LED(),
    Type.Resistor: Resistor(),
    Type.Diode: Diode(),
    Type.Interrupteur: Interrupteur(),
    Type.Voltmetre: Voltmetre(),
    Type.Amperemetre: Amperemetre()}
