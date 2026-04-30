from collections.abc import Callable
from enum import Enum

from PySide6.QtGui import QPixmap, Qt, QTransform
from PySide6.QtWidgets import QGraphicsPixmapItem, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QDoubleSpinBox
from abc import ABC


class Cote(Enum):
    Gauche = 1
    Droite = 2
    Haut = 3
    Bas = 4


# Type de composante que nous supportons
class Type(Enum):
    Batterie = 1
    LED = 2
    Resistor = 3
    Diode = 4
    Interrupteur = 5
    Voltmetre = 6
    Amperemetre = 7


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
        super().__init__(Type.Batterie, "Batterie", "images/circuit/batterie.png",
                         "images/circuit/batterie.png", 40,
                         "- Fournit l’énergie électrique au circuit. <br>"
                         "- Crée une différence de potentiel (tension). <br>"
                         "- Possède une borne positive (+) et négative (-). <br>"
                         "- Permet au courant de circuler dans le circuit."
                         )


class LED(ComposanteBase):
    def __init__(self):
        super().__init__(Type.LED, "LED", "images/circuit/LED.png", "images/circuit/LED.png", 68,
                         "- Diode qui émet de la lumière quand le courant passe dans le bon sens <br>"
                         "- Elle a une polarité : anode (+) et cathode (-). <br>"
                         "- On met souvent une résistance en série une LED pour évitr trop de courant"
                         )


class Resistor(ComposanteBase):
    def __init__(self):
        super().__init__(Type.Resistor, "Résistor", "images/circuit/resistor.png",
                         "images/circuit/resistor.png", 56,
                         "- Composante qui limite le courant. <br>"
                         "- Unité : Ohms (Ω) <br>"
                         "- Loi d'Ohm : V = R · I <br>"
                         "- Baisse l'intensité du courant. <br>"
                         "- V en Volts, R en Ohms, I en Ampères"
                         )


class Diode(ComposanteBase):
    def __init__(self):
        super().__init__(Type.Diode, "Diode", "images/circuit/diode.png", "images/circuit/diode.png", 30,
                         "- Laisse passer le courant dans un seul sens ( en résumé ). <br>"
                         "- Polarité importante. <br>"
                         "- Utile pour bloquer le retour de courant ou redresser un signal "
                         )


class Interrupteur(ComposanteBase):
    def __init__(self):
        super().__init__(Type.Interrupteur, "Interrupteur", "images/circuit/interrupteur_ouvert.png",
                         "images/circuit/interrupteur_ouvert.png", 45,
                         "- Sert à ouvrir ou fermer un circuit. <br>"
                         "- Ouvert : le courant ne passe pas. <br>"
                         "- Fermé : le courant peut passer ( si le circuit est complet )."
                         )


class Voltmetre(ComposanteBase):
    def __init__(self):
        super().__init__(Type.Voltmetre, "Voltmètre", "images/circuit/voltmetre.png",
                         "images/circuit/voltmetre.png", 40,
                         "- Sert à mesurer la tension (différence de potentiel) entre deux points. <br> "
                         "- Unité : Volt (V). <br> "
                         "- Se branche en parallèle aux bornes de la composante dont on veut mesurer la tension. <br>"
                         "- Idéalement, la résistance dans le voltmètre est très grande pour ne pas déranger le circuit."
                         )


