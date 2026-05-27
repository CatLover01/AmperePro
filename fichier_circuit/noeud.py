from __future__ import annotations
from typing import TYPE_CHECKING

from sauvegarde import NoeudDTO

# Évite dépendance circulaire pour avoir le type Circuit + Fil
if TYPE_CHECKING:
    from fichier_circuit.circuit import Circuit
    from fichier_circuit.fil import Fil

from PySide6.QtCore import QPointF, QLineF


class Noeud:
    def __init__(self, pos: QPointF, info_voisins=None, voltage: float = 0):
        if info_voisins is None:
            info_voisins = []
        self.voltage = voltage
        self._info_voisins: list[list[Fil | Noeud]] = info_voisins
        self._pos = pos

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos: QPointF):
        self._pos = pos

    @property
    def info_voisins(self):
        return self._info_voisins

    @info_voisins.setter
    def info_voisins(self, info_voisins: list[list[Fil | Noeud]]):
        self._info_voisins = info_voisins

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, voltage: float):
        self._voltage = voltage

    def to_dto(self, fil_to_index: dict, noeud_to_index: dict) -> NoeudDTO:
        return NoeudDTO(
            [self._pos.x(), self._pos.y()],
            self.voltage,
            [(fil_to_index[fil], noeud_to_index[voisin]) for fil, voisin in self.info_voisins]
        )

    @classmethod
    def from_dto(cls, dto: NoeudDTO) -> Noeud:
        return cls(QPointF(dto.pos[0], dto.pos[1]), dto.voisins, dto.voltage)

    # Rajoute un fil lié et l'autre noeud qui touche au fil
    def ajouter_info(self, fil: Fil, noeud_voisin: Noeud):
        nouveau_voisin = [fil, noeud_voisin]
        if nouveau_voisin not in self._info_voisins:
            self._info_voisins.append(nouveau_voisin)

    # Enlève les informations relatives à un fil
    def enlever_info_fil(self, fil: Fil):
        for info in self._info_voisins:
            if info[0] == fil:
                self._info_voisins.remove(info)
                break

    # Retire le noeud et merge les fils qui étaient séparés par ce noeud
    def enlever_noeud(self, circuit: Circuit):
        # le premier fil doit finir par self sinon switch
        # le dernier fil doit commencer par self sinon switch

        if len(self._info_voisins) == 2:
            fil_depart = self._info_voisins[0][0]

            if fil_depart.noeuds[0] == self:
                fil_depart.lignes.reverse()
                # On doit aussi reverse les points des lignes
                for ligne in fil_depart.lignes:
                    ligne.setLine(QLineF(ligne.line().p2(), ligne.line().p1()))

                fil_depart.noeuds.reverse()
                fil_depart.composantes.reverse()
                fil_depart.points.reverse()

            fil_fin = self._info_voisins[1][0]
            if fil_fin.noeuds[1] == self:
                fil_fin.lignes.reverse()
                # On doit aussi reverse les points des lignes
                for ligne in fil_fin.lignes:
                    ligne.setLine(QLineF(ligne.line().p2(), ligne.line().p1()))

                fil_fin.noeuds.reverse()
                fil_fin.composantes.reverse()
                fil_fin.points.reverse()

            # fil_depart va devenir le merge des deux fils
            fil_depart.lignes += fil_fin.lignes
            fil_depart.points += fil_fin.points
            fil_depart.composantes += fil_fin.composantes
            fil_depart.noeuds = [fil_depart.noeuds[0], fil_fin.noeuds[1]]

            fil_depart.noeuds[0].enlever_info_fil(fil_fin)
            fil_depart.noeuds[0].enlever_info_fil(fil_depart)
            fil_depart.noeuds[0].ajouter_info(fil_depart, fil_depart.noeuds[1])

            fil_depart.noeuds[1].enlever_info_fil(fil_fin)
            fil_depart.noeuds[1].enlever_info_fil(fil_depart)
            fil_depart.noeuds[1].ajouter_info(fil_depart, fil_depart.noeuds[0])

            for point in fil_fin.points:
                i, j = circuit.pos_to_mat(point.x(), point.y())
                touche = circuit.mat_points[i, j]
                if touche == fil_fin or touche == self:
                    circuit.mat_points[i, j] = fil_depart

            circuit.noeuds.remove(self)
            circuit.fils.remove(fil_fin)

            fil_depart.calculs()

        elif len(self._info_voisins) == 1:
            fil_restant = self._info_voisins[0][0]

            fil_restant.noeuds = None

            i, j = circuit.pos_to_mat(self._pos.x(), self._pos.y())
            circuit.mat_points[i, j] = self._info_voisins[0][0]
            self._info_voisins[0][0].points.append(self._pos)

            #print_matrice(circuit.mat_points, fil_restant.points, circuit)
