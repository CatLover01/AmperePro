from enum import Enum

from PySide6.QtWidgets import QVBoxLayout, QDialog

from Niveau.LoiKirchoff.Kirchoff_4 import NiveauKirchoff4
from Niveau.LoiOhm.ohm_1 import NiveauOhm1
from Niveau.LoiOhm.ohm_2 import NiveauOhm2
from Niveau.LoiOhm.ohm_3 import NiveauOhm3
from Niveau.LoiOhm.ohm_4 import NiveauOhm4
from Niveau.LoiOhm.ohm_5 import NiveauOhm5
from Niveau.LoiKirchoff.kirchoff_1 import NiveauKirchoff1
from Niveau.LoiKirchoff.kirchoff_2 import NiveauKirchoff2
from Niveau.LoiKirchoff.kirchoff_3 import NiveauKirchoff3
#from Niveau.LoiKirchoff.kirchoff_4 import NiveauKirchoff4
from Niveau.Resistance_equivalente.re_1 import NiveauRE1


class Sujet(Enum):
    Ohm = "Loi d'ohm"
    Resistance = "Résistance équivalente"
    Kirchoff = "Loi de Kirchoff"


descriptions = {
    Sujet.Ohm: {
        1: "...",
        2: "...",
        3: "...",
        4: "...",
        5: "..."
    },
    Sujet.Kirchoff: {
        1: "Identification des ",
        2: "...",
        3: "...",
        4: "...",
        5: "..."
    },
    Sujet.Resistance: {
        1: "...",
        2: "...",
        3: "...",
        4: "...",
        5: "..."
    }
}


class NiveauWindow(QDialog):
    # Niveau commence à 1
    def __init__(self, sujet: Sujet, niveau: int, retour_sujet):
        super().__init__()

        # Longeur et largeur par défault
        self.resize(1200, 900)

        widget = None
        if sujet == Sujet.Ohm and niveau == 1:
            widget = NiveauOhm1(self.quitter)
            self.resize(1100, 850)
        elif sujet == Sujet.Ohm and niveau == 2:
            widget = NiveauOhm2(self.quitter)
            self.resize(1100, 850)
        elif sujet == Sujet.Ohm and niveau == 3:
            widget = NiveauOhm3(self.quitter)
        elif sujet == Sujet.Ohm and niveau == 4:
            widget = NiveauOhm4(self.quitter)
        elif sujet == Sujet.Ohm and niveau == 5:
            widget = NiveauOhm5(self.quitter)

        elif sujet == Sujet.Kirchoff and niveau == 1:
            widget = NiveauKirchoff1(self.quitter)
        elif sujet == Sujet.Kirchoff and niveau == 2:
            widget = NiveauKirchoff2(self.quitter)
        elif sujet == Sujet.Kirchoff and niveau == 3:
            widget = NiveauKirchoff3(self.quitter)
        elif sujet == Sujet.Kirchoff and niveau == 4:
            widget = NiveauKirchoff4(self.quitter)

        elif sujet == Sujet.Resistance and niveau == 1:
            widget = NiveauRE1(self.quitter)

        if widget is not None:
            layout = QVBoxLayout()
            layout.addWidget(widget)
            self.setLayout(layout)

    def quitter(self):
        self.close()
