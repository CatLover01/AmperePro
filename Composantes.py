from PySide6.QtGui import QPixmap, Qt, QTransform
from PySide6.QtWidgets import QGraphicsPixmapItem

# Faudrait peut-être créer une classe abstraite pour les composantes
# Chaque classe a un nom (sûrement inutile et à enlever), son image dans la tool bar et dans le circuit,
# le scale de son image dans le circuit, si il doit se tourner (les composantes qui ont des lettre sur
# l'image peuvent pas). item_instance est leur QGraphicsPixmapItem et cote le cote ou ils sont
# Et def clicked est appelé quand leur item_instance est cliqué


class Batterie:
    def __init__(self):
        self.nom = "Batterie"
        self.image_toolbar = "images/toolbar/batterie.jpg"
        self.image_circuit = "images/circuit/batterie.png"
        self.scale = 40
        self.rotate = True

        self.item_instance = None
        self.cote = None

    def clicked(self):
        pass


class LED:
    def __init__(self):
        self.nom = "LED"
        self.image_toolbar = "images/toolbar/LED.webp"
        self.image_circuit = "images/circuit/LED.png"
        self.scale = 68
        self.rotate = True

        self.item_instance = None
        self.cote = None
        self.sens = 1

    def clicked(self):
        # Flip la LED
        transform = QTransform()
        transform.scale(-1, 1)
        pixmap_flipped = self.item_instance.pixmap().transformed(transform)
        self.item_instance.setPixmap(pixmap_flipped)
        self.sens *= -1


class Resistor:
    def __init__(self):
        self.nom = "Resistor"
        self.image_toolbar = "images/toolbar/resistor.jpg"
        self.image_circuit = "images/circuit/resistor.png"
        self.scale = 56
        self.rotate = True

        self.item_instance = None
        self.cote = None

    def clicked(self):
        pass


class Diode:
    def __init__(self):
        self.nom = "Diode"
        self.image_toolbar = "images/toolbar/diode.jpg"
        self.image_circuit = "images/circuit/diode.png"
        self.scale = 30
        self.rotate = True

        self.item_instance = None
        self.cote = None
        self.sens = 1

    def clicked(self):
        #Flip la diode
        transform = QTransform()
        transform.scale(-1, 1)
        pixmap_flipped = self.item_instance.pixmap().transformed(transform)
        self.item_instance.setPixmap(pixmap_flipped)
        self.sens *= -1


class Interrupteur:
    def __init__(self):
        self.nom = "Interrupteur"
        self.image_toolbar = "images/toolbar/interrupteur.jpg"
        self.image_ouvert = "images/circuit/interrupteur_ouvert.png"
        self.image_ferme = "images/circuit/interrupteur_ferme.png"
        self.scale = 45
        self.rotate = True

        self.image_circuit = self.image_ouvert
        self.item_instance = None
        self.cote = None
        self.ouvert = True

    def clicked(self):
        if self.image_circuit == self.image_ouvert:
            self.image_circuit = self.image_ferme
        else:
            self.image_circuit = self.image_ouvert

        pixmap = QPixmap(self.image_circuit)
        pixmap_scaled = pixmap.scaled(self.scale, self.scale, Qt.AspectRatioMode.KeepAspectRatio)

        self.item_instance.setPixmap(pixmap_scaled)
        self.ouvert = False


class Voltmetre:
    def __init__(self):
        self.nom = "Voltmetres"
        self.image_toolbar = "images/toolbar/voltmetre.jpg"
        self.image_circuit = "images/circuit/voltmetre.png"
        self.scale = 40
        self.rotate = False

        self.item_instance = None
        self.cote = None

    def clicked(self):
        pass


class Amperemetre:
    def __init__(self):
        self.nom = "Amperemetre"
        self.image_toolbar = "images/toolbar/amperemetre.jpg"
        self.image_circuit = "images/circuit/amperemetre.png"
        self.scale = 40
        self.rotate = False

        self.item_instance = None

    def clicked(self):
        pass


# Classe des item_instance des composantes
class Item(QGraphicsPixmapItem):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    # appel la fonction clicked de sa composante parente
    def mousePressEvent(self, event):
        self.parent.clicked()


toolbar_composantes = {
    "Batterie": Batterie(),
    "LED": LED(),
    "Resistor": Resistor(),
    "Diode": Diode(),
    "Interrupteur": Interrupteur(),
    "Voltmetre": Voltmetre(),
    "Amperemetre": Amperemetre()}
