from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QFont, QPixmap, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QScrollArea, QGridLayout
)

from Niveau.definitions import Sujet


class NiveauKirchoff5(QWidget):
    def __init__(self, retour_callback, update_niveau):
        super().__init__()

        self.update_niveau = update_niveau
        self.retour_callback = retour_callback
        self.reponses = []

        layout_exterieur = QVBoxLayout()
        self.setLayout(layout_exterieur)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout_exterieur.addWidget(scroll)

        contenu = QWidget()
        main_layout = QVBoxLayout()
        contenu.setLayout(main_layout)
        scroll.setWidget(contenu)

        contenu.setMaximumWidth(1100)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(25)

        titre = QLabel("Loi de Kirchoff - Niveau 5")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_titre = QFont()
        police_titre.setPointSize(30)
        titre.setFont(police_titre)
        main_layout.addWidget(titre)

        consigne = QLabel("Identifier le courant dans les branches du circuit")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        consigne.setWordWrap(True)
        main_layout.addWidget(consigne)

        image_circuit = QLabel(pixmap=QPixmap("images/niveau/kirchoff/5/circuit_k_5.png"))
        image_circuit.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(image_circuit)

        layout_reponse = QGridLayout()

        self.reponse_i1 = QLineEdit()
        self.reponse_i2 = QLineEdit()
        self.reponse_i3 = QLineEdit()

        self.reponse_i1.setInputMask("9;_")
        self.reponse_i2.setInputMask("9;_")
        self.reponse_i3.setInputMask("9;_")

        i1 = QLabel("I\u2081 = ")
        i2 = QLabel("I\u2082 = ")
        i3 = QLabel("I\u2083 = ")

        layout_reponse.addWidget(i1, 0, 0)
        layout_reponse.addWidget(i2, 1, 0)
        layout_reponse.addWidget(i3, 2, 0)

        layout_reponse.addWidget(self.reponse_i1, 0, 1)
        layout_reponse.addWidget(self.reponse_i2, 1, 1)
        layout_reponse.addWidget(self.reponse_i3, 2, 1)

        main_layout.addLayout(layout_reponse)
        boutons_layout = QHBoxLayout()

        bouton_valider = QPushButton("Valider")
        bouton_valider.setFixedWidth(180)
        bouton_valider.clicked.connect(self.valider_reponses)

        bouton_retour = QPushButton("Retour")
        bouton_retour.setFixedWidth(180)
        bouton_retour.clicked.connect(self.retour)

        boutons_layout.addStretch()
        boutons_layout.addWidget(bouton_valider)
        boutons_layout.addSpacing(20)
        boutons_layout.addWidget(bouton_retour)
        boutons_layout.addStretch()

        main_layout.addLayout(boutons_layout)

    def valider_reponses(self):
        bonne_reponses = 0
        total = 3
        if self.reponse_i1.text() == "1":
            bonne_reponses += 1
        if self.reponse_i2.text() == "0":
            bonne_reponses += 1
        if self.reponse_i3.text() == "1":
            bonne_reponses += 1
        else:
            bonne_reponses += 0

        if bonne_reponses == total:
            QMessageBox.information(self, "Résultat", "Bravo ! Toutes les réponses sont bonnes.")
        else:
            QMessageBox.warning(
                self,
                "Résultat",
                "Tu as " + str(bonne_reponses) + " bonne(s) réponse(s) sur " + str(total) + "."
            )

    def retour(self):
        if self.retour_callback is not None:
            self.retour_callback()
