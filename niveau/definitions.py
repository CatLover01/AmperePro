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
            DetailNiveau.Description: "Bases de la loi d'Ohm et des grandeurs U, R, I",
            DetailNiveau.PointTotal: 12,
        },
        2: {
            DetailNiveau.Description: "Calcule U, R ou I dans des exercices simples",
            DetailNiveau.PointTotal: 5,
        },
        3: {
            DetailNiveau.Description: "Trouve les valeurs manquantes à partir de schémas",
            DetailNiveau.PointTotal: 5,
        },
        4: {
            DetailNiveau.Description: "Classe des circuits selon leur résistance",
            DetailNiveau.PointTotal: 6,
        },
        5: {
            DetailNiveau.Description: "Calcule la résistance équivalente de circuits",
            DetailNiveau.PointTotal: 5,
        },
    },
    Sujet.Kirchoff: {
        1: {
            DetailNiveau.Description: "Repère les noeuds dans des circuits",
            DetailNiveau.PointTotal: 10,
        },
        2: {
            DetailNiveau.Description: "Complète des équations de mailles et de courants",
            DetailNiveau.PointTotal: 5,
        },
        3: {
            DetailNiveau.Description: "Identifie les mailles et leurs équations",
            DetailNiveau.PointTotal: 4,
        },
        4: {
            DetailNiveau.Description: "Résolution pas à pas des courants d'un circuit",
            DetailNiveau.PointTotal: None,
        },
        5: {
            DetailNiveau.Description: "Détermine les courants I1, I2 et I3",
            DetailNiveau.PointTotal: 3,
        },
    },
    Sujet.Resistance: {
        1: {
            DetailNiveau.Description: "Identifie les circuits en série, parallèle ou mixtes",
            DetailNiveau.PointTotal: 6,
        },
        2: {
            DetailNiveau.Description: "Trouve une résistance inconnue à partir de Req",
            DetailNiveau.PointTotal: 5,
        },
        3: {
            DetailNiveau.Description: "Calcule la résistance équivalente de chaque circuit",
            DetailNiveau.PointTotal: 2,
        },
        4: {
            DetailNiveau.Description: "Déduction d'une valeur inconnue en ohms",
            DetailNiveau.PointTotal: 2,
        },
        5: {
            DetailNiveau.Description: "Calcule Req d'un circuit plus complexe",
            DetailNiveau.PointTotal: 1,
        },
    }
}
