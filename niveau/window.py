from PySide6.QtWidgets import QVBoxLayout, QDialog

from niveau.kirchoff.kirchoff_4 import NiveauKirchoff4
from niveau.kirchoff.kirchoff_5 import NiveauKirchoff5
from niveau.ohm.ohm_1 import NiveauOhm1
from niveau.ohm.ohm_2 import NiveauOhm2
from niveau.ohm.ohm_3 import NiveauOhm3
from niveau.ohm.ohm_4 import NiveauOhm4
from niveau.ohm.ohm_5 import NiveauOhm5
from niveau.kirchoff.kirchoff_1 import NiveauKirchoff1
from niveau.kirchoff.kirchoff_2 import NiveauKirchoff2
from niveau.kirchoff.kirchoff_3 import NiveauKirchoff3
from niveau.resistance_equivalente.re_1 import NiveauRE1
from niveau.resistance_equivalente.re_2 import NiveauRE2
from niveau.resistance_equivalente.re_3 import NiveauRE3
from niveau.resistance_equivalente.re_4 import NiveauRE4
from niveau.definitions import Sujet


class NiveauWindow(QDialog):
    # niveau commence à 1
    def __init__(self, sujet: Sujet, niveau: int, update_niveau):
        super().__init__()

        # Longeur et largeur par défault
        self.resize(1200, 900)

        widget = None
        if sujet == Sujet.Ohm and niveau == 1:
            widget = NiveauOhm1(self.quitter, update_niveau)
            self.resize(1100, 850)
        elif sujet == Sujet.Ohm and niveau == 2:
            widget = NiveauOhm2(self.quitter, update_niveau)
            self.resize(1100, 850)
        elif sujet == Sujet.Ohm and niveau == 3:
            widget = NiveauOhm3(self.quitter, update_niveau)
        elif sujet == Sujet.Ohm and niveau == 4:
            widget = NiveauOhm4(self.quitter, update_niveau)
        elif sujet == Sujet.Ohm and niveau == 5:
            widget = NiveauOhm5(self.quitter, update_niveau)

        elif sujet == Sujet.Kirchoff and niveau == 1:
            widget = NiveauKirchoff1(self.quitter, update_niveau)
        elif sujet == Sujet.Kirchoff and niveau == 2:
            widget = NiveauKirchoff2(self.quitter, update_niveau)
        elif sujet == Sujet.Kirchoff and niveau == 3:
            widget = NiveauKirchoff3(self.quitter, update_niveau)
        elif sujet == Sujet.Kirchoff and niveau == 4:
            widget = NiveauKirchoff4(self.quitter, update_niveau)
        elif sujet == Sujet.Kirchoff and niveau == 5:
            widget = NiveauKirchoff5(self.quitter, update_niveau)

        elif sujet == Sujet.Resistance and niveau == 1:
            widget = NiveauRE1(self.quitter, update_niveau)
        elif sujet == Sujet.Resistance and niveau == 2:
            widget = NiveauRE2(self.quitter, update_niveau)
        elif sujet == Sujet.Resistance and niveau == 3:
            widget = NiveauRE3(self.quitter, update_niveau)
        elif sujet == Sujet.Resistance and niveau == 4:
            widget = NiveauRE4(self.quitter, update_niveau)

        if widget is not None:
            layout = QVBoxLayout()
            layout.addWidget(widget)
            self.setLayout(layout)

    def quitter(self):
        self.close()
