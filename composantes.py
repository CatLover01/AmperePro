from enum import Enum
from typing import override
from abc import ABC

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPixmap, Qt, QFontMetrics
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDoubleSpinBox

from sauvegarde import ComposanteDTO


class TypeComposante(Enum):
    Batterie = 1
    LED = 2
    Resistor = 3
    Diode = 4
    Interrupteur = 5
    Voltmetre = 6
    Amperemetre = 7


class Composante(ABC):
    def __init__(self, type_composante: TypeComposante, nom: str, image_toolbar: str, image_circuit: str,
                 description: str, tension: float = 0, resistance: float = 0):
        self._type = type_composante
        self._nom = nom
        self._description = description
        self._image_toolbar = image_toolbar
        self._image_circuit = image_circuit
        self.points_fil = []
        self.points_cote = []
        self.items = []
        self.image_item = None
        self.fil = None

        # Fait partie de chaque composante pour pouvoir faire les calculs plus tard
        self.tension = tension
        self.resistance = resistance

    @property
    def type(self):
        return self._type

    @property
    def nom(self):
        return self._nom

    @property
    def description(self):
        return self._description

    @property
    def image_toolbar(self):
        return self._image_toolbar

    @property
    def image_circuit(self):
        return self._image_circuit

    @property
    def tension(self) -> int:
        return self._tension

    @tension.setter
    def tension(self, tension: int):
        self._tension = tension

    @property
    def resistance(self) -> int:
        return self._resistance

    @resistance.setter
    def resistance(self, resistance: int):
        self._resistance = resistance

    # Fonction pouvant être redéfinie dans chaque composante
    # La taille de la grille est fournie pour conserver l'échelle lors d'un changement de pixmap
    def double_clique_gauche(self, taille_grid: int) -> None | int:
        pass

    def tourner(self):
        self.image_item.setRotation(self.image_item.rotation() + 180)

    def nettoyer(self):
        self.items = []
        self.points_fil = []
        self.points_cote = []

    def to_dto(self) -> ComposanteDTO:
        return ComposanteDTO(self.type.value, self.tension, self.resistance)

    @classmethod
    def from_dto(cls, dto: ComposanteDTO):
        composante = toolbar_composantes[TypeComposante(dto.type)]()
        composante.tension = dto.tension
        composante.resistance = dto.resistance
        return composante


class Batterie(Composante):
    def __init__(self):
        super().__init__(TypeComposante.Batterie, "Batterie", "images/circuit/batterie.png",
                         "images/circuit/batterie.png",
                         "- Fournit l’énergie électrique au circuit. <br>"
                         "- Crée une différence de potentiel (tension). <br>"
                         "- Possède une borne positive (+) et négative (-). <br>"
                         "- Permet au courant de circuler dans le circuit.",
                         10, 0.000001
                         )

    # Ouvre une fenetre pour changer la tension
    @override
    def double_clique_gauche(self, _):
        fenetre = QDialog()
        fenetre.setWindowTitle("Batterie")
        layout_principal = QVBoxLayout()
        fenetre.setLayout(layout_principal)
        sous_layout = QHBoxLayout()
        layout_principal.addLayout(sous_layout)

        texte = QLabel("Tension (V): ")
        sous_layout.addWidget(texte)
        # on veut que la tension inscrite soit un nombre entre 0 et 1000 (tensions réalistes)
        # avec une décimale de précision
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
            self.fil.calculs()
            # on retourne cela pour le rollback (1 pour savoir que batterie modifiée)
            return ancienne_tension, 1
        else:
            return -4, -4

    def rollback(self, ancienne_valeur):
        self.tension = ancienne_valeur


class LED(Composante):
    def __init__(self):
        super().__init__(TypeComposante.LED, "LED", "images/circuit/led.png",
                         "images/circuit/led.png",
                         "- Diode qui émet de la lumière quand le courant passe dans le bon sens <br>"
                         "- Elle a une polarité : anode (+) et cathode (-). <br>"
                         "- On met souvent une LED en série avec une résistance pour éviter trop de courant"
                         )


