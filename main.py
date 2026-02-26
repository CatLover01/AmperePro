from PySide6.QtCore import QSize
from PySide6.QtGui import Qt, QIcon, QPixmap
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QGraphicsView, QToolBar, QGridLayout
from enum import Enum

from Circuit import Circuit
from Composantes import toolbar_composantes


class Mode(Enum):
    Libre = 1
    Niveau = 2


class AmperePro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AmpèrePro")
        self.setMinimumSize(500, 500)

        main_layout = QGridLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.title = QLabel("AmpèrePro")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle = QLabel("Choisis un mode pour continuer!")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.title, 0, 0, 2, 0)
        #main_layout.addWidget(self.subtitle, 0, 1)

        #Logo

        logo = QPixmap("./images/Menu/AmperePro_logo_resized.png")
        affichage_logo = QLabel()
        affichage_logo.setPixmap(logo)
        main_layout.addWidget(affichage_logo, 1, 1)

        # Modes
        mode_layout = QVBoxLayout()
        main_layout.addLayout(mode_layout, 1, 0, )

        # Mode Niveau
        mode_niveau = QPushButton()
        mode_niveau.setText("Mode Niveau")
        mode_niveau.clicked.connect(lambda: self.change_mode(Mode.Niveau))
        mode_layout.addWidget(mode_niveau)

        # Mode Libre
        mode_libre = QPushButton()
        mode_libre.setText(" Mode Libre")
        mode_libre.clicked.connect(lambda: self.change_mode(Mode.Libre))
        mode_layout.addWidget(mode_libre)

        # Charger circuit

        charger_circuit = QPushButton()
        charger_circuit.setText("Charger Circuit électrique")
        mode_layout.addWidget(charger_circuit)

        # Documentation
        documentation = QPushButton()
        documentation.setText("Documentation")
        mode_layout.addWidget(documentation)

        # à propos
        bouton_propos = QPushButton()
        bouton_propos.setText("à Propos")
        mode_layout.addWidget(bouton_propos)

        # Quitter
        bouton_quitter = QPushButton()
        bouton_quitter.setText("Quitter")
        bouton_quitter.clicked.connect(lambda: self.close())
        mode_layout.addWidget(bouton_quitter)

        self.graphic_view = QGraphicsView()

    def change_mode(self, new_mode: Mode):
        match new_mode:
            case Mode.Libre:
                main_layout = QVBoxLayout()
                main_widget = QWidget()
                main_widget.setLayout(main_layout)
                self.setCentralWidget(main_widget)
                self.subtitle.setText("Crée un nouveau circuit!")
                main_layout.addWidget(self.title)
                main_layout.addWidget(self.subtitle)

                # Nouvelle Section Mode libre
                add_circuit_button = QPushButton()
                add_circuit_button.setText("Add circuit")
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
                pass  # TODO

    def add_circuit(self):
        new_circuit = Circuit()
        self.graphic_view.setScene(new_circuit.scene)
        self.setCentralWidget(self.graphic_view)

        toolbar = QToolBar()

        # Ajoute le bouton main à la toolbar
        main_icone = QIcon("images/toolbar/main.png")
        main_bouton = QPushButton()
        main_bouton.setIcon(main_icone)
        main_bouton.setIconSize(QSize(45, 45))
        main_bouton.clicked.connect(new_circuit.main_click)
        toolbar.addWidget(main_bouton)

        # Ajoute le bouton fil à la toolbar
        fil_icone = QIcon("images/toolbar/fil.webp")
        fil_bouton = QPushButton()
        fil_bouton.setIcon(fil_icone)
        fil_bouton.setIconSize(QSize(45, 45))
        fil_bouton.clicked.connect(new_circuit.fil_click)
        toolbar.addWidget(fil_bouton)

        # Ajouter un bouton dans la toolbar pour chaque composante
        for dispositif in toolbar_composantes.values():
            bouton = QPushButton()
            bouton.setIcon(QIcon(dispositif.image_toolbar))
            bouton.setIconSize(QSize(45, 45))

            bouton.clicked.connect(lambda _, x=dispositif: new_circuit.toolbar_clicked(x))

            toolbar.addWidget(bouton)

        self.addToolBar(toolbar)


if __name__ == "__main__":
    app = QApplication()
    window = AmperePro()
    window.show()
    app.exec()
