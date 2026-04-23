from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QScrollArea
)


class ChoixCircuit(QWidget):
    def __init__(self):
        super().__init__()

        self.choix = None

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.btn_serie = QPushButton("Série")
        self.btn_parallele = QPushButton("Parallèle")
        self.btn_mixte = QPushButton("Série + Parallèle")

        self.btn_serie.clicked.connect(self.select_serie)
        self.btn_parallele.clicked.connect(self.select_parallele)
        self.btn_mixte.clicked.connect(self.select_mixte)

        layout.addWidget(self.btn_serie)
        layout.addWidget(self.btn_parallele)
        layout.addWidget(self.btn_mixte)

    def reset_styles(self):
        self.btn_serie.setStyleSheet("")
        self.btn_parallele.setStyleSheet("")
        self.btn_mixte.setStyleSheet("")

    def select_serie(self):
        self.choix = "serie"
        self.reset_styles()
        self.btn_serie.setStyleSheet("border: 2px solid yellow;")

    def select_parallele(self):
        self.choix = "parallele"
        self.reset_styles()
        self.btn_parallele.setStyleSheet("border: 2px solid yellow;")

    def select_mixte(self):
        self.choix = "mixte"
        self.reset_styles()
        self.btn_mixte.setStyleSheet("border: 2px solid yellow;")

    def get_choix(self):
        return self.choix


class NiveauRE1(QWidget):
    def __init__(self, retour_callback=None):
        super().__init__()

        self.retour_callback = retour_callback
        self.questions_widgets = []

        self.questions = [
            ("images/niveau/Résistance équivalente/1/RE-circuit1.png", "serie"),
            ("images/niveau/Résistance équivalente/1/RE-circuit2.png", "serie"),
            ("images/niveau/Résistance équivalente/1/RE-circuit3.png", "mixte"),
            ("images/niveau/Résistance équivalente/1/RE-circuit4.png", "mixte"),
            ("images/niveau/Résistance équivalente/1/RE-circuit5.png", "mixte"),
            ("images/niveau/Résistance équivalente/1/RE-circuit6.png", "mixte"),
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

        titre = QLabel("Resistance_equivalente - Niveau 1")
        titre.setAlignment(Qt.AlignCenter)
        police = QFont()
        police.setPointSize(28)
        titre.setFont(police)
        main_layout.addWidget(titre)

        consigne = QLabel("Identifie si chaque circuit est en série, en parallèle ou mixte.")
        consigne.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(consigne)

        rappel = QLabel(
            "Série : Req = R1 + R2 + ...\n"
            "Parallèle : 1/Req = 1/R1 + 1/R2 + ...\n"
            "Mixte : combinaison série et parallèle"
        )
        rappel.setAlignment(Qt.AlignCenter)
        police_rappel = QFont()
        police_rappel.setPointSize(16)
        rappel.setFont(police_rappel)
        main_layout.addWidget(rappel)

        for path, bonne_rep in self.questions:
            self.ajouter_question(main_layout, path, bonne_rep)

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

        image_label = QLabel()
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            image_label.setPixmap(pixmap.scaledToWidth(700))
        else:
            image_label.setText("Image introuvable : " + image_path)

        image_label.setAlignment(Qt.AlignCenter)
        bloc.addWidget(image_label)

        choix_widget = ChoixCircuit()
        bloc.addWidget(choix_widget)

        layout.addLayout(bloc)

        self.questions_widgets.append((choix_widget, bonne_reponse))

    def valider(self):
        bonnes = 0

        for widget, bonne_rep in self.questions_widgets:
            if widget.get_choix() == bonne_rep:
                bonnes += 1

        QMessageBox.information(
            self,
            "Résultat",
            f"{bonnes} bonnes réponses sur {len(self.questions_widgets)}"
        )

    def retour(self):
        if self.retour_callback:
            self.retour_callback()