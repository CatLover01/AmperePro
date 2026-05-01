from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu, QMessageBox, QScrollArea


class TrouButton(QPushButton):
    def __init__(self, options):
        super().__init__("____________")
        self.options = options
        self.reponse_choisie = ""
        self.setMinimumWidth(220)
        self.clicked.connect(self.ouvrir_menu)

    def ouvrir_menu(self):
        menu = QMenu()

        for option in self.options:
            action = QAction(option, self)
            action.triggered.connect(lambda checked=False, texte=option: self.choisir_reponse(texte))
            menu.addAction(action)

        menu.exec(self.mapToGlobal(self.rect().bottomLeft()))

    def choisir_reponse(self, texte):
        self.reponse_choisie = texte
        self.setText(texte)


class NiveauOhm1(QWidget):
    def __init__(self, retour_callback=None):
        super().__init__()

        self.retour_callback = retour_callback
        self.bonnes_reponses = {}

        layout_exterieur = QVBoxLayout()
        layout_exterieur.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout_exterieur)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout_exterieur.addWidget(scroll)

        contenu = QWidget()
        contenu.setMaximumWidth(800)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        contenu.setLayout(main_layout)
        scroll.setWidget(contenu)

        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(15)

        titre = QLabel("Loi d'Ohm - Niveau 1")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_titre = QFont()
        police_titre.setPointSize(40)
        titre.setFont(police_titre)
        main_layout.addWidget(titre)

        formule = QLabel("U = R × I")
        formule.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_formule = QFont()
        police_formule.setPointSize(36)
        police_formule.setBold(True)
        formule.setFont(police_formule)
        main_layout.addWidget(formule)

        main_layout.addSpacing(20)

        options_noms = ["Tension", "Résistance", "Intensité du courant"]
        options_unites = ["Volt (V)", "Ohm (Ω)", "Ampère (A)"]
        options_series = [
            "U = U1 + U2 + U3",
            "R = R1 + R2 + R3",
            "I = I1 = I2 = I3",
            "U = U1 = U2 = U3",
            "1/R = 1/R1 + 1/R2 + 1/R3",
            "I = I1 + I2 + I3"
        ]
        options_paralleles = [
            "U = U1 + U2 + U3",
            "R = R1 + R2 + R3",
            "I = I1 = I2 = I3",
            "U = U1 = U2 = U3",
            "1/R = 1/R1 + 1/R2 + 1/R3",
            "I = I1 + I2 + I3"
        ]

        self.creer_section(main_layout, "U", "Tension", "Volt (V)", "U = U1 + U2 + U3", "U = U1 = U2 = U3",
                           options_noms, options_unites, options_series, options_paralleles)

        self.creer_section(main_layout, "R", "Résistance", "Ohm (Ω)", "R = R1 + R2 + R3", "1/R = 1/R1 + 1/R2 + 1/R3",
                           options_noms, options_unites, options_series, options_paralleles)

        self.creer_section(main_layout, "I", "Intensité du courant", "Ampère (A)", "I = I1 = I2 = I3", "I = I1 + I2 + I3",
                           options_noms, options_unites, options_series, options_paralleles)

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

    def creer_section(self, main_layout, lettre, bonne_nom, bonne_unite, bonne_serie, bonne_parallele,
                      options_noms, options_unites, options_series, options_paralleles):
        titre_section = QLabel(lettre + " :")
        police = QFont()
        police.setPointSize(16)
        police.setBold(True)
        titre_section.setFont(police)

        titre_section.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(titre_section)

        bouton_nom = TrouButton(options_noms)
        self.bonnes_reponses[bouton_nom] = bonne_nom
        self.ajouter_ligne(main_layout, "Nom :", bouton_nom)

        bouton_unite = TrouButton(options_unites)
        self.bonnes_reponses[bouton_unite] = bonne_unite
        self.ajouter_ligne(main_layout, "Unité :", bouton_unite)

        bouton_serie = TrouButton(options_series)
        self.bonnes_reponses[bouton_serie] = bonne_serie
        self.ajouter_ligne(main_layout, "Formule en série :", bouton_serie)

        bouton_parallele = TrouButton(options_paralleles)
        self.bonnes_reponses[bouton_parallele] = bonne_parallele
        self.ajouter_ligne(main_layout, "Formule en parallèle :", bouton_parallele)

        main_layout.addSpacing(10)

    def ajouter_ligne(self, main_layout, texte, bouton):
        ligne = QHBoxLayout()

        label = QLabel(texte)
        label.setFixedWidth(180)
        bouton.setFixedWidth(260)

        ligne.addStretch()
        ligne.addWidget(label)
        ligne.addSpacing(20)
        ligne.addWidget(bouton)
        ligne.addStretch()

        main_layout.addLayout(ligne)

    def valider_reponses(self):
        total = len(self.bonnes_reponses)
        bonnes = 0

        for bouton, bonne_reponse in self.bonnes_reponses.items():
            if bouton.reponse_choisie == bonne_reponse:
                bonnes += 1

        if bonnes == total:
            QMessageBox.information(self, "Résultat", "Bravo ! Toutes les réponses sont bonnes.")
        else:
            QMessageBox.warning(self, "Résultat", f"Tu as {bonnes} bonne(s) réponse(s) sur {total}.")

    def retour(self):
        if self.retour_callback is not None:
            self.retour_callback()