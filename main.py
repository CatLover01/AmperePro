from PySide6.QtCore import QSize, QFile, QTextStream
from PySide6.QtGui import Qt, QIcon, QPixmap, QFont, QAction
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QGraphicsView, QToolBar, QMenu, QGroupBox, QScrollArea
from enum import Enum

from Circuit import Circuit
from Composantes import toolbar_composantes
from a_propos import AProposWindow
from docs import DocumentationWindow


class Mode(Enum):
    Libre = 1
    Niveau = 2


class AmperePro(QMainWindow):
    def __init__(self):
        super().__init__()

        style_main = QFile("StyleMainWindow.qss")
        if style_main.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_main)
            self.setStyleSheet(stream.readAll())
            style_main.close()

        self.setWindowTitle("AmpèrePro")
        self.setMinimumSize(500, 500)

        self.title = None
        self.fenetre_doc = None
        self.init_main_window()

        # Menus
        menu_bar = self.menuBar()
        menu_aide = QMenu("Aide")

        # Documentation
        documentation_action = QAction("Documentation", self)
        documentation_action.triggered.connect(self.ouvrir_documentation)
        menu_aide.addAction(documentation_action)

        # À propos
        a_propos_action = QAction("À Propos", self)
        # aide_action.triggered.connect() ouvrir a propos
        menu_aide.addAction(a_propos_action)

        menu_bar.addMenu(menu_aide)

        # Quitter
        quitter_action = QAction("Quitter", self)
        quitter_action.triggered.connect(self.close)
        menu_bar.addAction(quitter_action)

        self.graphic_view = QGraphicsView()

    def init_main_window(self):
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Titre de notre projet, utiliser dans les sous interfaces
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

        # Modes
        mode_layout = QHBoxLayout()
        main_layout.addLayout(mode_layout)

        # Mode Niveau
        mode_niveau_button = QPushButton()
        mode_niveau_button.setText("Mode Niveau")
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

    def ouvrir_documentation(self):
        self.fenetre_doc = DocumentationWindow()
        style_docu = QFile("StyleDocumentation.qss")
        if style_docu.open(QFile.ReadOnly | QFile.Text):
            stream_docu = QTextStream(style_docu)
            self.fenetre_doc.setStyleSheet(stream_docu.readAll())
            style_docu.close()

        self.fenetre_doc.show()

    def change_mode(self, new_mode: Mode):
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        main_layout.addWidget(self.title)

        match new_mode:
            case Mode.Libre:
                subtitle = QLabel("Crée un nouveau circuit!")
                subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
                main_layout.addWidget(subtitle)

                # Nouvelle Section Mode libre
                add_circuit_button = QPushButton()
                add_circuit_button.setText("Créer")
                add_circuit_button.clicked.connect(self.add_circuit)
                main_layout.addWidget(add_circuit_button)

                mode_libre_layout = QHBoxLayout()
                main_layout.addLayout(mode_libre_layout)

                # Liste de circuit fait précédament loader en JSON
                circuit_list = QVBoxLayout()
                mode_libre_layout.addLayout(circuit_list)

                # preview_circuit = ...
                # mode_libre_layout.addLayout(preview_circuit)

            case Mode.Niveau:
                # Liste de config json pour tout les niveaux
                # devrait probablement être dans niveau/1.json et niveau/2.json ...
                niveau = [".", ".", ".", ".", ".", ".", "."]

                scroll_area = QScrollArea()
                main_layout.addWidget(scroll_area)

                widget = QWidget()
                niveau_layout = QVBoxLayout(widget)

                for index, file_path in enumerate(niveau):
                    group_box = QGroupBox(f"Niveau {index + 1}")
                    group_box_layout = QHBoxLayout()
                    group_box.setLayout(group_box_layout)

                    # bouton débuter et la group box devrait être disabled si le niveau de l'utilisateur est initial
                    # Doit sauvegarder en json pour savoir ou l'utilisateur est rendu et guarder le progret
                    button = QPushButton("Débuter")
                    group_box_layout.addWidget(button)

                    # Ici on pourrait généré un preview selon le json
                    #preview_image = QPixmap()
                    #label = QLabel(pixmap=preview_image)
                    #group_box_layout.addWidget(label)

                    niveau_layout.addWidget(group_box)

                scroll_area.setWidget(widget)

        # Bouton pour retourner au menu initial
        retour_arriere = QPushButton("Retour en Arrière")
        retour_arriere.clicked.connect(self.init_main_window)
        main_layout.addWidget(retour_arriere)


    def add_circuit(self):
        new_circuit = Circuit()
        self.graphic_view.setScene(new_circuit.scene)
        self.setCentralWidget(self.graphic_view)

        toolbar = QToolBar()
        # ne permet pas à l'utilisateur de cacher la toolbar.
        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        class ToolbarButton(QPushButton):
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
        main_bouton.clicked.connect(new_circuit.main_click)
        toolbar.addWidget(main_bouton)

        # Ajoute le bouton fil à la toolbar
        fil_icone = QIcon("images/toolbar/fil.webp")
        fil_bouton = ToolbarButton("Fil")
        fil_bouton.setIcon(fil_icone)
        fil_bouton.setIconSize(QSize(45, 45))
        fil_bouton.clicked.connect(new_circuit.fil_click)
        toolbar.addWidget(fil_bouton)

        # Ajouter un bouton dans la toolbar pour chaque composante
        for composante in toolbar_composantes.values():
            bouton = ToolbarButton(composante.nom)
            bouton.setIcon(QIcon(composante.image_toolbar))
            bouton.setIconSize(QSize(45, 45))

            bouton.clicked.connect(lambda _, c=composante: new_circuit.toolbar_clicked(c))
            toolbar.addWidget(bouton)

        self.addToolBar(toolbar)


if __name__ == "__main__":
    app = QApplication()
    window = AmperePro()
    window.show()
    app.exec()
