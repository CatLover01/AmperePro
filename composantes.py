from enum import Enum
from typing import override
from abc import ABC

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QDoubleSpinBox


class Type(Enum):
    Batterie = 1
    LED = 2
    Resistor = 3
    Diode = 4
    Interrupteur = 5
    Voltmetre = 6
    Amperemetre = 7


class Composante(ABC):
    def __init__(self, type: Type, nom: str, image_toolbar: str, image_circuit: str,
                 description: str, tension: int = 0, resistance: int = 0):
        self.type = type
        self.nom = nom
        self.description = description
        self.image_toolbar = image_toolbar
        self.image_circuit = image_circuit
        self.points_fil = []
        self.poins_cote = []
        self.items = []
        self.image_item = None

        # Fait partie de chaque composante pour pouvoir faire les calculs plus tard
        self.tension = tension
        self.resistance = resistance

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, types):
        self._type = types

    @property
    def nom(self):
        return self._nom

    @nom.setter
    def nom(self, noms):
        self._nom = noms

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, descriptions):
        self._description = descriptions

    @property
    def image_toolbar(self):
        return self._image_toolbar

    @image_toolbar.setter
    def image_toolbar(self, toolbar):
        self._image_toolbar = toolbar

    @property
    def image_circuit(self):
        return self._image_circuit

    @image_circuit.setter
    def image_circuit(self, circuit):
        self._image_circuit = circuit

    @property
    def tension(self):
        return self._tension

    @tension.setter
    def tension(self, tension):
        self._tension = tension

    @property
    def resistance(self):
        return self._resistance

    @resistance.setter
    def resistance(self, resistance):
        self._resistance = resistance

    # Fonction pouvant être redéfinie dans chaque composante
    # La taille de la grille est fournie pour conserver l'échelle lors d'un changement de pixmap
    def clique(self, taille_grid: int):
        pass


class Batterie(Composante):
    def __init__(self):
        super().__init__(Type.Batterie, "Batterie", "images/circuit/batterie.png",
                         "images/circuit/batterie.png",
                         "- Fournit l’énergie électrique au circuit. <br>"
                         "- Crée une différence de potentiel (tension). <br>"
                         "- Possède une borne positive (+) et négative (-). <br>"
                         "- Permet au courant de circuler dans le circuit.",
                         10
                         )

    # Ouvre une fenetre pour changer la tension
    @override
    def clique(self, _):
        fenetre = QDialog()
        fenetre.setWindowTitle("Batterie")
        layout_principal = QVBoxLayout()
        fenetre.setLayout(layout_principal)
        sous_layout = QHBoxLayout()
        layout_principal.addLayout(sous_layout)

        texte = QLabel("Tension (V): ")
        sous_layout.addWidget(texte)
        # on veut que la tension inscrite soit un nombre entre 0 et 1000 (tensions réalistes) avec une décimale de précision
        nombre = QDoubleSpinBox()
        nombre.setRange(0, 999.9)
        nombre.setDecimals(1)

        nombre.setValue(self.tension)
        sous_layout.addWidget(nombre)

        # boutons ok et annuler
        sous_layout_deux = QHBoxLayout()
        layout_principal.addLayout(sous_layout_deux)
        bouton_ok = QPushButton("OK")
        bouton_ok.clicked.connect(fenetre.accept)
        sous_layout_deux.addWidget(bouton_ok)
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(fenetre.reject)
        sous_layout_deux.addWidget(bouton_annuler)
        verifier_return = fenetre.exec()

        # si la valeur est modifiée, on retourne la liste initiale avec valeur modifiée
        if verifier_return == QDialog.DialogCode.Accepted and self.tension != nombre.value():
            ancienne_tension = self.tension
            self.tension = nombre.value()
            return ancienne_tension, self.tension
        else:
            return None


class LED(Composante):
    def __init__(self):
        super().__init__(Type.LED, "LED", "images/circuit/led.png",
                         "images/circuit/led.png",
                         "- Diode qui émet de la lumière quand le courant passe dans le bon sens <br>"
                         "- Elle a une polarité : anode (+) et cathode (-). <br>"
                         "- On met souvent une résistance en série une LED pour évitr trop de courant"
                         )


class Resistor(Composante):
    def __init__(self):
        super().__init__(Type.Resistor, "Résistor", "images/circuit/resistor.png",
                         "images/circuit/resistor.png",
                         "- Composante qui limite le courant. <br>"
                         "- Unité : Ohms (Ω) <br>"
                         "- Loi d'Ohm : V = R · I <br>"
                         "- Baisse l'intensité du courant. <br>"
                         "- V en Volts, R en Ohms, I en Ampères",
                         0, 1000
                         )

    # ouvre un dialog pour changer la resistance
    @override
    def clique(self, _):
        fenetre = QDialog()
        fenetre.setWindowTitle("Résistor")
        layout_principal = QVBoxLayout()
        fenetre.setLayout(layout_principal)
        sous_layout = QHBoxLayout()
        layout_principal.addLayout(sous_layout)

        texte = QLabel("Résistance (V): ")
        sous_layout.addWidget(texte)
        # on veut que la tension inscrite soit un nombre entre 0 et 1000 (tensions réalistes)
        # avec une décimale de précision
        nombre = QDoubleSpinBox()
        nombre.setRange(0, 9999999.9)
        nombre.setDecimals(1)

        nombre.setValue(self.resistance)
        sous_layout.addWidget(nombre)

        # boutons ok et annuler
        sous_layout_deux = QHBoxLayout()
        layout_principal.addLayout(sous_layout_deux)
        bouton_ok = QPushButton("OK")
        bouton_ok.clicked.connect(fenetre.accept)
        sous_layout_deux.addWidget(bouton_ok)
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(fenetre.reject)
        sous_layout_deux.addWidget(bouton_annuler)
        verifier_return = fenetre.exec()

        # si la valeur est modifiée, on retourne la liste initiale avec valeur modifiée
        if verifier_return == QDialog.DialogCode.Accepted and self.resistance != nombre.value():
            ancienne_resistance = self.resistance
            self.resistance = nombre.value()
            return ancienne_resistance, self.resistance
        else:
            return None


