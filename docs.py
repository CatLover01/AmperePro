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
        for composante in toolbar_composantes.values():
            self.liste.addItem(composante.nom)

        # texte à droite
        self.label = QLabel("Clique sur un sujet")

        self.label.setAlignment(Qt.AlignTop)

        # connecter le clic
        self.liste.itemClicked.connect(self.changer_texte)

        # ajouter dans le layout
        layout.addWidget(self.liste)
        layout.addWidget(self.label)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def changer_texte(self, item):
        texte_selectionne = item.text()

        if texte_selectionne == "Série / Parallèle":
            self.label.setText(Texte["Série / Parallèle"])
            return

        for composante in toolbar_composantes.values():
            if texte_selectionne == composante.nom:
                self.label.setText(composante.description)
                return