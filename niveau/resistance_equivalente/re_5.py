from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QScrollArea, QLineEdit
)


class NiveauRE5(QWidget):
    def __init__(self, retour_callback=None, update_niveau=None):
        super().__init__()

        self.retour_callback = retour_callback
        self.update_niveau = update_niveau
        self.questions_widgets = []

        self.questions = [
            ("images/niveau/resistance_equivalente/5/circuit_1.png", 5.625)
        ]

        layout_exterieur = QVBoxLayout()
        self.setLayout(layout_exterieur)

        # affichage bouton aide
        top_layout = QHBoxLayout()
        top_layout.addStretch()

        aide = QPushButton("Aide")
        aide.clicked.connect(self.ouvrir_aide)

        top_layout.addWidget(aide)
        layout_exterieur.addLayout(top_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout_exterieur.addWidget(scroll)

        contenu = QWidget()
        scroll.setWidget(contenu)

        main_layout = QVBoxLayout()
        contenu.setLayout(main_layout)

        titre = QLabel("Résistance équivalente - Niveau 5")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)

        police = QFont()
        police.setPointSize(28)
        titre.setFont(police)

        main_layout.addWidget(titre)

        consigne = QLabel("Calcule la résistance équivalente du circuit.")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(consigne)

        for image_path, reponse in self.questions:
            self.ajouter_question(main_layout, image_path, reponse)

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
            image_label.setPixmap(
                pixmap.scaledToWidth(
                    800,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        else:
            image_label.setText("Image introuvable : " + image_path)

        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bloc.addWidget(image_label)

        question = QLabel("Quelle est la résistance équivalente Req de ce circuit ?")
        question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        question.setFont(QFont("", 14))
        bloc.addWidget(question)

        ligne_reponse = QHBoxLayout()

        label = QLabel("Req =")
        champ = QLineEdit()
        champ.setPlaceholderText("Réponse en Ω")
        champ.setFixedWidth(180)
        unite = QLabel("Ω")

        ligne_reponse.addStretch()
        ligne_reponse.addWidget(label)
        ligne_reponse.addSpacing(8)
        ligne_reponse.addWidget(champ)
        ligne_reponse.addSpacing(8)
        ligne_reponse.addWidget(unite)
        ligne_reponse.addStretch()

        bloc.addLayout(ligne_reponse)
        layout.addLayout(bloc)

        self.questions_widgets.append((champ, bonne_reponse))

    # ouvrir la documentation
    def ouvrir_aide(self):
        from docs import DocumentationWindow
        from PySide6.QtCore import QFile, QTextStream, Qt

        parent_window = self.window()

        self.fenetre_doc = DocumentationWindow(parent_window)
        self.fenetre_doc.setWindowModality(Qt.WindowModality.NonModal)

        style_docu = QFile("stylesheet/documentation.qss")
        if style_docu.open(QFile.OpenModeFlag.ReadOnly):
            stream_docu = QTextStream(style_docu)
            self.fenetre_doc.setStyleSheet(stream_docu.readAll())
            style_docu.close()

        self.fenetre_doc.show()
        self.fenetre_doc.raise_()

    def valider(self):
        bonnes = 0

        for champ, bonne_reponse in self.questions_widgets:
            try:
                valeur = float(champ.text().replace(",", "."))
                if abs(valeur - bonne_reponse) < 0.05:
                    bonnes += 1
            except ValueError:
                pass

        QMessageBox.information(
            self,
            "Résultat",
            f"{bonnes} bonne réponse sur {len(self.questions_widgets)}"
        )

        if self.update_niveau is not None:
            self.update_niveau(bonnes, len(self.questions_widgets))

    def retour(self):
        if self.retour_callback:
            self.retour_callback()