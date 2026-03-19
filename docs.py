from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QLabel, QPushButton
)
from PySide6.QtCore import Qt

# Voir les descriptions des composantes pour le reste de la documentation
Texte = {
    "Série / Parallèle" :(
        "Série / Parallèle \n\n"
        "Série : \n"
        "- Le courant est le même partout. \n"
        "- Les résistances s'additionnent : R_eq = R1 + R2 + R3 +... \n\n"
        "Parallèle : \n"
        "- La tension est la même sur chaqu branche. \n"
        "- 1/R_eq = 1/R1 + 1/R2 + 1/R3 \n"
    )
}