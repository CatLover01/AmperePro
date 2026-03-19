from PySide6 import QtCore
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from Composantes import toolbar_composantes
# Voir les descriptions des composites pour le reste de la documentation
Texte = {
    "Série / Parallèle" :(
        "Série / Parallèle \n\n"
        "Série : \n"
        "- Le courant est le même partout. \n"
        "- Les résistances s'additionnent : R_eq = R1 + R2 + R3 +... \n\n"
        "Parallèle : \n"
        "- La tension est la même sur chaqu branche. \n"
        "- 1/R_eq = 1/R1 + 1/R2 + 1/R3 \n"
    ),
 "Loi d'Ohm": (
        "Loi d'Ohm \n\n"
        "- Relation entre tension, courant et résistance. \n"
        "- Formule : V = R · I \n"
        "- V en Volts, R en Ohms, I en Ampères"
    ),

    "Loi de Kirchhoff": (
        "Loi de Kirchhoff \n\n"
        "Loi des noeuds : \n"
        "- La somme des courants entrants = somme des courants sortants. \n\n"
        "Loi des mailles : \n"
        "- La somme des tensions dans une boucle = 0."
    ),

    "Puissance électrique": (
        "Puissance électrique \n\n"
        "- Mesure l’énergie consommée. \n"
        "- Formule : P = V · I \n"
        "- Unité : Watt (W)"
    )
}


class DocumentationWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        self.setWindowTitle("Documentation")
        self.setFixedSize(700, 500)

        # widget principal
        widget = QWidget()
        layout = QHBoxLayout()

        # liste à gauche
        self.liste = QListWidget()


        self.liste.addItem("Série / Parallèle")
        self.liste.addItem("Loi d'Ohm")
        self.liste.addItem("Loi de Kirchhoff")
        self.liste.addItem("Puissance électrique")
        for composante in toolbar_composantes.values():
            self.liste.addItem(composante.nom)

        # texte à droite
        self.label = QLabel("Clique sur un sujet")

        self.label.setFixedSize(450, 400)
        self.label.setAlignment(QtCore.Qt.AlignTop)
        self.label.setAlignment(Qt.AlignTop)
        self.label.setStyleSheet("border: 1px solid black; padding: 8px;")
        self.label.setWordWrap(True)

        # connecter le clic
        self.liste.itemClicked.connect(self.changer_texte)

        # ajouter dans le layout
        layout.addWidget(self.liste)
        layout.addWidget(self.label)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        bouton_retour = QPushButton("Retour")
        bouton_retour.clicked.connect(self.close)
        layout.addWidget(bouton_retour)

    def changer_texte(self, item):
        texte_selectionne = item.text()

        if texte_selectionne == "Série / Parallèle":
            self.label.setText(Texte["Série / Parallèle"])
            return

        if texte_selectionne == "Loi d'Ohm":
            self.label.setText("<b>Loi d'Ohm</b><br><br>" + Texte["Loi d'Ohm"])
            return

        if texte_selectionne == "Loi de Kirchhoff":
            self.label.setText("<b>Loi de Kirchhoff</b><br><br>" + Texte["Loi de Kirchhoff"])
            return

        if texte_selectionne == "Puissance électrique":
            self.label.setText("<b>Puissance électrique</b><br><br>" + Texte["Puissance électrique"])
            return


        for composante in toolbar_composantes.values():
            if texte_selectionne == composante.nom:
                self.label.setText("<b>" + composante.nom + "\n\n" + "</b><br><br>" + composante.description)
                return
