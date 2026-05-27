from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QScrollArea, QGridLayout
)


class NiveauKirchoff5(QWidget):
    def __init__(self, retour_callback, update_niveau):
        super().__init__()

        self.update_niveau = update_niveau
        self.retour_callback = retour_callback
        self.reponses = []
        self.fenetre_doc = None

        # affichage bouton aide
        layout_exterieur = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_layout.addStretch()

        aide = QPushButton("Aide")
        aide.clicked.connect(self.ouvrir_aide)

        top_layout.addWidget(aide)
        layout_exterieur.addLayout(top_layout)

        self.setLayout(layout_exterieur)

        # interface principale du niveau
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

        titre = QLabel("Loi de Kirchoff - niveau 5")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_titre = QFont()
        police_titre.setPointSize(30)
        titre.setFont(police_titre)
        main_layout.addWidget(titre)

        consigne = QLabel("Identifier le courant dans les branches du circuit")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        consigne.setWordWrap(True)
        main_layout.addWidget(consigne)

        image_circuit = QLabel(pixmap=QPixmap("images/niveau/kirchoff/5/circuit_1.png"))
        image_circuit.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(image_circuit)

        # question 1
        layout_reponse = QGridLayout()

        self.reponse_i1 = QLineEdit()
        self.reponse_i2 = QLineEdit()
        self.reponse_i3 = QLineEdit()

        self.reponse_i1.setInputMask("9;_")
        self.reponse_i2.setInputMask("9;_")
        self.reponse_i3.setInputMask("9;_")

        i1 = QLabel("I\u2081 = ")
        i2 = QLabel("I\u2082 = ")
        i3 = QLabel("I\u2083 = ")

        layout_reponse.addWidget(i1, 0, 0)
        layout_reponse.addWidget(i2, 1, 0)
        layout_reponse.addWidget(i3, 2, 0)

        layout_reponse.addWidget(self.reponse_i1, 0, 1)
        layout_reponse.addWidget(self.reponse_i2, 1, 1)
        layout_reponse.addWidget(self.reponse_i3, 2, 1)

        main_layout.addLayout(layout_reponse)
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

    @property
    def reponses(self):
        return self._reponses

    @reponses.setter
    def reponses(self, reponses):
        self._reponses = reponses

    @property
    def update_niveau(self):
        return self._update_niveau

    @update_niveau.setter
    def update_niveau(self, update_niveau):
        self._update_niveau = update_niveau

    @property
    def retour_callback(self):
        return self._retour_callback

    @retour_callback.setter
    def retour_callback(self, retour_callback):
        self._retour_callback = retour_callback

    @property
    def fenetre_doc(self):
        return self._fenetre_doc

    @fenetre_doc.setter
    def fenetre_doc(self, fenetre_doc):
        self._fenetre_doc = fenetre_doc

    @property
    def reponse_i1(self):
        return self._fenetre_i1

    @reponse_i1.setter
    def reponse_i1(self, reponse_i1):
        self._fenetre_i1 = reponse_i1

    @property
    def reponse_i2(self):
        return self._reponse_i2

    @reponse_i2.setter
    def reponse_i2(self, reponse_i2):
        self._reponse_i2 = reponse_i2

    @property
    def reponse_i3(self):
        return self._reponse_i3

    @reponse_i3.setter
    def reponse_i3(self, reponse_i3):
        self._reponse_i3 = reponse_i3

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

    # validation des reponses
    def valider_reponses(self):
        bonne_reponses = 0
        total = 3
        if self.reponse_i1.text() == "1":
            bonne_reponses += 1
        if self.reponse_i2.text() == "0":
            bonne_reponses += 1
        if self.reponse_i3.text() == "1":
            bonne_reponses += 1
        else:
            bonne_reponses += 0

        #affichage du totales de bonne rep
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