class Diode(Composante):
    def __init__(self):
        super().__init__(Type.Diode, "Diode", "images/circuit/diode.png",
                         "images/circuit/diode.png",
                         "- Laisse passer le courant dans un seul sens ( en résumé ). <br>"
                         "- Polarité importante. <br>"
                         "- Utile pour bloquer le retour de courant ou redresser un signal "
                         )


class Interrupteur(Composante):
    def __init__(self):
        super().__init__(Type.Interrupteur, "Interrupteur", "images/circuit/interrupteur_ouvert.png",
                         "images/circuit/interrupteur_ouvert.png",
                         "- Sert à ouvrir ou fermer un circuit. <br>"
                         "- Ouvert : le courant ne passe pas. <br>"
                         "- Fermé : le courant peut passer ( si le circuit est complet )."
                         )

        self.ouvert = True

    @override
    def clique(self, taille_grid):
        if self.ouvert:
            image_path = "images/circuit/interrupteur_ferme.png"
        else:
            # Image circuit est ouvert par défault dans la classe de base
            image_path = self.image_circuit

        self.ouvert = not self.ouvert

        pixmap = QPixmap(image_path)
        pixmap_scaled = pixmap.scaled(taille_grid * 2, taille_grid * 2)
        self.image_item.setPixmap(pixmap_scaled)


class Voltmetre(Composante):
    def __init__(self):
        super().__init__(Type.Voltmetre, "Voltmètre", "images/circuit/voltmetre.png",
                         "images/circuit/voltmetre.png",
                         "- Sert à mesurer la tension (différence de potentiel) entre deux points. <br> "
                         "- Unité : Volt (V). <br> "
                         "- Se branche en parallèle aux bornes de la composante dont on veut mesurer la tension. <br>"
                         "- Idéalement, la résistance dans le voltmètre est très grande pour ne pas affecter le circuit."
                         )

        self.voltage = 0

    @override
    def clique(self, _):
        fenetre = QDialog()
        fenetre.setWindowTitle("Voltmètre")
        fenetre.setFixedSize(240, 350)

        # image qui simule le voltmètre
        image = QLabel(parent=fenetre)
        pixmap = QPixmap("images/interface/voltmetre.png")
        image.setPixmap(pixmap)
        image.setScaledContents(True)
        image.setGeometry(QRect(0, 110, 240, 270))

        # on simule l'affichage du voltmètre
        fond = QLabel(parent=fenetre)
        fond.setStyleSheet("QLabel { background-color : #9e9a75; }")
        fond.setGeometry(4, 0, 232, 110)
        voltage = str(self.voltage)
        texte = QLabel(voltage, parent=fenetre)
        texte.setStyleSheet("font-size: 50pt; color: #000000")
        texte.setGeometry(4, 0, 232, 110)
        texte.setAlignment(Qt.AlignmentFlag.AlignCenter)
        """ Affiche un V dans le voltmetre (a mettre a lamperemetre aussi)
        texte_volt = QLabel("V", parent=fenetre)
        texte_volt.setStyleSheet("font-size: 50pt; color: #363535")
        texte_volt.setGeometry(4, 0, 232, 110)
        texte_volt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        """
        texte.raise_()
        fenetre.exec()


class Amperemetre(Composante):
    def __init__(self):
        super().__init__(Type.Amperemetre, "Ampèremètre", "images/circuit/amperemetre.png",
                         "images/circuit/amperemetre.png",
                         "- Sert à mesurer le courant électrique qui traverse une branche. <br>"
                         "- Unité : Ampères (A). <br> "
                         "- Se branche en série dans la branche où on veut mesurer le courant <br>"
                         "- Idéalement, la résistance dans l'ampèremètre est très faible."
                         )

        self.amperage = 0

    @override
    def clique(self, _):
        fenetre = QDialog()
        fenetre.setWindowTitle("Ampèremètre")
        fenetre.setFixedSize(240, 350)

        # image qui simule l'ampèremètre
        image = QLabel(parent=fenetre)
        pixmap = QPixmap("images/interface/amperemetre.png")
        image.setPixmap(pixmap)
        image.setScaledContents(True)
        image.setGeometry(QRect(0, 110, 240, 270))

        # on simule l'affichage du voltmètre
        fond = QLabel(parent=fenetre)
        fond.setStyleSheet("QLabel { background-color : #9e9a75; }")
        fond.setGeometry(4, 0, 232, 110)
        amperage = str(self.amperage)
        texte = QLabel(amperage, parent=fenetre)
        texte.setStyleSheet("font-size: 50pt; color: #000000")
        texte.setGeometry(4, 0, 232, 110)
        texte.setAlignment(Qt.AlignmentFlag.AlignCenter)

        texte.raise_()
        fenetre.exec()


toolbar_composantes = {
    Type.Batterie: Batterie(),
    Type.LED: LED(),
    Type.Resistor: Resistor(),
    Type.Diode: Diode(),
    Type.Interrupteur: Interrupteur(),
    Type.Voltmetre: Voltmetre(),
    Type.Amperemetre: Amperemetre()}
