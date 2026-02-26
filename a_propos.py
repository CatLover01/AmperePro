from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QApplication

class AProposWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("À propos :")
        self.setFixedSize(500, 500)

        widget = QWidget()
        layout = QVBoxLayout()

        titre = QLabel("À propos du projet :")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size: 40px; font-weight: bold;")
        layout.addWidget(titre)

        texte = QLabel(
            "Projet : AmeperePro \n\n"
            "Membres de l'équipe :\n\n"
            "- Olivier Allard \n"
            "- Rafael Costa \n"
            "- Hugo Fleury \n"
            "- Elliot Lalancette \n"
            "- Marc-Antoine Thibeault \n\n"
            "Cégep de Saint-Hyacinthe - 2026"
        )

        texte.setWordWrap(True)
        layout.addWidget(texte)

        bouton_fermer = QPushButton("Fermer")
        bouton_fermer.clicked.connect(self.close)
        layout.addWidget(bouton_fermer)

        widget.setLayout(layout)
        self.setCentralWidget(widget)
