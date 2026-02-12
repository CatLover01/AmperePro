from PySide6.QtGui import QPixmap, Qt, QTransform
from PySide6.QtWidgets import QGraphicsPixmapItem


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
        # 1 si elle va du sens horaire sinon -1
        self.sens = 1

    def clicked(self):
        transform = QTransform()
        transform.scale(-1, -1)
        pixmap = self.item_instance.pixmap().transformed(transform, Qt.TransformationMode.SmoothTransformation)
        self.item_instance.setPixmap(pixmap)
        self.sens *= -1


class Resistor:
    def __init__(self):
        self.nom = "Resistor"
        self.image_toolbar = "images/toolbar/resistor.jpg"
        self.image_circuit = "images/circuit/resistor.png"
        self.scale = 55
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
        #1 si elle va du sens horaire sinon -1
        self.sens = 1

    def clicked(self):
        transform = QTransform()
        transform.scale(-1, -1)
        pixmap = self.item_instance.pixmap().transformed(transform, Qt.TransformationMode.SmoothTransformation)
        self.item_instance.setPixmap(pixmap)
        self.sens *= -1

class Interrupteur:
    def __init__(self):
        self.nom = "Interrupteur"
        self.image_toolbar = "images/toolbar/interrupteur.jpg"
        self.image_ferme = "images/circuit/interrupteur_ferme.png"
        self.image_ouvert = "images/circuit/interrupteur_ouvert.png"

        self.image_circuit = self.image_ouvert
        self.scale = 45
        self.rotate = True

        self.item_instance = None
        self.cote = None

    def clicked(self):

        if self.image_circuit == self.image_ouvert:
            self.image_circuit = self.image_ferme
        else:
            self.image_circuit = self.image_ouvert

        pixmap = QPixmap(self.image_circuit)
        pixmap_scaled = pixmap.scaled(self.scale, self.scale, Qt.AspectRatioMode.KeepAspectRatio)

        self.item_instance.setPixmap(pixmap_scaled)

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

class Item(QGraphicsPixmapItem):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def mousePressEvent(self, event):
        self.parent.clicked()

toolbar_dispositifs = {
    "Batterie": Batterie(),
    "LED": LED(),
    "Resistor": Resistor(),
    "Diode": Diode(),
    "Interrupteur": Interrupteur(),
    "Voltmetre": Voltmetre(),
    "Amperemetre": Amperemetre()}
