import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, \
    QScrollArea, QCheckBox


class NiveauKirchoff1(QWidget):
    def __init__(self, retour_callback=None):
        super().__init__()

        self.retour_callback = retour_callback
        self.reponses = []

        layout_exterieur = QVBoxLayout()
        self.setLayout(layout_exterieur)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout_exterieur.addWidget(scroll)

        contenu = QWidget()
        contenu.setMaximumWidth(900)
        main_layout = QVBoxLayout()
        contenu.setLayout(main_layout)
        scroll.setWidget(contenu)

        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        titre = QLabel("LoiKirchoff - Niveau 1")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_titre = QFont()
        police_titre.setPointSize(32)
        titre.setFont(police_titre)
        main_layout.addWidget(titre)

        formule = QLabel("I\u2081 = I\u2082 + I\u2083")
        formule.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_formule = QFont()
        police_formule.setPointSize(36)
        police_formule.setBold(True)
        formule.setFont(police_formule)
        main_layout.addWidget(formule)

        consigne = QLabel("Trouver les différents noeud dans les circuits")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(consigne)

        main_layout.addSpacing(10)
        lettre = ["A", "B", "C", "D", "E", "F"]
        q1_layout = QVBoxLayout()

        circuit1 = QLabel(pixmap=QPixmap("images/Niveau/kirchoff/1/circuit_K_1.1.png"))
        circuit1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q1_layout.addWidget(circuit1)

        bonne_reponse_q1 = ["B", "E"]

        for i in range(6):
            layout_choix1 = QHBoxLayout()  # revenir dessus
            choix_de_reponse = QCheckBox(lettre[i])
            layout_choix1.addWidget(choix_de_reponse)
            q1_layout.addLayout(layout_choix1)

            self.reponses.append((choix_de_reponse, lettre[i] in bonne_reponse_q1))
        main_layout.addLayout(q1_layout)

        q2_layout = QVBoxLayout()

        circuit2 = QLabel(pixmap=QPixmap("images/Niveau/kirchoff/1/circuit_K_1.2.png"))
        circuit2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q2_layout.addWidget(circuit2)

        bonne_reponse_q2 = ["B", "D"]

        for i in range(4):
            layout_choix2 = QHBoxLayout()  # revenir dessus
            choix_de_reponse = QCheckBox(lettre[i])
            layout_choix2.addWidget(choix_de_reponse)
            q2_layout.addLayout(layout_choix2)

            self.reponses.append((choix_de_reponse, lettre[i] in bonne_reponse_q2))
        main_layout.addLayout(q2_layout)

        main_layout.addSpacing(20)

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
        bonnes = 0
        total = len(self.reponses)

        for checkbox, bonne_reponse in self.reponses:
            if checkbox.isChecked() == bonne_reponse:
                bonnes += 1

        if bonnes == total:
            QMessageBox.information(self, "Résultat", "Bravo ! Toutes les réponses sont bonnes.")
        else:
            QMessageBox.warning(
                self,
                "Résultat",
                "Tu as " + str(bonnes) + " bonne(s) réponse(s) sur " + str(total) + "."
            )

    def retour(self):
        if self.retour_callback is not None:
            self.retour_callback()