class Amperemetre(ComposanteBase):
    def __init__(self):
        super().__init__(Type.Amperemetre, "Ampèremètre", "images/circuit/amperemetre.png",
                         "images/circuit/amperemetre.png", 40,
                         "- Sert à mesurer le courant électrique qui traverse une branche. <br>"
                         "- Unité : Ampères (A). <br> "
                         "- Se branche en série dans la branche où on veut mesurer le courant <br>"
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


class InfosComposantes:
    @staticmethod
    def infos_batterie(sens):
        nom = "Batterie"
        direction = sens
        voltage = 10
        return [nom, direction, voltage]

    @staticmethod
    def infos_led(sens):
        nom = "LED"
        direction = sens
        return [nom, direction]

    @staticmethod
    def infos_resistor(sens):
        nom = "Résistor"
        direction = sens
        resistance = 1000
        return [nom, direction, resistance]

    @staticmethod
    def infos_diode(sens):
        nom = "Diode"
        direction = sens
        return [nom, direction]

    @staticmethod
    def infos_interrupteur(sens):
        nom = "Interrupteur"
        direction = sens
        etat = "ouvert"
        return [nom, direction, etat]

    @staticmethod
    def infos_amperemetre(sens):
        nom = "Ampèremètre"
        affichage = 0
        return [nom,affichage]

    @staticmethod
    def infos_voltmetre(sens):
        nom = "Voltmètre"
        affichage = 0
        return [nom, affichage]

    def liste_a_ajouter(self, composante, sens):
        nom = composante.nom
        retourne = []
        if nom == "Batterie":
            retourne = self.infos_batterie(sens)
        elif nom == "LED":
            retourne = self.infos_led(sens)
        elif nom == "Résistor":
            retourne = self.infos_resistor(sens)
        elif nom == "Diode":
            retourne = self.infos_diode(sens)
        elif nom == "Interrupteur":
            retourne = self.infos_interrupteur(sens)
        elif nom == "Ampèremètre":
            retourne = self.infos_amperemetre(sens)
        elif nom == "Voltmètre":
            retourne = self.infos_voltmetre(sens)

        return retourne

    @staticmethod
    def verifier_composante_modifiee(element):
        nom = element[0]
        # on ne peut pas modifier une led et une diode
        if nom == "LED" or nom == "Diode":
            return "ignorer"
        # sinon on veut savoir le nom de la composante pour l'étape à suivre.
        else:
            return nom

    @staticmethod
    def fenetre_batterie(infos_batterie):
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
        nombre.setRange(0, 9999.9)
        nombre.setDecimals(1)
        # on donne au line edit la valeur actuelle de tension (10v si aucune modification)
        valeur = infos_batterie[-1]
        nombre.setValue(valeur)
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
        if verifier_return == QDialog.Accepted:
            if verifier_return == QDialog.Accepted:
                if valeur != nombre.value():
                    infos_batterie = infos_batterie[0:2]
                    infos_batterie.append(nombre.value())
                    return infos_batterie, valeur
                else:
                    return None, None
        else:
            return None, None

    @staticmethod
    def fenetre_resistor(infos_resistor):
        fenetre = QDialog()
        fenetre.setWindowTitle("Résistor")
        layout_principal = QVBoxLayout()
        fenetre.setLayout(layout_principal)
        sous_layout = QHBoxLayout()
        layout_principal.addLayout(sous_layout)

        texte = QLabel("Résistance (Ω): ")
        sous_layout.addWidget(texte)
        # on veut que la résistance inscrite soit un nombre entre 0 et 10000 (résistances réalistes) avec une décimale de précision
        nombre = QDoubleSpinBox()
        nombre.setRange(0, 9999999.9)
        nombre.setDecimals(1)
        # on donne au line edit la valeur actuelle de tension (10v si aucune modification)
        valeur = infos_resistor[-1]
        nombre.setValue(valeur)
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
        if verifier_return == QDialog.Accepted:
            if valeur != nombre.value():
                infos_resistor = infos_resistor[0:2]
                infos_resistor.append(nombre.value())
                return infos_resistor, valeur
            else:
                return None, None

        else:
            return None, None

    @staticmethod
    def retourner_image(liste):
        nom_composante = liste[0]
        sens = liste[1]
        classe = composantes.get(nom_composante)
        image = classe.image_circuit
        nouveau_sens = ""
        if sens == "haut":
            nouveau_sens = "bas"
        elif sens == "bas":
            nouveau_sens = "haut"
        elif sens == "droite":
            nouveau_sens = "gauche"
        else:
            nouveau_sens = "droite"

        return image, sens, nouveau_sens


toolbar_composantes = {
    Type.Batterie: Batterie(),
    Type.LED: LED(),
    Type.Resistor: Resistor(),
    Type.Diode: Diode(),
    Type.Interrupteur: Interrupteur(),
    Type.Voltmetre: Voltmetre(),
    Type.Amperemetre: Amperemetre()}

composantes = {"Batterie": Batterie(),
               "LED": LED(),
               "Résistor": Resistor(),
               "Diode": Diode(),
               "Interrupteur": Interrupteur(),
               "Voltmètre": Voltmetre(),
               "Ampèremètre": Amperemetre()}
