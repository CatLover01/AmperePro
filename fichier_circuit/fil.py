from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtGui import QColorConstants

from sauvegarde import FilDTO

# Évite dépendance circulaire pour avoir le type Circuit
if TYPE_CHECKING:
    from fichier_circuit.circuit import Circuit

from PySide6.QtCore import QLineF, QPointF
from PySide6.QtWidgets import QGraphicsLineItem

from fichier_circuit.noeud import Noeud
from composantes import Composante, TypeComposante


class Fil:
    def __init__(self, circuit: Circuit, points: list[QPointF], lignes: list[QGraphicsLineItem], composantes=None,
                 tension: float = 0, resistance: float = 0):
        if composantes is None:
            composantes = []

        self._circuit = circuit
        self.points = points
        self.noeuds = None
        self.lignes = lignes

        self.composantes: list[Composante] = composantes
        self.tension = tension
        self.resistance = resistance
        self.amperage = 0

        # 0 si y'a pas de diode, 1 si y'a une diode dans le sens du fil, -1 si dans le sens inverse et ignorer
        # va être True s'il y a une diode dans chaque sens
        self.sens_diode = 0
        # Si diode dans chaque sens, voltmetre present
        self.ignorer = False



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
    def composantes(self):
        return self._composantes

    @composantes.setter
    def composantes(self, composante):
        self._composantes = composante

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

    @property
    def amperage(self):
        return self._amperage

    @amperage.setter
    def amperage(self, amperage):
        self._amperage = amperage

    @property
    def sens_diode(self):
        return self._sens_diode

    @sens_diode.setter
    def sens_diode(self, sens_diode):
        self._sens_diode = sens_diode

    @property
    def ignorer(self):
        return self._ignorer

    @ignorer.setter
    def ignorer(self, ignorer):
        self._ignorer = ignorer


    def to_dto(self, noeud_to_index: dict) -> FilDTO:
        points = [[p.x(), p.y()] for p in self.points]
        composantes = [composante.to_dto() for composante in self.composantes]
        if self.noeuds is None:
            noeuds = None
        else:
            noeuds = [noeud_to_index[n] for n in self.noeuds]

        return FilDTO(points, composantes, self.tension, self.resistance, noeuds)

    @classmethod
    def from_dto(cls, dto: FilDTO, circuit: Circuit) -> Fil:
        points = [QPointF(p[0], p[1]) for p in dto.points]
        composantes = [Composante.from_dto(composante) for composante in dto.composantes]
        # TODO: générer les lignes (QGraphicsLineItem) à partir des points
        lignes = []

        return cls(circuit, points, lignes, composantes, dto.tension, dto.resistance)

    def definir_amperage(self, nouveau_amperage):
        self.amperage = nouveau_amperage

        # Les lignes deviennent rouges s'il y a court circuit
        pen = self.lignes[0].pen()
        if abs(nouveau_amperage) > 100:
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

    # Calcul la tension et la résistance relative dans le fil
    def calculs(self):
        self.resistance = 0
        self.tension = 0
        self.sens_diode = 0
        self.ignorer = False
        for composante in self.composantes:
            # Enlever plus tard ils vont avoir un sens comme les autres composantes
            if not composante.type == TypeComposante.Amperemetre and not composante.type == TypeComposante.Voltmetre:

                index_point_depart = self.points.index(composante.points_fil[0])
                index_point_fin = self.points.index(composante.points_fil[-1])

                sens_comp = 1
                if index_point_depart > index_point_fin:
                    sens_comp = -1
            else:
                sens_comp = 1

            if composante.type == TypeComposante.Voltmetre:
                self.ignorer = True

            elif composante.type == TypeComposante.Diode:
                if self.sens_diode != 0 and self.sens_diode != sens_comp:
                    self.ignorer = True
                self.sens_diode = sens_comp

            elif composante.type == TypeComposante.Interrupteur and composante.ouvert:
                print(3)
                self.ignorer = True

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

    def retirer_composante(self, composante):
        if composante in self.composantes:
            self.composantes.remove(composante)


    # Ajoute un noeud au fil, ce qui sépare le fil en deux fils distincts
    def ajouter_noeud(self, pos: QPointF, noeud: Noeud):
        index_point = self.points.index(pos)
        points_avant = self.points[:index_point + 1]
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
            self.lignes = lignes_apres.copy() + lignes_avant.copy()

            comp_avant = []
            comp_apres = []
            for i in range(len(self.composantes)):
                pos_comp = self.composantes[i].points_fil[1]
                index_comp_points = self.points.index(pos_comp)

                if index_point < index_comp_points:
                    comp_avant = self.composantes[:i + 1]
                    comp_apres = self.composantes[i + 1:]
                    break

            if comp_avant == []:
                comp_apres = self.composantes.copy()

            self.composantes = comp_apres + comp_avant

            self.noeuds = [noeud, noeud]
            noeud.ajouter_info(self, noeud)
            noeud.ajouter_info(self, noeud)

        else:
            comp_avant = []
            comp_apres = []
            for composante in self.composantes:
                pos_comp = composante.points_fil[1]
                if pos_comp in points_avant:
                    comp_avant.append(composante)
                else:
                    comp_apres.append(composante)

            nouveau_fil = Fil(self._circuit, points_apres.copy(), lignes_apres.copy())
            nouveau_fil.noeuds = [noeud, self.noeuds[1]]
            nouveau_fil.composantes = comp_apres.copy()
            for comp in comp_apres:
                comp.fil = nouveau_fil
            self._circuit.fils.append(nouveau_fil)

            for point_apres in points_apres:
                i, j = self._circuit.pos_to_mat(point_apres.x(), point_apres.y())
                if (not isinstance(self._circuit.mat_points[i, j], Composante)
                        and not isinstance(self._circuit.mat_points[i, j], Noeud)):
                    self._circuit.mat_points[i, j] = nouveau_fil

            self.noeuds[0].info_voisins.remove([self, self.noeuds[1]])
            self.noeuds[0].ajouter_info(self, noeud)

            self.noeuds[1].info_voisins.remove([self, self.noeuds[0]])
            self.noeuds[1].ajouter_info(nouveau_fil, noeud)

            noeud.ajouter_info(self, self.noeuds[0])
            noeud.ajouter_info(nouveau_fil, self.noeuds[1])

            self.composantes = comp_avant.copy()
            self.noeuds = [self.noeuds[0], noeud]
            self.points = points_avant.copy()
            self.lignes = lignes_avant.copy()

            nouveau_fil.calculs()
            self.calculs()

    # TODO faire en sorte que les noeuds soient pas retirés si ils sont connectés à plus de deux fils
    def enlever_fil(self):
        for point in self.points:
            i, j = self._circuit.pos_to_mat(point.x(), point.y())
            self._circuit.mat_points[i, j] = None

        self._circuit.rapetisser_matrice()

        self.noeuds[0].enlever_info_fil(self)
        if len(self.noeuds[0].info_voisins) <= 2:
            self.noeuds[0].enlever_noeud(self._circuit)

        self.noeuds[1].enlever_info_fil(self)
        if len(self.noeuds[1].info_voisins) <= 2:
            self.noeuds[1].enlever_noeud(self._circuit)

        for composante in self.composantes:
            self._circuit.removeItem(composante.image_item)
            self._circuit.retirer_elements(composante)
        for ligne in self.lignes:
            self._circuit.removeItem(ligne)
