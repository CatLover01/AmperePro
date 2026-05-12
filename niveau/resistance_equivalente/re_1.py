from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QScrollArea, QRadioButton, QButtonGroup
)

from niveau.definitions import Sujet


class ChoixCircuit(QWidget):
    def __init__(self):
        super().__init__()

        self.choix = None

        layout = QHBoxLayout()
        layout.setSpacing(25)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.btn_serie = QRadioButton("Série")
        self.btn_parallele = QRadioButton("Parallèle")
        self.btn_mixte = QRadioButton("Mixte")

        self.groupe = QButtonGroup(self)
        self.groupe.addButton(self.btn_serie)
        self.groupe.addButton(self.btn_parallele)
        self.groupe.addButton(self.btn_mixte)
        self.groupe.setExclusive(True)

        self.btn_serie.toggled.connect(self.mettre_a_jour_choix)
        self.btn_parallele.toggled.connect(self.mettre_a_jour_choix)
        self.btn_mixte.toggled.connect(self.mettre_a_jour_choix)

        self.btn_serie.setFont(QFont("", 14))
        self.btn_parallele.setFont(QFont("", 14))
        self.btn_mixte.setFont(QFont("", 14))

        layout.addWidget(self.btn_serie)
        layout.addWidget(self.btn_parallele)
        layout.addWidget(self.btn_mixte)

    def mettre_a_jour_choix(self):
        if self.btn_serie.isChecked():
            self.choix = "série"
        elif self.btn_parallele.isChecked():
            self.choix = "parallèle"
        elif self.btn_mixte.isChecked():
            self.choix = "mixte"
        else:
            self.choix = None

    def get_choix(self):
        return self.choix


class NiveauRE1(QWidget):
    def __init__(self, retour_callback, update_niveau):
        super().__init__()

        self.update_niveau = update_niveau
        self.retour_callback = retour_callback
        self.questions_widgets = []
        self.fenetre_doc = None

        self.questions = [
            ("images/niveau/resistance_equivalente/1/circuit_1.png", "série"),
            ("images/niveau/resistance_equivalente/1/circuit_2.png", "série"),
            ("images/niveau/resistance_equivalente/1/circuit_3.png", "parallèle"),
            ("images/niveau/resistance_equivalente/1/circuit_4.png", "série"),
            ("images/niveau/resistance_equivalente/1/circuit_5.png", "mixte"),
            ("images/niveau/resistance_equivalente/1/circuit_6.png", "série"),
        ]

        layout_exterieur = QVBoxLayout()
        self.setLayout(layout_exterieur)

        # === BOUTON AIDE EN HAUT ===
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

        titre = QLabel("Résistance équivalente - niveau 1")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police = QFont()
        police.setPointSize(28)
        titre.setFont(police)
        main_layout.addWidget(titre)

        consigne = QLabel("Identifie si chaque circuit est en série, en parallèle ou mixte.")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(consigne)

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

        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bloc.addWidget(image_label)

        choix_widget = ChoixCircuit()
        bloc.addWidget(choix_widget)

        layout.addLayout(bloc)

        self.questions_widgets.append((choix_widget, bonne_reponse))

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
        self.fenetre_doc.activateWindow()

    def valider(self):
        bonne_reponses = 0

        for widget, bonne_rep in self.questions_widgets:
            if widget.get_choix() == bonne_rep:
                bonne_reponses += 1

        self.update_niveau(Sujet.Resistance, 1, bonne_reponses)
        QMessageBox.information(
            self,
            "Résultat",
            f"{bonne_reponses} bonnes réponses sur {len(self.questions_widgets)}"
        )

    def retour(self):
        if self.retour_callback:
            self.retour_callback()