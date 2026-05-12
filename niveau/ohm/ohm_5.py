from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QScrollArea
)

from niveau.definitions import Sujet


class NiveauOhm5(QWidget):
    def __init__(self, retour_callback, update_niveau):
        super().__init__()

        self.update_niveau = update_niveau
        self.retour_callback = retour_callback
        self.reponses = []

        self.questions = [
            ("images/niveau/ohm/5/circuit_1.png", 4.67),
            ("images/niveau/ohm/5/circuit_2.png", 4),
            ("images/niveau/ohm/5/circuit_3.png", 2.75),
            ("images/niveau/ohm/5/circuit_4.png", 5),
            ("images/niveau/ohm/5/circuit_5.png", 4),
        ]

        layout_exterieur = QVBoxLayout()
        self.setLayout(layout_exterieur)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout_exterieur.addWidget(scroll)

        contenu = QWidget()
        scroll.setWidget(contenu)

        main_layout = QVBoxLayout()
        contenu.setLayout(main_layout)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(30)

        titre = QLabel("Loi d'Ohm - niveau 5")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_titre = QFont()
        police_titre.setPointSize(30)
        titre.setFont(police_titre)
        main_layout.addWidget(titre)

        consigne = QLabel("Trouver la résistance équivalente de chaque circuit.")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        consigne.setWordWrap(True)
        main_layout.addWidget(consigne)

        for image_path, bonne_reponse in self.questions:
            self.ajouter_question(main_layout, image_path, bonne_reponse)

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

    def ajouter_question(self, main_layout, image_path, bonne_reponse):
        bloc = QVBoxLayout()
        bloc.setSpacing(12)

        image_label = QLabel()
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            image_label.setPixmap(
                pixmap.scaledToWidth(800, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            image_label.setText("Image introuvable : " + image_path)

        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bloc.addWidget(image_label)

        ligne_reponse = QHBoxLayout()

        label = QLabel("R =")
        champ = QLineEdit()
        champ.setFixedWidth(120)
        unite = QLabel("Ω")

        ligne_reponse.addStretch()
        ligne_reponse.addWidget(label)
        ligne_reponse.addSpacing(8)
        ligne_reponse.addWidget(champ)
        ligne_reponse.addSpacing(8)
        ligne_reponse.addWidget(unite)
        ligne_reponse.addStretch()

        bloc.addLayout(ligne_reponse)
        main_layout.addLayout(bloc)

        self.reponses.append((champ, bonne_reponse))

    def valider_reponses(self):
        bonne_reponses = 0

        for champ, bonne_reponse in self.reponses:
            try:
                valeur = float(champ.text().replace(",", "."))
                if abs(valeur - bonne_reponse) < 0.05:
                    bonne_reponses += 1
            except ValueError:
                pass

        self.update_niveau(Sujet.Ohm, 5, bonne_reponses)
        QMessageBox.information(
            self,
            "Résultat",
            f"{bonne_reponses} bonnes réponses sur {len(self.reponses)}"
        )

    def retour(self):
        if self.retour_callback is not None:
            self.retour_callback()