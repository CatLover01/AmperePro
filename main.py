from PySide6.QtCore import QSize
from PySide6.QtGui import Qt, QIcon
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QGraphicsView, QToolBar
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
        self.setFixedSize(500, 500)

        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.title = QLabel("AmpèrePro")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle = QLabel("Choisie un mode pour continuer!")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title)
        main_layout.addWidget(self.subtitle)

        # Modes
        mode_layout = QHBoxLayout()
        main_layout.addLayout(mode_layout)

        # Mode Niveau
        mode_niveau = QPushButton()
        mode_niveau.setText("Niveau")
        mode_niveau.clicked.connect(lambda: self.change_mode(Mode.Niveau))
        mode_layout.addWidget(mode_niveau)

        # Mode Libre
        mode_libre = QPushButton()
        mode_libre.setText("Libre")
        mode_libre.clicked.connect(lambda: self.change_mode(Mode.Libre))
        mode_layout.addWidget(mode_libre)

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
