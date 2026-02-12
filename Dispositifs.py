class Batterie:
    def __init__(self):
        self.nom = "Batterie"
        self.image_toolbar = "images/toolbar/batterie.jpg"
        self.image_circuit = "images/circuit/batterie.png"
        self.scale = 40
        self.rotate = True

        self.item_instance = None
        self.cote = None


class LED:
    def __init__(self):
        self.nom = "LED"
        self.image_toolbar = "images/toolbar/LED.webp"
        self.image_circuit = "images/circuit/LED.png"
        self.scale = 68
        self.rotate = True

        self.item_instance = None
        self.cote = None


class Resistor:
    def __init__(self):
        self.nom = "Resistor"
        self.image_toolbar = "images/toolbar/resistor.jpg"
        self.image_circuit = "images/circuit/resistor.png"
        self.scale = 55
        self.rotate = True

        self.item_instance = None
        self.cote = None


class Diode:
    def __init__(self):
        self.nom = "Diode"
        self.image_toolbar = "images/toolbar/diode.jpg"
        self.image_circuit = "images/circuit/diode.png"
        self.scale = 30
        self.rotate = True

        self.item_instance = None
        self.cote = None


class Interrupteur:
    def __init__(self):
        self.nom = "Interrupteur"
        self.image_toolbar = "images/toolbar/interrupteur.jpg"
        self.image_circuit = "images/circuit/interrupteur_ouvert.png"
        self.scale = 45
        self.rotate = True

        self.item_instance = None
        self.cote = None


class Voltmetre:
    def __init__(self):
        self.nom = "Voltmetres"
        self.image_toolbar = "images/toolbar/voltmetre.jpg"
        self.image_circuit = "images/circuit/voltmetre.png"
        self.scale = 40
        self.rotate = False

        self.item_instance = None
        self.cote = None


class Amperemetre:
    def __init__(self):
        self.nom = "Amperemetre"
        self.image_toolbar = "images/toolbar/amperemetre.jpg"
        self.image_circuit = "images/circuit/amperemetre.png"
        self.scale = 40
        self.rotate = False

        self.item_instance = None


toolbar_dispositifs = {
    "Batterie": Batterie(),
    "LED": LED(),
    "Resistor": Resistor(),
    "Diode": Diode(),
    "Interrupteur": Interrupteur(),
    "Voltmetre": Voltmetre(),
    "Amperemetre": Amperemetre()}
