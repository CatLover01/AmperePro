from PySide6.QtCore import QFile, QTextStream
from PySide6.QtGui import Qt, QIcon, QPixmap, QFont, QAction, QMovie
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QGraphicsView, QMenu, QProgressBar, QDialog, QInputDialog
from enum import Enum

from popup import OuvertureFenetre, Popup
from a_propos import AProposWindow
from docs import DocumentationWindow
from sauvegarde import Sauvegarde, CircuitLibre
from circuit_libre import Circuit, GraphicsView
from niveau.ohm_1 import NiveauOhm1
from niveau.ohm_2 import NiveauOhm2
from niveau.ohm_3 import NiveauOhm3

class Mode(Enum):
    Libre = 1
    Niveau = 2

class Sujet(Enum):
    Ohm = "Loi d'ohm"
    Resistance = "Résistance équivalente"
    Kirchoff = "Loi de Kirchoff"


class AmperePro(QMainWindow):
    def __init__(self):
        super().__init__()

        style_main = QFile("StyleSheet/StyleMainWindow.qss")
        if style_main.open(QFile.OpenModeFlag.ReadOnly):
            stream = QTextStream(style_main)
            self.setStyleSheet(stream.readAll())
            style_main.close()

        self.setWindowTitle("AmpèrePro")
        self.setWindowIcon(QIcon("images/interface/AmperePro_fond_bleu.png"))
        self.setMinimumSize(500, 500)

        self.title = None
        self.fenetre_doc = None
        self.popups = None
        self.init_main_window()

        self.data = Sauvegarde()
        self.fenetre_a_propos = AProposWindow()

        # Menus
        self.menu_bar = self.menuBar()
        self.menu_aide = QMenu("Aide")

        # À propos
        a_propos_action = QAction("À Propos", self)
        a_propos_action.setIcon(QIcon("images/menubar/a_propos.png"))
        a_propos_action.triggered.connect(self.ouvrir_a_propos)
        self.menu_aide.addAction(a_propos_action)

        # Documentation
        documentation_action = QAction("Documentation", self)
        documentation_action.setIcon(QIcon("images/menubar/docu.png"))
        documentation_action.triggered.connect(self.ouvrir_documentation)
        self.menu_aide.addAction(documentation_action)

        self.menu_bar.addMenu(self.menu_aide)

        # Quitter
        self.quitter_action = QAction("Quitter", self)
        self.quitter_action.triggered.connect(self.close)
        self.menu_bar.addAction(self.quitter_action)

        self.graphic_view = QGraphicsView()
        self.nouveau_circuit = None
        self.toolbar = None

    def init_main_window(self):
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Logo
        logo = QLabel(pixmap=QPixmap("images/Interface/AmperePro_logo.png"))
        logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(logo)

        # Modes
        mode_layout = QHBoxLayout()
        main_layout.addLayout(mode_layout)

        # Mode Niveaux
        mode_niveau_button = QPushButton()
        mode_niveau_button.setText("Mode Niveaux")
        mode_niveau_button.clicked.connect(lambda: self.change_mode(Mode.Niveau))
        mode_layout.addWidget(mode_niveau_button)

        # Mode Libre
        mode_libre_button = QPushButton()
        mode_libre_button.setText(" Mode Libre")
        mode_libre_button.clicked.connect(lambda: self.change_mode(Mode.Libre))
        mode_layout.addWidget(mode_libre_button)

        # Devrait ouvrir un nouveau window avec la documentation
        documentation_button = QPushButton()
        documentation_button.setText("Documentation")
        main_layout.addWidget(documentation_button)
        documentation_button.clicked.connect(self.ouvrir_documentation)

        a_propos_button = QPushButton()
        a_propos_button.setText("À Propos")
        main_layout.addWidget(a_propos_button)
        a_propos_button.clicked.connect(self.ouvrir_a_propos)

    def add_title(self) -> QLabel:
        title = QLabel("AmpèrePro")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setStyleSheet("color:yellow")

        police = QFont()
        police.setPointSize(32)
        title.setFont(police)
        return title

    def ouvrir_documentation(self):
        self.fenetre_doc = DocumentationWindow()

        # ouverture du Stylesheet
        style_docu = QFile("StyleSheet/StyleDocumentation.qss")
        if style_docu.open(QFile.OpenModeFlag.ReadOnly):
            stream_docu = QTextStream(style_docu)
            self.fenetre_doc.setStyleSheet(stream_docu.readAll())
            style_docu.close()

            self.fenetre_doc.show()

    def ouvrir_a_propos(self):
        # ouverture du stylesheet
        style_propos = QFile("StyleSheet/StylePropos.qss")
        if style_propos.open(QFile.OpenModeFlag.ReadOnly):
            stream = QTextStream(style_propos)
            self.fenetre_a_propos.setStyleSheet(stream.readAll())
            style_propos.close()

        self.fenetre_a_propos.show()

    def change_mode(self, new_mode: Mode):
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        main_layout.addWidget(self.add_title())

        match new_mode:
            case Mode.Libre:
                self.afficher_mode_libre(main_layout)
            case Mode.Niveau:
                self.afficher_mode_niveaux(main_layout)

        retour_arriere = QPushButton("Retour en Arrière")
        retour_arriere.clicked.connect(self.init_main_window)
        main_layout.addWidget(retour_arriere)

    def afficher_mode_libre(self, main_layout):
        circuit_libres = self.data.circuits_libre()
        for circuit in circuit_libres:
            circuit_button = QPushButton()
            circuit_button.setText(circuit.nom)
            circuit_button.clicked.connect(lambda: self.add_circuit(circuit))
            main_layout.addWidget(circuit_button)

        gif_electricite = QMovie("images/interface/mode_libre.gif")

        label = QLabel()
        label.setMovie(gif_electricite)
        label.setScaledContents(True)
        label.resize(200, 500)
        gif_electricite.start()

        main_layout.addWidget(label)

        # Nouvelle Section Mode libre
        add_circuit_button = QPushButton()
        add_circuit_button.setText("Créer un nouveau circuit")
        add_circuit_button.clicked.connect(lambda: self.add_circuit(None))
        main_layout.addWidget(add_circuit_button)

        mode_libre_layout = QHBoxLayout()
        main_layout.addLayout(mode_libre_layout)

        # Liste de circuit fait précédament loader en JSON
        circuit_list = QVBoxLayout()
        mode_libre_layout.addLayout(circuit_list)

        # preview_circuit = ...
        # mode_libre_layout.addLayout(preview_circuit)

    def afficher_mode_niveaux(self, main_layout):
        subtitle = QLabel("Bienvenue ! Choisis un sujet")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        for sujet in Sujet:
            bouton = QPushButton(sujet.value)
            bouton.clicked.connect(lambda _, s=sujet: self.afficher_niveaux_sujet(s))
            main_layout.addWidget(bouton)

    def afficher_niveaux_sujet(self, sujet: Sujet):
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        titre = QLabel("AmpèrePro")
        titre.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        titre.setStyleSheet("color:yellow")

        police = QFont()
        police.setPointSize(30)
        titre.setFont(police)

        main_layout.addWidget(titre)

        subtitle = QLabel("Sujet choisi : " + sujet.value)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        self.popups = []

        difficultes = ["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★"]
        progressions = [0, 0, 0, 0, 0]

        for i in range(5):
            if sujet == Sujet.Ohm and i == 0:
                popup = Popup(callback_commencer=self.ouvrir_niveau_ohm_1)
            elif sujet == Sujet.Ohm and i == 1:
                popup = Popup(callback_commencer=self.ouvrir_niveau_ohm_2)
            elif sujet ==Sujet.Ohm and i == 2:
                popup = Popup(callback_commencer=self.ouvrir_niveau_ohm_3)
            else:
                popup = Popup()

            self.popups.append(popup)

            ligne_widget = QWidget()
            ligne_layout = QHBoxLayout()
            ligne_widget.setLayout(ligne_layout)

            barre_progression = QProgressBar()
            barre_progression.setMinimum(0)
            barre_progression.setMaximum(100)
            barre_progression.setValue(progressions[i])
            barre_progression.setFormat(str(progressions[i]) + "%")
            barre_progression.setFixedWidth(140)

            bouton_niveau = OuvertureFenetre("Niveau " + str(i + 1), popup)

            label_difficulte = QLabel(difficultes[i])
            label_difficulte.setFixedWidth(80)
            label_difficulte.setAlignment(Qt.AlignmentFlag.AlignCenter)

            ligne_layout.addWidget(barre_progression)
            ligne_layout.addWidget(bouton_niveau)
            ligne_layout.addWidget(label_difficulte)

            main_layout.addWidget(ligne_widget)

        retour_arriere = QPushButton("Retour aux sujets")
        retour_arriere.clicked.connect(lambda: self.change_mode(Mode.Niveau))
        main_layout.addWidget(retour_arriere)

    def ouvrir_niveau_ohm_1(self):
        niveau = NiveauOhm1(self.retour_sujets)
        self.setCentralWidget(niveau)
        self.resize(1100, 850)

    def ouvrir_niveau_ohm_2(self):
        niveau = NiveauOhm2(self.retour_sujets)
        self.setCentralWidget(niveau)
        self.resize(1100, 850)

    def ouvrir_niveau_ohm_3(self):
        niveau = NiveauOhm3(self.retour_sujets)
        self.setCentralWidget(niveau)
        self.resize(1200, 900)

    def retour_sujets(self):
        self.change_mode(Mode.Niveau)

    def add_circuit(self, circuit: CircuitLibre | None):
        matrix = None

        # Si circuit est None, on créé un nouveau circuit
        if circuit is None:
            nom, ok = QInputDialog.getText(self, "Nouveau circuit", "Entre le nom de ton circuit")
            if nom and ok:
                id = self.data.creation_circuit_libre(nom)
            else:
                # Si l'utilisateur a dismiss(quitter) le dialog pour le nom du circuit, on annuler la création du circuit
                return
        else:
            matrix = circuit.matrix
            id = circuit.id

        self.nouveau_circuit = Circuit(self, id, matrix)
        self.nouveau_circuit.creer_toolbar()
        self.setCentralWidget(self.nouveau_circuit.graphics_view)
        self.setMenuBar(self.nouveau_circuit.barre_menu)
        self.menu_bar.removeAction(self.quitter_action)

        # complétion de la barre menu avec la possibilité de revenir au menu principal
        retour_action = QAction("Menu Principal", self)
        retour_action.setShortcut("Ctrl+M")
        retour_action.setIcon(QIcon("images/menubar/menu_principal.png"))
        retour_action.triggered.connect(self.retour_menu_triggered)
        self.nouveau_circuit.menu_naviguer.addAction(retour_action)

    # méthodes pour barre menu de circuit libre
    def retour_menu_triggered(self):
        avertissement = QDialog()
        avertissement.setWindowTitle("Voulez-vous Sauvegarder?")
        avertissement.setModal(True)

        layout_dialogue = QHBoxLayout()
        avertissement.setLayout(layout_dialogue)

        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(avertissement.close)

        bouton_sauvegarder_et_quitter = QPushButton("Sauvegarder et Menu")
        bouton_sauvegarder_et_quitter.clicked.connect(lambda: self.sauvegarder_et_menu(avertissement))

        bouton_quitter_sans_sauvegarder = QPushButton("Menu sans sauvegarder")
        bouton_quitter_sans_sauvegarder.clicked.connect(lambda: self.menu_sans_sauvegarder(avertissement))

        layout_dialogue.addWidget(bouton_sauvegarder_et_quitter)
        layout_dialogue.addWidget(bouton_quitter_sans_sauvegarder)
        layout_dialogue.addWidget(bouton_annuler)

        avertissement.exec()

    def retour_menu(self):
        self.nouveau_circuit.supprimer_toolbar()
        self.init_main_window()

    def sauvegarder_et_menu(self, dialog):
        # ferme QDialog, sauvegarde et retourne au menu principal
        dialog.close()
        self.nouveau_circuit.sauvegarder_triggered()
        self.retour_menu()
        self.menu_bar.clear()
        self.menu_bar.addMenu(self.menu_aide)
        self.menu_bar.addAction(self.quitter_action)
        self.toolbar.clear()

    def menu_sans_sauvegarder(self, dialog):
        dialog.close()
        self.retour_menu()
        self.menu_bar.clear()
        self.menu_bar.addMenu(self.menu_aide)
        self.menu_bar.addAction(self.quitter_action)
        self.toolbar.clear()

    def closeEvent(self, event):
        # change le "x" de la fenêtre du circuit libre
        if isinstance(self.centralWidget(), GraphicsView):
                resultat = self.nouveau_circuit.quitter_triggered()
                if resultat == "oui":
                    event.accept()
                else:
                    event.ignore()
                    self.nouveau_circuit.allouer_fermeture = "oui"
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication()
    window = AmperePro()
    window.show()
    app.exec()
