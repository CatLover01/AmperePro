from enum import Enum


class Sujet(Enum):
    Ohm = "Loi d'ohm"
    Resistance = "Résistance équivalente"
    Kirchoff = "Loi de Kirchoff"


class DetailNiveau(Enum):
    Description = 1,
    PointTotal = 2


INFO_NIVEAUX = {
    Sujet.Ohm: {
        1: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 12,
        },
        2: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 5,
        },
        3: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 5,
        },
        4: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 6,
        },
        5: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 5,
        },
    },
    Sujet.Kirchoff: {
        1: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 10,
        },
        2: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 5,
        },
        3: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 4,
        },
        4: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: None,
        },
        5: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 3,
        },
    },
    Sujet.Resistance: {
        1: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 6,
        },
        2: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 5,
        },
        3: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 2,
        },
        4: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: 2,
        },
        5: {
            DetailNiveau.Description: "...",
            DetailNiveau.PointTotal: None,
        },
    }
}
