from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QMessageBox, QScrollArea
)

from niveau.definitions import Sujet

DOSSIER_IMAGES = "images/niveau/ohm/4/"

class CaseNumero(QPushButton):
    def __init__(self, index_case, parent_niveau):
        super().__init__("")
        self.index_case = index_case
        self.parent_niveau = parent_niveau
        self.setFixedSize(60, 45)
        self.clicked.connect(self.cliquer_case)

    def cliquer_case(self):
        self.parent_niveau.placer_numero(self.index_case)


class NiveauOhm4(QWidget):
    def __init__(self, retour_callback, update_niveau):
        super().__init__()

        self.update_niveau = update_niveau
        self.retour_callback = retour_callback
        self.numero_selectionne = None
        self.cases = []
        self.boutons_numeros = []


        self.circuits = [
            {
                "image": DOSSIER_IMAGES + "circuit_1.png",
                "bonne_position": 1,
            },
            {
                "image": DOSSIER_IMAGES + "circuit_2.png",
                "bonne_position": 2,
            },
            {
                "image": DOSSIER_IMAGES + "circuit_3.png",
                "bonne_position": 6,
            },
            {
                "image": DOSSIER_IMAGES + "circuit_4.png",
                "bonne_position": 4,
            },
            {
                "image": DOSSIER_IMAGES + "circuit_5.png",
                "bonne_position": 3,
            },
            {
                "image": DOSSIER_IMAGES + "circuit_6.png",
                "bonne_position": 5,
            }
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
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        titre = QLabel("Loi d'Ohm - niveau 4")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_titre = QFont()
        police_titre.setPointSize(28)
        titre.setFont(police_titre)
        main_layout.addWidget(titre)

        consigne = QLabel("Classe les circuits suivants en ordre croissant de résistance.")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        consigne.setWordWrap(True)
        main_layout.addWidget(consigne)

        grille = QGridLayout()
        grille.setHorizontalSpacing(20)
        grille.setVerticalSpacing(25)
        main_layout.addLayout(grille)

        for i, circuit in enumerate(self.circuits):
            bloc = self.creer_bloc_circuit(i, circuit["image"])
            ligne = i // 3
            colonne = i % 3
            grille.addLayout(bloc, ligne, colonne)

        ligne_numeros = QHBoxLayout()
        ligne_numeros.addStretch()

        for numero in range(1, 7):
            bouton = QPushButton(str(numero))
            bouton.setFixedSize(50, 40)
            bouton.clicked.connect(lambda checked=False, n=numero: self.selectionner_numero(n))
            self.boutons_numeros.append(bouton)
            ligne_numeros.addWidget(bouton)
            ligne_numeros.addSpacing(8)

        ligne_numeros.addStretch()
        main_layout.addLayout(ligne_numeros)

        ligne_ordre = QVBoxLayout()
        textes = [
            "1 : Plus petite résistance",
            "3 : Deuxième plus petite résistance",
            "3 : Troisième plus petite résistance",
            "4 : Quatrième plus petite résistance",
            "5 : Cinquième plus petite résistance",
            "6 : Plus grande résistance"
        ]

        for texte in textes:
            label = QLabel(texte)
            ligne_ordre.addWidget(label)

        main_layout.addLayout(ligne_ordre)

        boutons_bas = QHBoxLayout()

        bouton_valider = QPushButton("Valider")
        bouton_valider.setFixedWidth(180)
        bouton_valider.clicked.connect(self.valider_reponses)

        bouton_reset = QPushButton("Effacer")
        bouton_reset.setFixedWidth(180)
        bouton_reset.clicked.connect(self.effacer_cases)

        bouton_retour = QPushButton("Retour")
        bouton_retour.setFixedWidth(180)
        bouton_retour.clicked.connect(self.retour)

        boutons_bas.addStretch()
        boutons_bas.addWidget(bouton_valider)
        boutons_bas.addSpacing(15)
        boutons_bas.addWidget(bouton_reset)
        boutons_bas.addSpacing(15)
        boutons_bas.addWidget(bouton_retour)
        boutons_bas.addStretch()

        main_layout.addLayout(boutons_bas)

    def creer_bloc_circuit(self, index_circuit, image_path):
        bloc = QVBoxLayout()
        bloc.setSpacing(10)

        image_label = QLabel()
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            image_label.setPixmap(
                pixmap.scaledToWidth(380, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            image_label.setText("Image introuvable : " + image_path)

        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bloc.addWidget(image_label)

        ligne_case = QHBoxLayout()
        ligne_case.addStretch()

        texte_numero = QLabel("Numéro :")
        ligne_case.addWidget(texte_numero)
        ligne_case.addSpacing(8)

        case = CaseNumero(index_circuit, self)
        self.cases.append(case)
        ligne_case.addWidget(case)

        ligne_case.addStretch()
        bloc.addLayout(ligne_case)

        return bloc

    def selectionner_numero(self, numero):
        self.numero_selectionne = numero

        for bouton in self.boutons_numeros:
            if bouton.text() == str(numero):
                bouton.setStyleSheet("border: 2px solid yellow;")
            else:
                bouton.setStyleSheet("")

    def placer_numero(self, index_case):
        if self.numero_selectionne is None:
            return

        # enlève ce numéro ailleurs si déjà utilisé
        for case in self.cases:
            if case.text() == str(self.numero_selectionne):
                case.setText("")

        self.cases[index_case].setText(str(self.numero_selectionne))

    def effacer_cases(self):
        for case in self.cases:
            case.setText("")

        self.numero_selectionne = None

        for bouton in self.boutons_numeros:
            bouton.setStyleSheet("")

    def valider_reponses(self):
        # vérifier si toutes les cases sont remplies
        for case in self.cases:
            if case.text() == "":
                QMessageBox.warning(self, "Résultat", "Il manque des numéros à placer.")
                return

        bonne_reponses = 0


        for i, circuit in enumerate(self.circuits):
            numero_place = int(self.cases[i].text())
            if numero_place == circuit["bonne_position"]:
                bonne_reponses += 1

        self.update_niveau(Sujet.Ohm, 4, bonne_reponses)
        if bonne_reponses == len(self.circuits):
            QMessageBox.information(self, "Résultat", "Bravo ! L'ordre est correct.")
        else:
            QMessageBox.warning(
                self,
                "Résultat",
                f"Tu as {bonne_reponses} bonne(s) position(s) sur {len(self.circuits)}."
            )

    def retour(self):
        if self.retour_callback is not None:
            self.retour_callback()