class Noeud:
    def __init__(self, pos):
        self.voltage = 0
        self.info_voisins = []
        self.pos = pos

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, voltage):
        self._voltage = voltage

    @property
    def voisins(self):
        return self._info_voisins

    @voisins.setter
    def voisins(self, voisins):
        self._info_voisins = voisins

    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, position):
        self._pos = position

    # Rajoute un fil lié et l'autre noeud qui touche au fil
    def ajouter_info(self, fil, noeud_voisin):
        nouveau_voisin = [fil, noeud_voisin]
        if nouveau_voisin not in self.info_voisins:
            self.info_voisins.append(nouveau_voisin)

    # Enlève les informations relatives à un fil
    def enlever_info_fil(self, fil):
        for k in range(len(self.info_voisins)):
            if self.info_voisins[k][0] == fil:
                del self.info_voisins[k]
                break

    # Retire le noeud et merge les fils qui étaient séparés par ce noeud
    def enlever_noeud(self, scene):
        # le premier fil doit finir par self sinon switch
        # le dernier fil doit commencer par self sinon switch

        # TODO Ça marche pas TABARNAK
        if len(self.info_voisins) == 1:
            i, j = scene.pos_to_mat(self.pos.x(), self.pos.y())
            scene.mat_points[i, j] = self.info_voisins[0][0]
            scene.noeuds.remove(self)
            scene.visualiser_matrice()

        else:
            fil_depart = self.info_voisins[0][0]
            if fil_depart.noeuds[0] == self:
                fil_depart.lignes.reverse()
                fil_depart.noeuds.reverse()
                fil_depart.composantes.reverse()
                fil_depart.points.reverse()

            fil_fin = self.info_voisins[1][0]
            if fil_fin.noeuds[1] == self:
                fil_fin.lignes.reverse()
                fil_fin.noeuds.reverse()
                fil_fin.composantes.reverse()
                fil_fin.points.reverse()

            # fil_depart va devenir le merge des deux fils
            fil_depart.lignes += fil_fin.lignes
            fil_depart.noeuds[1] = fil_fin.noeuds[1]
            fil_depart.composantes += fil_fin.composantes

            fil_fin.points.append(self.pos)
            fil_depart.points += fil_fin.points

            fil_depart.noeuds[0].enlever_info_fil(fil_depart)
            fil_depart.noeuds[0].ajouter_info(fil_depart, fil_depart.noeuds[1])
            fil_depart.noeuds[1].enlever_info_fil(fil_fin)
            fil_depart.noeuds[1].ajouter_info(fil_depart, fil_depart.noeuds[0])

            scene.fils.remove(fil_fin)

            for point in fil_fin.points:
                i, j = scene.pos_to_mat(point.x(), point.y())
                scene.mat_points[i, j] = fil_depart

            scene.noeuds.remove(self)

            scene.visualiser_matrice()


