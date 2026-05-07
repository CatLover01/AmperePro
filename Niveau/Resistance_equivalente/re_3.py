from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QScrollArea, QLineEdit
)


class NiveauRE3(QWidget):
    def __init__(self, retour_callback, update_niveau):
        super().__init__()

        self.retour_callback = retour_callback
        self.update_niveau = update_niveau

        self.questions_widgets = []

        # image + réponse
        self.questions = [
            ("images/niveau/Résistance équivalente/3/RE3-circuit1.png", 2),
            ("images/niveau/Résistance équivalente/3/RE3-circuit2.png", 2),
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

        # Titre
        titre = QLabel("Résistance équivalente - Niveau 3")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)

        police = QFont()
        police.setPointSize(28)

        titre.setFont(police)

        main_layout.addWidget(titre)

        # Consigne
        consigne = QLabel(
            "Calcule la résistance équivalente de chaque circuit."
        )

        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(consigne)

        # Questions
        for image_path, reponse in self.questions:
            self.ajouter_question(main_layout, image_path, reponse)

        # Boutons
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

    def ajouter_question(self, layout, image_path, bonne_reponse):

        bloc = QVBoxLayout()

        # Image
        image_label = QLabel()

        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            image_label.setPixmap(
                pixmap.scaledToWidth(
                    900
                )
            )
        else:
            image_label.setText(
                "Image introuvable : " + image_path
            )

        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        bloc.addWidget(image_label)

        # Question
        question = QLabel(
            "Quelle est la résistance équivalente dans ce circuit ?"
        )

        question.setAlignment(Qt.AlignmentFlag.AlignCenter)

        question.setFont(QFont("", 14))

        bloc.addWidget(question)

        # Input
        input_field = QLineEdit()

        input_field.setPlaceholderText(
            "Réponse en Ω"
        )

        input_field.setFixedWidth(200)

        bloc.addWidget(
            input_field,
            alignment=Qt.AlignCenter
        )

        layout.addLayout(bloc)

        self.questions_widgets.append(
            (input_field, bonne_reponse)
        )

    def valider(self):

        bonnes = 0

        for input_field, bonne_rep in self.questions_widgets:

            try:
                valeur = float(
                    input_field.text().replace(",", ".")
                )

                if valeur == bonne_rep:
                    bonnes += 1

            except:
                pass

        QMessageBox.information(
            self,
            "Résultat",
            f"{bonnes} bonnes réponses sur {len(self.questions_widgets)}"
        )

    def retour(self):

        if self.retour_callback:
            self.retour_callback()