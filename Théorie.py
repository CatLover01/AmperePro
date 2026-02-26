from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QLabel, QPushButton
)
from PySide6.QtCore import Qt

Texte = {
    "Voltmètre " : (
        "Le Voltmètre \n\n "
        "- Sert à mesurer la tension (différence de potentiel) entre deux points. \n "
        "- Unité : Volt (V). \n "
        "- Se branche en parallèle aux bornes de la composante dont on veut mesurer la tension. \n"
        "- Idéalement, la résistance dans le voltmètre est très grande pour ne pas déranger le circuit."
    ),

    "Ampèremètre": (
        "Ampèremètre \n\n"
        "- Sert à mesurer le courant électrique qui traverse une branche. \n"
        "- Unité : Ampères (A). \n "
        "- Se branche en série dans la branche où on veut mesurer le courant \n"
        "- Idéalement, la résistance dans l'ampèremètre est très faible."

    ),
    "Résistance": (
        "Résistance \n\n"
        "- Composante qui limite le courant. \n"
        "- Unité : Ohms (Ω) \n"
        "- Loi d'Ohm : V = R · I \n"
        "- Baisse l'intensité du courant. \n"
        "- V en Volts, R en Ohms, I en Ampères"
    ),
    "DEL": (
        "DEL \n\n"
        "- Diode qui émet de la lumière quand le courant passe dans le bon sens"
        "- Elle a une polarité : anode (+) et cathode (-). \n"
        "- On met souvent une résistance en série une LED pour évitr trop de courant"
    ),
    "Diode": (
        "Diode \n\n"
        "- Laisse passer le courant dans un seul sens ( en résumé ). \n"
        "- Polarité importante. \n"
        "- Utile pour boquer le retour de courant ou redresser un signal "
    ),
    "Intrrupteur": (
        "Intrrupteur \n\n"
        "- Sert à ouvrir ou fermer un circuit. \n"
        "- Ouvert : le courant ne passe pas. \n"
        "- Fermé : le courant peut passer ( si le circuit est complet )."
    ),
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