from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QScrollArea, QRadioButton, QButtonGroup, QComboBox, QLineEdit
)


class NiveauKirchoff4(QWidget):
    def __init__(self, retour_callback, update_niveau):
        super().__init__()

        self.update_niveau = update_niveau
        self.retour_callback = retour_callback
        self.questions_widgets = []

        # affichage bouton aide
        layout_exterieur = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_layout.addStretch()

        aide = QPushButton("Aide")
        aide.clicked.connect(self.ouvrir_aide)

        top_layout.addWidget(aide)
        layout_exterieur.addLayout(top_layout)

        self.questions = [
            {
                "question": "Coche un noeud valide",
                "type": "noeud",
                "reponse": "B",
            },
            {
                "question": "Coche deux mailles valide",
                "type": "mailles",
                "reponse": ["AFEBA", "EDCBAFE"]
            },
            {
                "question": "A partir dès mailles trouvées au numero précédent\n écrit les équations",
                "type": "equation",
                "reponse": ["-3I1+6I2=0", "-8I3-3I1-11=0"]
            },
            {
                "question": "À partir de la maille trouvée au numero précédent\n"
                            " isoler I\u2083 et I\u2081",
                "type": "isoler",
                "reponse": ["I\u2083 = -0,375*I\u2081 - 1,375", "I\u2081 = 2I\u2082"]
            },
            {
                "question": "À partir de la loi des noeuds Isole I\u2082\n"
                            " indice utilise les équation trouvées au numéros précédents",
                "type": "isolerNoeud",
                "reponse": "I\u2082 = 1,375*I\u2081+ 1,375",
            },
            {
                "question": "Déterminer I\u2082 ",
                "type": "reponse",
                "reponse": "-0,5"
            }
        ]

        main_layout = QVBoxLayout()

        titre = QLabel("Loi de Kirchoff - niveau 4 ")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police = QFont()
        police.setPointSize(28)
        titre.setFont(police)
        main_layout.addWidget(titre)

        consigne = QLabel("Déterminez le courant circulant dans chaque branche du circuit.")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(consigne)

        image_circuit = QLabel(pixmap=QPixmap("images/niveau/kirchoff/4/circuit_1.png"))
        image_circuit.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(image_circuit)

        for question in self.questions:
            self.ajouter_question(
                main_layout,
                "image/niveau/kirchoff/4/circuit_1.png",
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

    @property
    def questions_widgets(self):
        return self._questions_widgets

    @questions_widgets.setter
    def questions_widgets(self, question):
        self._questions_widgets = question

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
    def questions(self):
        return self._questions

    @questions.setter
    def questions(self, questions):
        self._questions = questions

    def ajouter_question(self, main_layout, image_path, texte_question, type_question, bonne_reponse):
    def ajouter_question(self, main_layout, texte_question, type_question, bonne_reponse):
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

        if type_question == "noeud":
            btn_a = QRadioButton("A")
            btn_b = QRadioButton("B")
            btn_c = QRadioButton("C")

            groupe = QButtonGroup(self)
            groupe.addButton(btn_a)
            groupe.addButton(btn_b)
            groupe.addButton(btn_c)

            groupe.setExclusive(True)

            ligne_question.addWidget(btn_a)
            ligne_question.addWidget(btn_b)
            ligne_question.addWidget(btn_c)

        elif type_question == "mailles":

            choix1 = ["ABEF", "ABC", "AFEBA", "FEDF"]
            choix2 = ["EDCBAFE", "FEBC", "AFDC", "FEDF"]

            combo = QComboBox()
            combo2 = QComboBox()

            for i in choix1:
                combo.addItem(i)
            for i in choix2:
                combo2.addItem(i)

            ligne_question.addWidget(combo)
            ligne_question.addWidget(combo2)

        elif type_question == "equation":
            champ_reponse1 = QLineEdit()
            champ_reponse2 = QLineEdit()

            # champ_reponse1.setInputMask("-9\I\u2081+9\I\u2083=0;_")
            champ_reponse2.setInputMask("XXI\u2083XXI\u2081XXX=0;_")

            ligne_question.addWidget(champ_reponse1)
            ligne_question.addWidget(champ_reponse2)

        elif type_question == "isoler":

            choix1 = ["I\u2083 = -0,375*I\u2081 - 1,375", "I\u2083 = +0,375*I\u2081 + 1,375"]
            choix2 = ["I\u2081 = 0,5I\u2082", "I\u2081 = -2I\u2082", "I\u2081 = 2I\u2082"]

            combo1 = QComboBox()
            combo2 = QComboBox()

            for i in choix1:
                combo1.addItem(i)
            for i in choix2:
                combo2.addItem(i)

            ligne_question.addWidget(combo1)
            ligne_question.addWidget(combo2)

        elif type_question == "isolerNoeud":
            choix = ["I\u2082 = 1,375*I\u2081+ 1,375", "I\u2082 = -1,375*I\u2081- 1,375",
                     "I\u2082 = -0,375*I\u2081+ 1,375"]

            combo = QComboBox()

            for i in choix:
                combo.addItem(i)

            ligne_question.addWidget(combo)
        elif type_question == "reponse":
            champ_reponse1 = QLineEdit()
            ligne_question.addWidget(champ_reponse1)

        if type_question == "noeud":
            self.questions_widgets.append((groupe,bonne_reponse,"radio"))
        elif type_question == "mailles":
            self.questions_widgets.append(((combo,combo2), bonne_reponse,"combo2"))
        elif type_question == "equation":
            self.questions_widgets.append(((champ_reponse1,champ_reponse2),bonne_reponse,"lineedit2"))
        elif type_question == "isoler":
            self.questions_widgets.append(((combo1,combo2), bonne_reponse,"combo2"))
        elif type_question == "isolerNoeud":
            self.questions_widgets.append((combo, bonne_reponse,"combo"))
        elif type_question == "reponse":
            self.questions_widgets.append((champ_reponse1,bonne_reponse,"lineedit"))

        bloc.addLayout(ligne_question)
        bloc.addWidget(image_label)

        ligne_question.addStretch()
        ligne_question.addSpacing(10)
        ligne_question.addSpacing(5)
        ligne_question.addStretch()

        main_layout.addLayout(bloc)

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

        for groupe, bonne_rep in self.questions_widgets:
            btn = groupe.checkedButton()
            if btn and btn.text() == bonne_rep:
                bonnes += 1

        QMessageBox.information(
            self,
            "Résultat",
            f"{bonnes} bonnes réponses sur {len(self.questions_widgets)}"
        )

    def retour(self):
        if self.retour_callback:
            self.retour_callback()
