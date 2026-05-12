from __future__ import annotations
from typing import TYPE_CHECKING

# Évite circular dependency pour avoir le type Circuit
if TYPE_CHECKING:
    from circuit.circuit import Circuit

from PySide6.QtCore import QLineF, QPointF
from PySide6.QtWidgets import QGraphicsLineItem

from circuit.noeud import Noeud
from composantes import Composante


class Fil:
    def __init__(self, circuit: Circuit, points: list[QPointF], lignes: list[QGraphicsLineItem]):
        self._circuit = circuit
        self.points = points
        self.noeuds = None
        self.lignes = lignes

        # self.resistance, self.tension = self.calculs()
        self.composantes: list[Composante] = []

        self.tension = 0
        self.resistance = 0


    # Calcul la tension et la résistance relative dans le fil
    def calculs(self):
        res = 0
        tension = 0
        for composante in self.composantes:
            if hasattr(composante, 'resistance'):
                res += composante.resistance
            if hasattr(composante, 'tension'):
                tension += composante.tension
        return res, tension

    def ajouter_composante(self, composante: Composante):
        def index_comp(index_point: int):
            for i in range(len(self.composantes)):
                pos_comp = self.composantes[i].points_fil[1]
                index_comp_points = self.points.index(pos_comp)

                if index_point <= index_comp_points:
                    return i
            return 0

        if composante.nom == "Batterie":
            index_point_depart = self.points.index(composante.points_fil[0])
            index_point_fin = self.points.index(composante.points_fil[-1])

            sens_comp = 1
            if index_point_depart > index_point_fin:
                sens_comp = -1

            self.composantes.insert(index_comp(index_point_depart), composante)

            self.resistance += composante.resistance
            self.tension += sens_comp * composante.tension
        else:
            index_milieu = self.points.index(composante.points_fil[1])

            self.composantes.insert(index_comp(index_milieu), composante)

            self.resistance += composante.resistance

    # Ajoute un noeud au fil, ce qui sépare le fil en deux fils distincts
    def ajouter_noeud(self, pos: QPointF, noeud: Noeud):
        index_point = self.points.index(pos)
        points_avant = self.points[:index_point]
        points_apres = self.points[index_point + 1:]

        lignes_avant = []
        lignes_apres = []

        for i in range(len(self.lignes)):
            ligne = self.lignes[i]
            p1 = ligne.line().p1()
            p2 = ligne.line().p2()
            x_max, x_min = max(p1.x(), p2.x()), min(p1.x(), p2.x())
            y_max, y_min = max(p1.y(), p2.y()), min(p1.y(), p2.y())
            if x_max >= pos.x() >= x_min and y_max >= pos.y() >= y_min:
                ligne.setLine(QLineF(p1, pos))

                nouvelle_ligne = self._circuit.ajouter_ligne(pos.x(), pos.y(), p2.x(), p2.y())
                self.lignes.insert(i + 1, nouvelle_ligne)

                lignes_avant = self.lignes[:i + 1]
                lignes_apres = self.lignes[i + 1:]
                break

        # Quand y'a pas de noeud, le fil ne se split pas, mais le début commence maintenant au noeud
        if self.noeuds is None:
            self.points = points_apres.copy() + points_avant.copy()
            self._lignes = lignes_apres.copy() + lignes_avant.copy()
            self.noeuds = [noeud, noeud]
        else:
            comp_avant = []
            comp_apres = []
            for i in range(len(self.composantes)):
                pos_comp = self.composantes[i].points_fil[1]
                index_comp_points = self.points.index(pos_comp)

                if index_point < index_comp_points:
                    comp_avant = self.composantes[:i]
                    comp_apres = self.composantes[i:]
                    break

            nouveau_fil = Fil(self._circuit, points_apres, lignes_apres.copy())
            nouveau_fil.noeuds = [noeud, self.noeuds[1]]
            nouveau_fil.composantes = comp_apres.copy()
            self._circuit.fils.append(nouveau_fil)

            for point_apres in points_apres:
                i, j = self._circuit.pos_to_mat(point_apres.x(), point_apres.y())
                self._circuit.mat_points[i, j] = nouveau_fil

            self.noeuds[0].enlever_info_fil(self)
            self.noeuds[0].ajouter_info(self, noeud)

            if self.noeuds[0] != self.noeuds[1]:
                self.noeuds[1].enlever_info_fil(self)
            self.noeuds[1].ajouter_info(nouveau_fil, noeud)

            noeud.ajouter_info(self, self.noeuds[0])
            noeud.ajouter_info(nouveau_fil, self.noeuds[0])

            self.composantes = comp_avant.copy()
            self.noeuds = [self.noeuds[0], noeud]
            self.points = points_avant.copy()
            self.lignes = lignes_avant.copy()

    # TODO faire en sorte que les noeuds soient pas retirés si ils sont connectés à plus de deux fils
    def enlever_fil(self):
        for point in self.points:
            i, j = self._circuit.pos_to_mat(point.x(), point.y())
            self._circuit.mat_points[i, j] = None

        self._circuit.rapetisser_matrice()
        self._circuit.visualiser_matrice()

        self.noeuds[0].enlever_info_fil(self)
        if len(self.noeuds[0]._info_voisins) <= 2:
            self.noeuds[0].enlever_noeud(self._circuit)

        self.noeuds[1].enlever_info_fil(self)
        if len(self.noeuds[1]._info_voisins) <= 2:
            self.noeuds[1].enlever_noeud(self._circuit)

        for composante in self.composantes:
            self._circuit.removeItem(composante.image_item)
            self._circuit.retirer_elements(composante)
        for ligne in self._lignes:
            self._circuit.removeItem(ligne)
