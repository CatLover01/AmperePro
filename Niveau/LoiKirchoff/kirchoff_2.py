from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QScrollArea, QRadioButton, QButtonGroup
)

from Niveau.definitions import Sujet

DOSSIER_IMAGES = "images/Niveau/kirchoff/2/"


class NiveauKirchoff2(QWidget):
    def __init__(self, retour_callback, update_niveau):
        super().__init__()

        self.update_niveau = update_niveau
        self.retour_callback = retour_callback
        self.questions_widgets = []

        self.questions = [
            {
                "image": DOSSIER_IMAGES + "circuitk_2.1.png",
                "question": "15-12I\u2081-5I\u2082-7?=0",
                "type": "lettre",
                "reponse": "I₁",
            },
            {
                "image": DOSSIER_IMAGES + "circuitk_2.2.png",
                "question": "15-12I\u2081?5-7I\u2081=0",
                "type": "symbole",
                "reponse": "-",
            },
            {
                "image": DOSSIER_IMAGES + "circuitk_2.3.png",
                "question": "15-12I\u2081-2?-7I\u2082=0",
                "type": "lettre",
                "reponse": "I₃",
            },
            {
                "image": DOSSIER_IMAGES + "circuitk_2.4.png",
                "question": "À partir de la maille FEBAF\n"
                            "?6I\u2082+12-5I\u2081=0",
                "type": "symbole",
                "reponse": "+",
            },
            {
                "image": DOSSIER_IMAGES + "circuitk_2.4.png",
                "question": "À partir de la maille DCBED\n"
                            "-100I\u2083?12-6I\u2082=0",
                "type": "symbole",
                "reponse": "-",
            }

        ]

        main_layout = QVBoxLayout()

        titre = QLabel("Loi de Kirchoff - Niveau 2 ")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police = QFont()
        police.setPointSize(28)
        titre.setFont(police)
        main_layout.addWidget(titre)

        consigne = QLabel("Remplacer le symbole ? par la bonne réponse")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(consigne)

        for question in self.questions:
            self.ajouter_question(
                main_layout,
                question["image"],
                question["question"],
                question["type"],
                question["reponse"],
            )
        layout_exterieur = QVBoxLayout()
        self.setLayout(layout_exterieur)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout_exterieur.addWidget(scroll)

        contenu = QWidget()
        scroll.setWidget(contenu)
        contenu.setLayout(main_layout)

        boutons = QHBoxLayout()

        valider = QPushButton("Valider")
        valider.clicked.connect(self.valider)

        retour = QPushButton("Retour")
        retour.clicked.connect(self.retour)

        boutons.addStretch()
        boutons.addWidget(valider)
        boutons.addSpacing(20)
        boutons.addWidget(retour)
        boutons.addStretch()

        main_layout.addLayout(boutons)

    def ajouter_question(self, main_layout, image_path, texte_question, type_question, bonne_reponse):
        bloc = QHBoxLayout()
        bloc.setSpacing(20)

        image_label = QLabel()
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            image_label.setPixmap(
                pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            image_label.setText("Image introuvable : " + image_path)

            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ligne_question = QVBoxLayout()

        label_question = QLabel(texte_question)

        label_question.setWordWrap(True)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        label_question.setFont(font)


        ligne_question.addWidget(label_question)

        groupe = None
        if type_question == "symbole":
            btn_plus = QRadioButton("+")
            btn_moins = QRadioButton("-")

            groupe = QButtonGroup(self)
            groupe.addButton(btn_plus)
            groupe.addButton(btn_moins)
            groupe.setExclusive(True)

            ligne_question.addWidget(btn_plus)
            ligne_question.addWidget(btn_moins)

        elif type_question == "lettre":
            btn_i1 = QRadioButton("I₁")
            btn_i2 = QRadioButton("I₂")
            btn_i3 = QRadioButton("I₃")

            groupe = QButtonGroup(self)
            groupe.addButton(btn_i1)
            groupe.addButton(btn_i2)
            groupe.addButton(btn_i3)
            groupe.setExclusive(True)

            ligne_question.addWidget(btn_i1)
            ligne_question.addWidget(btn_i2)
            ligne_question.addWidget(btn_i3)

        self.questions_widgets.append((groupe, bonne_reponse))

        bloc.addLayout(ligne_question)
        bloc.addWidget(image_label)


        ligne_question.addStretch()
        ligne_question.addSpacing(10)
        ligne_question.addSpacing(5)
        ligne_question.addStretch()

        main_layout.addLayout(bloc)

    def valider(self):
        bonne_reponses = 0

        for groupe, bonne_rep in self.questions_widgets:
            btn = groupe.checkedButton()
            if btn and btn.text() == bonne_rep:
                bonne_reponses += 1

        self.update_niveau(Sujet.Kirchoff, 2, bonne_reponses)
        QMessageBox.information(
            self,
            "Résultat",
            f"{bonne_reponses} bonnes réponses sur {len(self.questions_widgets)}"
        )

    def retour(self):
        if self.retour_callback:
            self.retour_callback()
