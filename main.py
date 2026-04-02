from PySide6.QtCore import QSize, QFile, QTextStream
from PySide6.QtGui import Qt, QIcon, QPixmap, QFont, QAction, QMovie
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QGraphicsView, QToolBar, QMenu, QGroupBox, QScrollArea, QProgressBar, QDialog
from enum import Enum

from popup import OuvertureFenetre, Popup
from Composantes import toolbar_composantes
from a_propos import AProposWindow
from docs import DocumentationWindow
from sauvegarder import Sauvegarder
from circuit_libre import Window


class Mode(Enum):
    Libre = 1
    Niveau = 2


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
        self.init_main_window()

        self.data = Sauvegarder()

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

    def init_main_window(self):
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Titre de notre projet, utilisé dans les sous-interfaces
        self.title = QLabel("AmpèrePro")
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.title.setStyleSheet("color:yellow")

        police = QFont()
        police.setPointSize(32)
        self.title.setFont(police)

        # Logo
        logo = QLabel(pixmap=QPixmap("images/Interface/AmperePro_logo.png"))
        logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(logo)
        main_layout.addWidget(self.title)

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
        self.fenetre_a_propos = AProposWindow()

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
        main_layout.addWidget(self.title)

        match new_mode:
            case Mode.Libre:
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
                add_circuit_button.clicked.connect(self.add_circuit)
                main_layout.addWidget(add_circuit_button)

                add_circuit_charger = QPushButton("Charger un circuit sauvegardé")
                add_circuit_charger.clicked.connect(self.charger_circuit)
                main_layout.addWidget(add_circuit_charger)

                retour_menu = QPushButton("Retour au menu")
                retour_menu.clicked.connect(self.init_main_window)
                main_layout.addWidget(retour_menu)

                mode_libre_layout = QHBoxLayout()
                main_layout.addLayout(mode_libre_layout)

                # Liste de circuit fait précédament loader en JSON
                circuit_list = QVBoxLayout()
                mode_libre_layout.addLayout(circuit_list)

                # preview_circuit = ...
                # mode_libre_layout.addLayout(preview_circuit)

            case Mode.Niveau:
                self.afficher_sujets_niveau()
            case Niveau:
                self.afficher_niveau_O1()
                return

    def afficher_sujets_niveau(self):
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        titre = QLabel("AmpèrePro")
        titre.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        titre.setStyleSheet("color:yellow")

        police = QFont()
        police.setPointSize(32)
        titre.setFont(police)

        main_layout.addWidget(titre)

        subtitle = QLabel("Bienvenue ! Choisis un sujet")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        sujets = [
            "Loi de Kirchoff",
            "Loi d'ohms",
            "Série/Parallèle"
        ]

        for sujet in sujets:
            bouton = QPushButton(sujet)

            if sujet == "Loi de Kirchoff":
                bouton.clicked.connect(self.ouvrir_kirchoff)

            elif sujet == "Loi d'ohms":
                bouton.clicked.connect(self.ouvrir_ohms)

            elif sujet == "Série/Parallèle":
                bouton.clicked.connect(self.ouvrir_serie_parallele)

            main_layout.addWidget(bouton)

        retour_arriere = QPushButton("Retour en Arrière")
        retour_arriere.clicked.connect(self.init_main_window)
        main_layout.addWidget(retour_arriere)

    def ouvrir_kirchoff(self):
        self.afficher_niveaux_sujet("Loi de Kirchoff")

    def ouvrir_ohms(self):
        self.afficher_niveaux_sujet("Loi d'ohms")

    def ouvrir_serie_parallele(self):
        self.afficher_niveaux_sujet("Série/Parallèle")

    def afficher_niveaux_sujet(self, sujet):
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

        subtitle = QLabel("Sujet choisi : " + sujet)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        self.popups = []

        difficultes = ["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★"]
        progressions = [0, 0, 0, 0, 0]

        for i in range(5):
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
        retour_arriere.clicked.connect(self.retour_sujets)
        main_layout.addWidget(retour_arriere)

    def retour_sujets(self):
        self.afficher_sujets_niveau()

    def add_circuit(self):
        nouveau_circuit = Window(self)
        self.setCentralWidget(nouveau_circuit.graphics_view)
        self.setMenuBar(nouveau_circuit.barre_menu)
        self.menu_bar.removeAction(self.quitter_action)

        # complétion de la barre menu avec la possibilité de revenir au menu principal
        retour_action = QAction("Menu Principal", self)
        retour_action.setShortcut("Ctrl+M")
        retour_action.setIcon(QIcon("images/menubar/menu_principal.png"))
        retour_action.triggered.connect(self.retour_menu_triggered)
        nouveau_circuit.menu_naviguer.addAction(retour_action)

        toolbar = QToolBar()
        # ne permet pas à l'utilisateur de cacher la toolbar.
        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        """class ToolbarButton(QPushButton):
            def __init__(self, nom: str):
                super().__init__()
                self.nom = nom

            def enterEvent(self, event):
                self.setToolTip(self.nom)

        # Ajoute le bouton main à la toolbar
        main_icone = QIcon("images/toolbar/main.png")
        main_bouton = ToolbarButton("Main")
        main_bouton.setIcon(main_icone)
        main_bouton.setIconSize(QSize(45, 45))
        main_bouton.clicked.connect(nouveau_circuit.main_click)
        toolbar.addWidget(main_bouton)

        # Ajoute le bouton fil à la toolbar
        fil_icone = QIcon("images/toolbar/fil.webp")
        fil_bouton = ToolbarButton("Fil")
        fil_bouton.setIcon(fil_icone)
        fil_bouton.setIconSize(QSize(45, 45))
        fil_bouton.clicked.connect(nouveau_circuit.fil_click)
        toolbar.addWidget(fil_bouton)

        # Ajouter un bouton dans la toolbar pour chaque composante
        for composante in toolbar_composantes.values():
            bouton = ToolbarButton(composante.nom)
            bouton.setIcon(QIcon(composante.image_toolbar))
            bouton.setIconSize(QSize(45, 45))

            bouton.clicked.connect(lambda _, c=composante: new_circuit.toolbar_clicked(c))
            toolbar.addWidget(bouton)

        self.addToolBar(toolbar)"""

    # méthodes pour barre menu de circuit libre
    def retour_menu_triggered(self):
        avertissement = QDialog()
        avertissement.setWindowTitle("Voulez-vous Sauvegarder?")
        avertissement.setModal(True)

        layout_dialogue = QHBoxLayout()
        avertissement.setLayout(layout_dialogue)

        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(avertissement.close)

        bouton_sauvegarder_et_quitter = QPushButton("Sauvegarder et Quitter")
        bouton_sauvegarder_et_quitter.clicked.connect(lambda: self.sauvegarder_et_menu(avertissement))

        bouton_quitter_sans_sauvegarder = QPushButton("quitter sans sauvegarder")
        bouton_quitter_sans_sauvegarder.clicked.connect(lambda: self.menu_sans_sauvegarder(avertissement))

        layout_dialogue.addWidget(bouton_sauvegarder_et_quitter)
        layout_dialogue.addWidget(bouton_quitter_sans_sauvegarder)
        layout_dialogue.addWidget(bouton_annuler)

        avertissement.exec()

    def retour_menu(self):
        self.init_main_window()

    def sauvegarder_et_menu(self, dialog):
        nouveau_circuit = Window(self)
        #ferme QDialog, sauvegarde et retourne au menu principal
        dialog.close()
        nouveau_circuit.sauvegarder_triggered()
        self.retour_menu()
        self.menu_bar.clear()
        self.menu_bar.addMenu(self.menu_aide)
        self.menu_bar.addAction(self.quitter_action)

    def menu_sans_sauvegarder(self, dialog):
        nouveau_circuit = Window(self)
        dialog.close()
        self.retour_menu()
        self.menu_bar.clear()
        self.menu_bar.addMenu(self.menu_aide)
        self.menu_bar.addAction(self.quitter_action)

    def charger_circuit(self):
        pass


if __name__ == "__main__":
    app = QApplication()
    window = AmperePro()
    window.show()
    app.exec()
