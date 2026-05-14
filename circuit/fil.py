from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QColorConstants, QPen

from sauvegarde import FilDTO

# Évite dépendance circulaire pour avoir le type Circuit
if TYPE_CHECKING:
    from circuit.circuit import Circuit

from PySide6.QtCore import QLineF, QPointF
from PySide6.QtWidgets import QGraphicsLineItem

from circuit.noeud import Noeud
from composantes import Composante, TypeComposante


class Fil:
    def __init__(self, scene, points, lignes):
        self.scene = scene
        self.points = points
        self.noeuds = None
        self.lignes = lignes

        self.composantes = []
        self.tension = 0
        self.resistance = 0.0000000001
        self.amperage = 0

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    @property
    def noeuds(self):
        return self._noeuds

    @noeuds.setter
    def noeuds(self, noeuds):
        self._noeuds = noeuds

    @property
    def lignes(self):
        return self._lignes

    @lignes.setter
    def lignes(self, lignes):
        self._lignes = lignes

    @property
    def tension(self):
        return self._tension

    @tension.setter
    def tension(self, tension):
        self._tension = tension

    @property
    def resistance(self):
        return self._resistance

    @resistance.setter
    def resistance(self, resistance):
        self._resistance = resistance

    def definir_amperage(self, nouveau_amperage):
        self.amperage = nouveau_amperage


        # Les lignes deviennent rouges s'il y a court circuit
        pen = self.lignes[0].pen()
        # print(nouveau_amperage)
        if abs(nouveau_amperage) > 100:
            # print(self)
            pen.setColor(QColorConstants.Red)
            for ligne in self.lignes:
                ligne.setPen(pen)
        else:
            pen.setColor(QColorConstants.Black)
            for ligne in self.lignes:
                ligne.setPen(pen)


        for composante in self.composantes:
            # TODO Pouvoir changer le sens des voltmetres et amperemetres et que ca paraisse
            # enlever ensuite le abs
            if composante.type == TypeComposante.Amperemetre:
                composante.amperage = abs(nouveau_amperage)
                # print(nouveau_amperage)
            elif composante.type == TypeComposante.Voltmetre:
                voltage = self.resistance * nouveau_amperage
                composante.voltage = abs(voltage)

    # Calcul la tension et la résistance relative dans le fil
    def calculs(self):
        self.resistance = 0.0000000001
        self.tension = 0
        for composante in self.composantes:
            if not composante.type == TypeComposante.Amperemetre and not composante.type == TypeComposante.Voltmetre:
                index_point_depart = self.points.index(composante.points_fil[0])
                index_point_fin = self.points.index(composante.points_fil[-1])

                sens_comp = 1
                if index_point_depart > index_point_fin:
                    sens_comp = -1
            else:
                sens_comp = 1

            self.resistance += composante.resistance
            self.tension += composante.tension * sens_comp

    def ajouter_composante(self, composante):

        def index_comp(index_point):
            for i in range(len(self.composantes)):
                pos_comp = self.composantes[i].points_fil[1]
                index_comp_points = self.points.index(pos_comp)
                if index_point < index_comp_points:
                    return i

            return len(self.composantes)

        index_milieu = self.points.index(composante.points_fil[1])
        self.composantes.insert(index_comp(index_milieu), composante)
        self.calculs()

    # Ajoute un noeud au fil, ce qui sépare le fil en deux fils distincts
    def ajouter_noeud(self, pos: QPointF, noeud: Noeud):
        index_point = self.points.index(pos)
        points_avant = self.points[:index_point]
        points_apres = self.points[index_point + 1:]

        for i in range(len(self.lignes)):
            ligne = self.lignes[i]
            p1 = ligne.line().p1()
            p2 = ligne.line().p2()
            x_max, x_min = max(p1.x(), p2.x()), min(p1.x(), p2.x())
            y_max, y_min = max(p1.y(), p2.y()), min(p1.y(), p2.y())
            if x_max >= pos.x() >= x_min and y_max >= pos.y() >= y_min:
                ligne.setLine(QLineF(p1, pos))

                nouvelle_ligne = self.scene.ajouter_ligne(pos.x(), pos.y(), p2.x(), p2.y())
                self.lignes.insert(i + 1, nouvelle_ligne)

                lignes_avant = self.lignes[:i + 1]
                lignes_apres = self.lignes[i + 1:]
                break

        # Quand y'a pas de noeud, le fil ne se split pas, mais le début commence maintenant au noeud
        if self.noeuds is None:
            self.points = points_apres.copy() + points_avant.copy()
            self.lignes = lignes_apres.copy() + lignes_avant.copy()

            comp_avant = []
            comp_apres = []
            for i in range(len(self.composantes)):
                pos_comp = self.composantes[i].points_fil[1]
                index_comp_points = self.points.index(pos_comp)

                if index_point > index_comp_points:
                    comp_avant = self.composantes[:i]
                    comp_apres = self.composantes[i:]
                    break

            if comp_apres == []:
                comp_avant = self.composantes.copy()

            self.composantes = comp_apres + comp_avant

            self.noeuds = [noeud, noeud]

        else:
            comp_avant = []
            comp_apres = []
            for i in range(len(self.composantes)):
                pos_comp = self.composantes[i].points_fil[1]
                index_comp_points = self.points.index(pos_comp)

                if index_point > index_comp_points:
                    comp_avant = self.composantes[:i+1]
                    comp_apres = self.composantes[i+1:]
                    break

            if comp_apres == []:
                comp_avant = self.composantes.copy()

            nouveau_fil = Fil(self.scene, points_apres.copy(), lignes_apres.copy())
            nouveau_fil.noeuds = [self.noeuds[1], noeud]
            nouveau_fil.composantes = comp_apres.copy()
            for comp in comp_apres:
                comp.fil = nouveau_fil
            self.scene.fils.append(nouveau_fil)

            for point_apres in points_apres:
                i, j = self.scene.pos_to_mat(point_apres.x(), point_apres.y())
                if not isinstance(self.scene.mat_points[i, j], Composante):
                    self.scene.mat_points[i, j] = nouveau_fil


            self.noeuds[0].enlever_info_fil(self)
            self.noeuds[0].ajouter_info(self, noeud)

            if self.noeuds[0] != self.noeuds[1]:
                self.noeuds[1].enlever_info_fil(self)
            self.noeuds[1].ajouter_info(nouveau_fil, noeud)

            noeud.ajouter_info(self, self.noeuds[0])
            noeud.ajouter_info(nouveau_fil, self.noeuds[1])

            self.composantes = comp_avant.copy()
            self.noeuds = [self.noeuds[0], noeud]
            self.points = points_avant.copy()
            self.lignes = lignes_avant.copy()

    # TODO faire en sorte que les noeuds soient pas retirés si ils sont connectés à plus de deux fils
    def enlever_fil(self):
        for point in self.points:
            i, j = self.scene.pos_to_mat(point.x(), point.y())
            self.scene.mat_points[i, j] = None

        self.scene.rapetisser_matrice()

        self.noeuds[0].enlever_info_fil(self)
        if len(self.noeuds[0].info_voisins) <= 2:
            self.noeuds[0].enlever_noeud(self.scene)

        self.noeuds[1].enlever_info_fil(self)
        if len(self.noeuds[1].info_voisins) <= 2:
            self.noeuds[1].enlever_noeud(self.scene)

        for composante in self.composantes:
            self.scene.removeItem(composante)
        for ligne in self.lignes:
            self.scene.removeItem(ligne)
