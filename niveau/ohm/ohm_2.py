import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QScrollArea

from niveau.definitions import Sujet


class NiveauOhm2(QWidget):
    def __init__(self, retour_callback, update_niveau):
        super().__init__()

        self.update_niveau = update_niveau
        self.retour_callback = retour_callback
        self.reponses = []

        layout_exterieur = QVBoxLayout()
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

        titre = QLabel("Loi d'Ohm - niveau 2")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_titre = QFont()
        police_titre.setPointSize(32)
        titre.setFont(police_titre)
        main_layout.addWidget(titre)

        formule = QLabel("U = R × I")
        formule.setAlignment(Qt.AlignmentFlag.AlignCenter)
        police_formule = QFont()
        police_formule.setPointSize(36)
        police_formule.setBold(True)
        formule.setFont(police_formule)
        main_layout.addWidget(formule)

        consigne = QLabel("Trouve la bonne valeur demandée pour chaque circuit.")
        consigne.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(consigne)

        main_layout.addSpacing(10)

        self.questions = self.generer_questions()

        for i in range(5):
            question = self.questions[i]
            self.ajouter_question(
                main_layout,
                i + 1,
                question["type"],
                question["u"],
                question["r"],
                question["i"]
            )

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

    def generer_questions(self):
        questions = []

        for _ in range(5):
            type_question = random.choice(["U", "R", "I"])

            resistance = random.randint(1, 10)
            intensite = random.randint(1, 10)
            tension = resistance * intensite

            question = {
                "type": type_question,
                "u": tension,
                "r": resistance,
                "i": intensite
            }

            questions.append(question)

        return questions

    def ajouter_question(self, main_layout, numero, type_question, tension, resistance, intensite):
        bloc = QVBoxLayout()

        titre_question = QLabel("Question " + str(numero))
        police_question = QFont()
        police_question.setPointSize(16)
        police_question.setBold(True)
        titre_question.setFont(police_question)
        bloc.addWidget(titre_question)

        if type_question == "I":
            enonce = QLabel(
                "Dans un circuit, nous avons une source de "
                + str(tension)
                + " V et une résistance de "
                + str(resistance)
                + " Ω. Quelle est l'intensité du courant ?"
            )
            bonne_reponse = intensite
            unite = "A"

        elif type_question == "R":
            enonce = QLabel(
                "Dans un circuit, nous avons une source de "
                + str(tension)
                + " V et une intensité de courant de "
                + str(intensite)
                + " A. Quelle est la résistance ?"
            )
            bonne_reponse = resistance
            unite = "Ω"

        else:
            enonce = QLabel(
                "Dans un circuit, nous avons une résistance de "
                + str(resistance)
                + " Ω et une intensité de courant de "
                + str(intensite)
                + " A. Quelle est la tension ?"
            )
            bonne_reponse = tension
            unite = "V"

        enonce.setWordWrap(True)
        bloc.addWidget(enonce)

        ligne_reponse = QHBoxLayout()

        label_reponse = QLabel("Réponse :")
        champ_reponse = QLineEdit()
        champ_reponse.setPlaceholderText("Entre ta réponse")
        champ_reponse.setFixedWidth(220)

        ligne_reponse.addWidget(label_reponse)
        ligne_reponse.addSpacing(10)
        ligne_reponse.addWidget(champ_reponse)
        ligne_reponse.addWidget(QLabel(unite))
        ligne_reponse.addStretch()

        bloc.addLayout(ligne_reponse)

        self.reponses.append((champ_reponse, bonne_reponse))

        main_layout.addLayout(bloc)
        main_layout.addSpacing(15)

    def valider_reponses(self):
        bonne_reponses = 0
        total = len(self.reponses)

        for champ, bonne_reponse in self.reponses:
            texte = champ.text().strip().replace(",", ".")

            try:
                valeur = float(texte)
                if valeur == bonne_reponse:
                    bonne_reponses += 1
            except ValueError:
                pass

        self.update_niveau(Sujet.Ohm, 2, bonne_reponses)
        if bonne_reponses == total:
            QMessageBox.information(self, "Résultat", "Bravo ! Toutes les réponses sont bonne_reponses.")
        else:
            QMessageBox.warning(
                self,
                "Résultat",
                "Tu as " + str(bonne_reponses) + " bonne(s) réponse(s) sur " + str(total) + "."
            )

    def retour(self):
        if self.retour_callback is not None:
            self.retour_callback()