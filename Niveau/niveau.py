from enum import Enum


class Sujet(Enum):
    Ohm = "Loi d'ohm"
    Resistance = "Résistance équivalente"
    Kirchoff = "Loi de Kirchoff"


descriptions = {
    Sujet.Ohm: {
        1: "...",
        2: "...",
        3: "...",
        4: "...",
        5: "..."
    },
    Sujet.Kirchoff: {
        1: "...",
        2: "...",
        3: "...",
        4: "...",
        5: "..."
    },
    Sujet.Resistance: {
        1: "...",
        2: "...",
        3: "...",
        4: "...",
        5: "..."
    }
}