class Resistor(Composante):
    def __init__(self):
        super().__init__(TypeComposante.Resistor, "Résistor", "images/circuit/resistor.png",
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
    def double_clique_gauche(self, _):
        fenetre = QDialog()
        fenetre.setWindowTitle("Résistor")
        layout_principal = QVBoxLayout()
        fenetre.setLayout(layout_principal)
        sous_layout = QHBoxLayout()
        layout_principal.addLayout(sous_layout)

        texte = QLabel("Résistance (Ω): ")
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
            self.fil.calculs()
            return ancienne_resistance, 2
        else:
            return -4, -4

    def rollback(self, ancienne_resistance):
        self.resistance = ancienne_resistance


class Diode(Composante):
    def __init__(self):
        super().__init__(TypeComposante.Diode, "Diode", "images/circuit/diode.png",
                         "images/circuit/diode.png",
                         "- Laisse passer le courant dans un seul sens ( en résumé ). <br>"
                         "- Polarité importante. <br>"
                         "- Utile pour bloquer le retour de courant ou redresser un signal "
                         )


class Interrupteur(Composante):
    def __init__(self):
        super().__init__(TypeComposante.Interrupteur, "Interrupteur", "images/circuit/interrupteur_ouvert.png",
                         "images/circuit/interrupteur_ferme.png",
                         "- Sert à ouvrir ou fermer un circuit. <br>"
                         "- Ouvert : le courant ne passe pas. <br>"
                         "- Fermé : le courant peut passer ( si le circuit est complet )."
                         )

        self.ouvert = False

    @override
    def double_clique_gauche(self, taille_grid):
        if self.ouvert:
            image_path = self.image_circuit
            self.ouvert = False
            self.fil.calculs()
        else:
            # Image circuit est ouvert par défault dans la classe de base
            image_path = "images/circuit/interrupteur_ouvert.png"
            self.ouvert = True
            self.fil.ignorer = True

        pixmap = QPixmap(image_path)
        pixmap_scaled = pixmap.scaled(taille_grid * 2, taille_grid * 2)
        self.image_item.setPixmap(pixmap_scaled)
        # pour permettre logique uniforme dans modification
        return 0, 3


class Voltmetre(Composante):
    def __init__(self):
        super().__init__(TypeComposante.Voltmetre, "Voltmètre", "images/circuit/voltmetre.png",
                         "images/circuit/voltmetre.png",
                         "- Sert à mesurer la tension (différence de potentiel) entre deux points. <br> "
                         "- Unité : Volt (V). <br> "
                         "- Se branche en parallèle aux bornes de la composante dont on veut mesurer la tension. <br>"
                         "- Idéalement, la résistance dans le voltmètre est "
                         "très grande pour ne pas affecter le circuit."
                         )

        self.item_comp = None
        self.diff_potentiel = 0

    @override
    def double_clique_gauche(self, _):
        fenetre = QDialog()
        fenetre.setWindowTitle("Voltmètre")
        fenetre.setFixedSize(240, 350)

        # image qui simule le voltmètre
        image = QLabel(parent=fenetre)
        pixmap = QPixmap("images/interface/voltmetre.png")
        image.setPixmap(pixmap)
        image.setScaledContents(True)
        image.setGeometry(QRect(0, 110, 240, 270))

        fond = QLabel(parent=fenetre)
        fond.setStyleSheet("QLabel { background-color : #9e9a75; }")
        fond.setGeometry(4, 0, 232, 110)

        # Affiche un prefixe + V dans l'amperemetre
        if len(self.fil.composantes) == 1:
            prefixe, mult = prefixe_valeur(self.diff_potentiel)
            voltage_texte = str(round(self.diff_potentiel * mult, 4))
            texte_unite = QLabel(prefixe + "V", parent=fenetre)
            texte_unite.setStyleSheet("font-size: 30pt; color: #363535")
            texte_unite.setGeometry(4, 0, 232, 110)
            texte_unite.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            texte = QLabel(voltage_texte, parent=fenetre)
            texte.setStyleSheet("font-size: 40pt; color: #000000")

            # s'assure que le texte ne sorte pas ou n'overlap pas le "V"
            longueur_max = 186
            position_x = 5
            taille_police_initiale = 50
            police = texte.font()
            police.setPointSizeF(taille_police_initiale)
            verification = QFontMetrics(police)
            taille_texte = verification.boundingRect(texte.text()).width()
            if taille_texte >= longueur_max:
                while taille_texte >= longueur_max:
                    taille_police_initiale -= 1
                    police.setPointSizeF(taille_police_initiale)
                    verification = QFontMetrics(police)
                    taille_texte = verification.boundingRect(texte.text()).width()

            else:
                position_x = longueur_max / 2 - taille_texte / 2

            police.setPointSizeF(taille_police_initiale)
            texte.setFont(police)
            texte.setGeometry(position_x, 0, taille_texte + 4, 110)
        else:
            texte = QLabel("Le Voltmètre doit \nêtre seul sur un fil", parent=fenetre)
            texte.setStyleSheet("font-size: 20pt; color: #000000")
            texte.setGeometry(4, 0, 232, 110)
            texte.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        texte.raise_()
        fenetre.exec()


class Amperemetre(Composante):
    def __init__(self):
        super().__init__(TypeComposante.Amperemetre, "Ampèremètre", "images/circuit/amperemetre.png",
                         "images/circuit/amperemetre.png",
                         "- Sert à mesurer le courant électrique qui traverse une branche. <br>"
                         "- Unité : Ampères (A). <br> "
                         "- Se branche en série dans la branche où on veut mesurer le courant <br>"
                         "- Idéalement, la résistance dans l'ampèremètre est très faible."
                         )

        self.item_signes = None
        self.amperage = 0

    @override
    def double_clique_gauche(self, _):
        fenetre = QDialog()
        fenetre.setWindowTitle("Ampèremètre")
        fenetre.setFixedSize(240, 350)

        # image qui simule l'amperemetre
        image = QLabel(parent=fenetre)
        pixmap = QPixmap("images/interface/amperemetre.png")
        image.setPixmap(pixmap)
        image.setScaledContents(True)
        image.setGeometry(QRect(0, 110, 240, 270))

        fond = QLabel(parent=fenetre)
        fond.setStyleSheet("QLabel { background-color : #9e9a75; }")
        fond.setGeometry(4, 0, 232, 110)
        if abs(self.amperage) > 1000:
            texte = QLabel("COURT CIRCUIT", parent=fenetre)
            texte.setStyleSheet("font-size: 25pt; color: #EE0000")
            texte.setGeometry(4, 0, 232, 110)
            texte.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        else:
            prefixe, mult = prefixe_valeur(self.amperage)
            amperage_texte = str(round(self.amperage * mult, 4))
            texte = QLabel(amperage_texte, parent=fenetre)
            texte.setStyleSheet("font-size: 40pt; color: #000000")

            # Affiche un prefixe + A dans l'amperemetre
            texte_unite = QLabel(prefixe + "A", parent=fenetre)
            texte_unite.setStyleSheet("font-size: 30pt; color: #363535")
            texte_unite.setGeometry(4, 0, 232, 110)
            texte_unite.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # s'assure que le texte ne sorte pas ou n'overlap pas le "V"
            longueur_max = 186
            position_x = 5
            taille_police_initiale = 50
            police = texte.font()
            police.setPointSizeF(taille_police_initiale)
            verification = QFontMetrics(police)
            taille_texte = verification.boundingRect(texte.text()).width()
            if taille_texte >= longueur_max:
                while taille_texte >= longueur_max:
                    taille_police_initiale -= 1
                    police.setPointSizeF(taille_police_initiale)
                    verification = QFontMetrics(police)
                    taille_texte = verification.boundingRect(texte.text()).width()

            else:
                position_x = longueur_max / 2 - taille_texte / 2

            police.setPointSizeF(taille_police_initiale)
            texte.setFont(police)
            texte.setGeometry(position_x, 0, taille_texte + 4, 110)

        texte.raise_()
        fenetre.exec()


# ajoute le prefixe m(milli), mu(lettre grecque) ou n(nano)
def prefixe_valeur(valeur):
    valeur = abs(valeur)
    if valeur > 0.1:
        return "", 1
    elif valeur > 0.0001:
        return "m", 1000
    elif valeur > 0.0000001:
        return "μ", 1000000
    elif valeur > 0:
        return "n", 1000000000
    else:
        return "", 1


# afin de permettre aux copies d'être uniques, cela n'appelle plus la classe mais crée un objet de la classe
toolbar_composantes = {
    TypeComposante.Batterie: Batterie,
    TypeComposante.LED: LED,
    TypeComposante.Resistor: Resistor,
    TypeComposante.Diode: Diode,
    TypeComposante.Interrupteur: Interrupteur,
    TypeComposante.Voltmetre: Voltmetre,
    TypeComposante.Amperemetre: Amperemetre}
