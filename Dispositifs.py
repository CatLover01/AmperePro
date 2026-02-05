from PySide6.QtWidgets import QMainWindow



class Batterie:
    def __init__(self):
        self.nom = "Batterie"
        self.image_toolbar = "images/batterie.jpg"
        self.image_circuit = "images/pile_circuit.png"

class LED:
    def __init__(self):
        self.nom = "LED"
        self.image_toolbar = "images/LED.webp"

class Resistor:
    def __init__(self):
        self.nom = "Resistor"
        self.image_toolbar = "images/Resistor.jpg"

class Diode:
    def __init__(self):
        self.nom = "Diode"
        self.image_toolbar = "images/diode.jpg"

class Interrupteur:
    def __init__(self):
        self.nom = "Interrupteur"
        self.image_toolbar = "images/interrupteur.jpg"

class Voltmetre:
    def __init__(self):
        self.nom = "Voltmetres"
        self.image_toolbar = "images/voltmetre.jpg"

class Amperemetre:
    def __init__(self):
        self.nom = "Amperemetre"
        self.image_toolbar = "images/amperemetre.jpg"

toolbar_dispositifs = [Batterie(), LED(), Resistor(), Diode(), Interrupteur(), Voltmetre(), Amperemetre()]
