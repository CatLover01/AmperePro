from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QScrollArea, QLineEdit
)


class NiveauRE2(QWidget):
    def __init__(self, retour_callback=None, update_niveau=None):
        super().__init__()

        self.retour_callback = retour_callback
        self.questions_widgets = []

        # (question, réponse)
        self.questions = [
            # Série
            ("Circuit en série :\nReq = 15 Ω\nR1 = 5 Ω\nR2 = 4 Ω\nR3 = ?", 6),

            # Parallèle
            ("Circuit en parallèle à 3 branches :\nReq = 2 Ω\nR1 = 6 Ω\nR2 = 3 Ω\nR3 = ?", 6),

            # Parallèle
            ("Circuit en parallèle à 4 branches :\nReq = 1 Ω\nR1 = 2 Ω\nR2 = 2 Ω\nR3 = 2 Ω\nR4 = ?", 2),

            # Série
            ("Circuit en série :\nReq = 20 Ω\nR1 = 8 Ω\nR2 = ?\nR3 = 5 Ω", 7),

            # Parallèle
            ("Circuit en parallèle à 3 branches :\nReq = 3 Ω\nR1 = 6 Ω\nR2 = ?\nR3 = 6 Ω", 6),
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
        titre = QLabel("Résistance équivalente - Niveau 2")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police = QFont()
        police.setPointSize(28)
        titre.setFont(police)
        main_layout.addWidget(titre)

        # Consigne
        consigne = QLabel("Trouve la résistance inconnue dans chaque circuit.")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(consigne)

        # Questions
        for texte, reponse in self.questions:
            self.ajouter_question(main_layout, texte, reponse)

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

    def ajouter_question(self, layout, texte, bonne_reponse):
        bloc = QVBoxLayout()

        label = QLabel(texte)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("", 14))
        bloc.addWidget(label)

        input_field = QLineEdit()
        input_field.setPlaceholderText("Réponse en Ω")
        input_field.setFixedWidth(200)
        bloc.addWidget(input_field, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(bloc)

        self.questions_widgets.append((input_field, bonne_reponse))

    def valider(self):
        bonnes = 0

        for input_field, bonne_rep in self.questions_widgets:
            try:
                valeur = float(input_field.text())
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

