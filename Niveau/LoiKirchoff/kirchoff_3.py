from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QFont, QPixmap, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QScrollArea
)

DOSSIER_IMAGES = "images/Niveau/kirchoff/3/"


class NiveauKirchoff3(QWidget):
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
        main_layout = QVBoxLayout()
        contenu.setLayout(main_layout)
        scroll.setWidget(contenu)

        contenu.setMaximumWidth(1100)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(25)

        titre = QLabel("Loi de Kirchoff - Niveau 3")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_titre = QFont()
        police_titre.setPointSize(30)
        titre.setFont(police_titre)
        main_layout.addWidget(titre)

        consigne = QLabel("Identifier les différentes mailles dans les cirucits suivants")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        consigne.setWordWrap(True)
        main_layout.addWidget(consigne)

        self.questions = [
            {
                "image": DOSSIER_IMAGES + "circuit_k_3.1.png",
                "texte": "Une des mailles dans le circuit en partant du point A",
                "reponse": "'ABEFA',ABCDEFA, AFEBA, AFEDCBA",

            },
            {
                "image": DOSSIER_IMAGES + "circuit_k_3.3.png",
                "texte": "Trouve l'Équation pour la maille FEBAF\n ne pas mettre les indices exemple: I\u2082=I2",
                "reponse": "12-4I2-6I3=0",

            },
            {
                "image": DOSSIER_IMAGES + "circuit_k_3.3.png",
                "texte": "Trouve l'Équation pour la maille FEBAF\n ne pas mettre les indices exemple: I\u2082=I2",
                "reponse": "-6+6I2+6-3I1",

            },
            {
                "image": DOSSIER_IMAGES + "circuit_k_3.4.png",
                "texte": "À partir du point D trouve l'éqaution d'une maille\n"
                         " sachant que I\u2081 = I\u2082 + I\u2083",
                "reponse": "",  #à repenser
            },

        ]

        for question in self.questions:
            self.ajouter_question(
                main_layout,
                question["image"],
                question["texte"],
                question["reponse"],
            )

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

    def ajouter_question(self, main_layout, image_path, texte_question, bonne_reponse):
        bloc = QVBoxLayout()
        bloc.setSpacing(12)

        image_label = QLabel()
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            image_label.setPixmap(
                pixmap.scaledToWidth(850, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            image_label.setText("Image introuvable : " + image_path)

        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bloc.addWidget(image_label)

        ligne_question = QHBoxLayout()

        label_question = QLabel(texte_question)
        champ_reponse = QLineEdit()
        champ_reponse.setFixedWidth(140)

        regex = QRegularExpression("^[I0-9+=-]*$")
        validator = QRegularExpressionValidator(regex)
        champ_reponse.setValidator(validator)

        ligne_question.addStretch()
        ligne_question.addWidget(label_question)
        ligne_question.addSpacing(10)
        ligne_question.addWidget(champ_reponse)
        ligne_question.addSpacing(5)
        ligne_question.addStretch()

        bloc.addLayout(ligne_question)

        main_layout.addLayout(bloc)

        self.reponses.append((champ_reponse, bonne_reponse))

    def normaliser_equation(self, eq):
        eq = eq.replace(" ", "")

        if "=" not in eq:
            return eq

        gauche, droite = eq.split("=")
        return f"{gauche}-{droite}"

    def valider_reponses(self):
        bonnes = 0
        total = len(self.reponses)

        for champ, bonne_reponse in self.reponses:
            texte = champ.text().strip()

            if not texte:
                continue

            try:
                eq_reponse = self.normaliser_equation(texte)
                eq_correcte = self.normaliser_equation(bonne_reponse)

                if eq_reponse == eq_correcte:
                    bonnes += 1
            except ValueError:
                pass

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
