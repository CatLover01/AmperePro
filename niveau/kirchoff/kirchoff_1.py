from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, \
    QScrollArea, QCheckBox

from niveau.definitions import Sujet


class NiveauKirchoff1(QWidget):
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

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout_exterieur.addWidget(scroll)

        contenu = QWidget()
        contenu.setMaximumWidth(900)
        main_layout = QVBoxLayout()
        contenu.setLayout(main_layout)
        scroll.setWidget(contenu)

        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # affichage principale
        titre = QLabel("kirchoff - niveau 1")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_titre = QFont()
        police_titre.setPointSize(32)
        titre.setFont(police_titre)
        main_layout.addWidget(titre)

        formule = QLabel("I\u2081 = I\u2082 + I\u2083")
        formule.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_formule = QFont()
        police_formule.setPointSize(36)
        police_formule.setBold(True)
        formule.setFont(police_formule)
        main_layout.addWidget(formule)

        consigne = QLabel("Trouver les différents noeud dans les circuits")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(consigne)

        main_layout.addSpacing(10)

        #question 1
        lettre = ["A", "B", "C", "D", "E", "F"]
        q1_layout = QVBoxLayout()

        circuit1 = QLabel(pixmap=QPixmap("images/niveau/kirchoff/1/circuit_1.png"))
        circuit1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q1_layout.addWidget(circuit1)

        bonne_reponse_q1 = ["B", "E"]

        for i in range(6):
            layout_choix1 = QHBoxLayout()  # revenir dessus
            choix_de_reponse = QCheckBox(lettre[i])
            layout_choix1.addWidget(choix_de_reponse)
            q1_layout.addLayout(layout_choix1)

            self.reponses.append((choix_de_reponse, lettre[i] in bonne_reponse_q1))
        main_layout.addLayout(q1_layout)

        # question 2
        q2_layout = QVBoxLayout()

        circuit2 = QLabel(pixmap=QPixmap("images/niveau/kirchoff/1/circuit_2.png"))
        circuit2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q2_layout.addWidget(circuit2)

        bonne_reponse_q2 = ["B", "D"]

        for i in range(4):
            layout_choix2 = QHBoxLayout()  # revenir dessus
            choix_de_reponse = QCheckBox(lettre[i])
            layout_choix2.addWidget(choix_de_reponse)
            q2_layout.addLayout(layout_choix2)

            self.reponses.append((choix_de_reponse, lettre[i] in bonne_reponse_q2))
        main_layout.addLayout(q2_layout)

        # bouton valider
        main_layout.addSpacing(20)

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

    #validation des reponses
    def valider_reponses(self):
        bonne_reponses = 0
        total = len(self.reponses)

        for checkbox, bonne_reponse in self.reponses:
            if checkbox.isChecked() == bonne_reponse:
                bonne_reponses += 1

        self.update_niveau(Sujet.Kirchoff, 1, bonne_reponses)
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
