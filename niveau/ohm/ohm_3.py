from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QScrollArea
)

from niveau.definitions import Sujet

DOSSIER_IMAGES = "images/niveau/ohm/3/"

class NiveauOhm3(QWidget):
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

        titre = QLabel("Loi d'Ohm - Niveau 3")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_titre = QFont()
        police_titre.setPointSize(30)
        titre.setFont(police_titre)
        main_layout.addWidget(titre)

        consigne = QLabel("Détermine les valeurs manquantes pour chacune des mises en situation proposées.")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        consigne.setWordWrap(True)
        main_layout.addWidget(consigne)

        self.questions = [
            {
                "image": DOSSIER_IMAGES + "circuit_1.png",
                "texte": "La résistance dans R1 est de",
                "reponse": 20,
                "unite": "Ω"
            },
            {
                "image": DOSSIER_IMAGES + "circuit_2.png",
                "texte": "La tension à la source est de",
                "reponse": 100,
                "unite": "V"
            },
            {
                "image": DOSSIER_IMAGES + "circuit_3.png",
                "texte": "La résistance de la source lumineuse est de",
                "reponse": 20,
                "unite": "Ω"
            },
            {
                "image": DOSSIER_IMAGES + "circuit_4.png",
                "texte": "L'intensité du courant sortant de l'ampoule est de",
                "reponse": 0.6,
                "unite": "A"
            },
            {
                "image": DOSSIER_IMAGES + "circuit_5.png",
                "texte": "La différence de potentiel dans la résistance est de",
                "reponse": 50,
                "unite": "V"
            }
        ]

        for question in self.questions:
            self.ajouter_question(
                main_layout,
                question["image"],
                question["texte"],
                question["reponse"],
                question["unite"]
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

    def ajouter_question(self, main_layout, image_path, texte_question, bonne_reponse, unite):
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

        label_unite = QLabel(unite)

        ligne_question.addStretch()
        ligne_question.addWidget(label_question)
        ligne_question.addSpacing(10)
        ligne_question.addWidget(champ_reponse)
        ligne_question.addSpacing(5)
        ligne_question.addWidget(label_unite)
        ligne_question.addStretch()

        bloc.addLayout(ligne_question)

        main_layout.addLayout(bloc)

        self.reponses.append((champ_reponse, bonne_reponse))

    def valider_reponses(self):
        bonne_reponses = 0
        total = len(self.reponses)

        for champ, bonne_reponse in self.reponses:
            texte = champ.text().strip().replace(",", ".")

            try:
                valeur = float(texte)
                if abs(valeur - bonne_reponse) < 0.01:
                    bonne_reponses += 1
            except ValueError:
                pass

        self.update_niveau(Sujet.Ohm, 3, bonne_reponses)
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